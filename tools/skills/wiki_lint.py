#!/usr/bin/env python3
"""Lint and optionally fix JarvisOS wiki notes.

Checks:
  - Required YAML frontmatter keys present
  - Notes >100 lines have a non-empty Summary
  - sources[] values are non-empty
  - Filenames are lowercase and hyphenated
  - Duplicate notes (same URL in sources[])

Usage:
  python3 wiki_lint.py [--fix] [--model local] [--path wiki/]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"

REQUIRED_KEYS = {"title", "type", "status", "tags", "created", "updated",
                 "tokens_consumed", "sources", "Summary"}

# Notes in these folders get a lighter check (no Summary required under 50 lines)
LIGHT_FOLDERS = {"tasks", "logs"}


@dataclass
class LintIssue:
    path: Path
    code: str
    message: str
    fixable: bool = False


@dataclass
class LintResult:
    issues: list[LintIssue] = field(default_factory=list)
    checked: int = 0
    fixed: int = 0


def _parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Return {key: raw_value} and the line index after the closing ---."""
    if not text.startswith("---"):
        return {}, 0
    lines = text.splitlines()
    end = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}, 0
    fm: dict[str, str] = {}
    current_key = ""
    for line in lines[1:end]:
        if re.match(r"^\s+", line) and current_key:
            fm[current_key] = fm.get(current_key, "") + "\n" + line
        else:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)", line)
            if m:
                current_key = m.group(1)
                fm[current_key] = m.group(2).strip()
    return fm, end + 1


def lint_file(path: Path) -> list[LintIssue]:
    issues: list[LintIssue] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return issues

    lines = text.splitlines()
    line_count = len(lines)
    fm, body_start = _parse_frontmatter(text)

    folder = path.parent.name

    # Missing frontmatter entirely
    if not fm:
        issues.append(LintIssue(path, "NO_FRONTMATTER", "No YAML frontmatter found", fixable=False))
        return issues

    # Missing required keys
    light = folder in LIGHT_FOLDERS
    for key in REQUIRED_KEYS:
        if key not in fm:
            if key == "Summary" and light:
                continue
            issues.append(LintIssue(path, f"MISSING_{key.upper()}",
                                    f"Missing required key: {key}", fixable=(key == "Summary")))

    # Empty Summary on long notes
    summary = fm.get("Summary", "").strip().strip('"').strip("'")
    if line_count > 100 and not summary:
        issues.append(LintIssue(path, "EMPTY_SUMMARY",
                                f"Note has {line_count} lines but Summary is empty", fixable=True))

    # Filename convention (lowercase, hyphenated)
    name = path.stem
    expected = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if name != expected:
        issues.append(LintIssue(path, "BAD_FILENAME",
                                f"Filename '{name}' should be '{expected}'", fixable=False))

    # sources empty
    sources_val = fm.get("sources", "")
    if "sources" in fm and not sources_val.strip().replace("[]", "").replace("-", "").strip():
        issues.append(LintIssue(path, "EMPTY_SOURCES", "sources[] is empty", fixable=False))

    # tokens_consumed = 0 on non-trivial files
    if fm.get("tokens_consumed", "0").strip() == "0" and line_count > 20:
        issues.append(LintIssue(path, "ZERO_TOKENS",
                                "tokens_consumed is 0 on a non-trivial note", fixable=True))

    return issues


def fix_summary(path: Path, model: str) -> bool:
    """Auto-generate Summary using LLM and patch frontmatter."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from jarvis_llm import JarvisLLM  # type: ignore
    except ImportError:
        return False

    text = path.read_text(encoding="utf-8", errors="replace")
    body = text[text.find("---", 3) + 3:].strip()[:3000] if text.startswith("---") else text[:3000]

    llm = JarvisLLM(model)
    try:
        resp = llm.complete(
            f"Write a one-sentence summary (max 160 chars) of this note. "
            f"Respond with ONLY the summary text, no quotes, no prefix.\n\n{body[:2000]}",
            system="You are a concise summarizer.",
        )
        summary = resp.text.strip().strip('"').strip("'")[:200]
    except Exception:
        return False

    if not summary:
        return False

    # Patch Summary field if it exists, else add it before closing ---
    new_text = re.sub(
        r'^(Summary:\s*).*$',
        f'Summary: "{summary}"',
        text,
        flags=re.MULTILINE,
    )
    if new_text == text:
        # Summary key didn't exist — insert before closing ---
        new_text = re.sub(r'\n---\n', f'\nSummary: "{summary}"\n---\n', text, count=1)

    # Also fix tokens_consumed
    word_count = len(body.split())
    tokens = max(1, word_count * 4 // 3)
    new_text = re.sub(r'^(tokens_consumed:\s*).*$', f'tokens_consumed: {tokens}',
                      new_text, flags=re.MULTILINE)

    path.write_text(new_text, encoding="utf-8")
    return True


def lint_wiki(wiki_path: Path, fix: bool = False, model: str = "local") -> LintResult:
    result = LintResult()
    seen_sources: dict[str, Path] = {}

    md_files = sorted(wiki_path.rglob("*.md"))
    result.checked = len(md_files)

    all_issues: list[LintIssue] = []

    for path in md_files:
        issues = lint_file(path)

        # Check for duplicate sources
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            fm, _ = _parse_frontmatter(text)
            sources_block = fm.get("sources", "")
            urls = re.findall(r'https?://[^\s"\'>\]]+', sources_block)
            for url in urls:
                if url in seen_sources:
                    issues.append(LintIssue(path, "DUPLICATE_SOURCE",
                                            f"URL already in {seen_sources[url].name}: {url[:60]}",
                                            fixable=False))
                else:
                    seen_sources[url] = path
        except OSError:
            pass

        if fix:
            for issue in issues:
                if issue.fixable and issue.code in ("EMPTY_SUMMARY", "ZERO_TOKENS"):
                    if fix_summary(path, model):
                        result.fixed += 1
                        issue.message += " [FIXED]"

        all_issues.extend(issues)

    result.issues = all_issues
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fix", action="store_true",
                        help="Auto-fix missing Summary fields using LLM")
    parser.add_argument("--model", default="local",
                        help="LLM model for --fix (default: local/phi3:mini)")
    parser.add_argument("--path", type=Path, default=WIKI,
                        help="Wiki directory to lint (default: wiki/)")
    parser.add_argument("--code", default=None,
                        help="Filter by issue code (e.g. EMPTY_SUMMARY)")
    args = parser.parse_args()

    result = lint_wiki(args.path, fix=args.fix, model=args.model)

    issues = result.issues
    if args.code:
        issues = [i for i in issues if i.code == args.code.upper()]

    if not issues:
        print(f"✓ {result.checked} notes checked — no issues found.")
        if result.fixed:
            print(f"  {result.fixed} notes auto-fixed.")
        return

    # Group by file
    by_file: dict[Path, list[LintIssue]] = {}
    for issue in issues:
        by_file.setdefault(issue.path, []).append(issue)

    print(f"\n{'─'*60}")
    print(f"  Wiki Lint — {result.checked} notes checked")
    print(f"{'─'*60}\n")

    fixable_count = sum(1 for i in issues if i.fixable)

    for path, file_issues in sorted(by_file.items()):
        rel = path.relative_to(ROOT)
        print(f"  {rel}")
        for issue in file_issues:
            fix_marker = " [fixable]" if issue.fixable and not args.fix else ""
            fixed_marker = " ✓" if "[FIXED]" in issue.message else ""
            print(f"    [{issue.code}] {issue.message.replace(' [FIXED]', '')}{fix_marker}{fixed_marker}")
        print()

    print(f"{'─'*60}")
    print(f"  Total issues: {len(issues)}  ·  Fixable: {fixable_count}  ·  Fixed: {result.fixed}")
    if fixable_count > result.fixed and not args.fix:
        print(f"  Run with --fix to auto-generate {fixable_count} missing Summaries.")
    print()


if __name__ == "__main__":
    main()
