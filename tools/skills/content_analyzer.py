#!/usr/bin/env python3
"""Analyze URLs and files into structured JarvisOS wiki notes.

Extracts raw content per type, then uses LLM to produce a structured analysis.
Writes output to wiki/sources/ (and wiki/patterns/ for code-heavy content).

Usage:
  python3 content_analyzer.py <url_or_path> [options]

Options:
  --type    auto|youtube|instagram|github|pdf|article|local (default: auto)
  --model   local|local:llama3.1|sonnet|opus|gemini (default: $JARVIS_DEFAULT_MODEL or local)
  --out     sources|patterns|concepts (default: sources)
  --no-llm  extract raw content only, skip LLM analysis
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCES = ROOT / "wiki" / "sources"
WIKI_PATTERNS = ROOT / "wiki" / "patterns"
WIKI_CONCEPTS = ROOT / "wiki" / "concepts"
WIKI_TASKS = ROOT / "wiki" / "tasks"


# ── Type detection ─────────────────────────────────────────────────────────────

def detect_type(target: str) -> str:
    if Path(target).exists():
        suffix = Path(target).suffix.lower()
        if suffix == ".pdf":
            return "pdf"
        if suffix in (".txt", ".zip") or "whatsapp" in Path(target).name.lower():
            return "chat"
        return "local"
    if re.search(r"youtube\.com/watch|youtu\.be/", target):
        return "youtube"
    if re.search(r"youtube\.com/shorts/", target):
        return "youtube"
    if re.search(r"instagram\.com/(reel|p)/", target):
        return "instagram"
    if re.search(r"github\.com/[^/]+/[^/]+", target):
        return "github"
    if target.endswith(".pdf"):
        return "pdf"
    return "article"


# ── Extractors ─────────────────────────────────────────────────────────────────

@dataclass
class ExtractResult:
    text: str
    title: str
    metadata: dict
    content_type: str
    url: str


def extract_youtube(url: str) -> ExtractResult:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Get metadata + subtitles
        result = subprocess.run(
            ["yt-dlp", "--skip-download", "--write-auto-subs", "--sub-format", "vtt",
             "--sub-langs", "es,en", "--dump-json", "--no-playlist", url],
            capture_output=True, text=True, timeout=60, cwd=tmpdir,
        )
        meta: dict = {}
        if result.returncode == 0 and result.stdout.strip():
            try:
                meta = json.loads(result.stdout.strip().splitlines()[0])
            except Exception:
                pass

        title = meta.get("title", "") or url
        description = meta.get("description", "")[:500] or ""
        duration = meta.get("duration_string", "")
        uploader = meta.get("uploader", "")
        tags = meta.get("tags", [])[:10]

        # Try to get transcript from subtitle files
        transcript = ""
        for vtt_file in Path(tmpdir).glob("*.vtt"):
            raw = vtt_file.read_text(encoding="utf-8", errors="replace")
            # Strip VTT timestamps and dedup lines
            lines = []
            seen: set[str] = set()
            for line in raw.splitlines():
                line = line.strip()
                if not line or "-->" in line or line.startswith("WEBVTT") or re.match(r"^\d+$", line):
                    continue
                # Strip HTML tags
                clean = re.sub(r"<[^>]+>", "", line).strip()
                if clean and clean not in seen:
                    seen.add(clean)
                    lines.append(clean)
            transcript = " ".join(lines)[:8000]
            break

        text_parts = []
        if transcript:
            text_parts.append(f"## Transcript\n{transcript}")
        if description:
            text_parts.append(f"## Description\n{description}")

        return ExtractResult(
            text="\n\n".join(text_parts) or f"No transcript available. Title: {title}",
            title=title,
            metadata={"uploader": uploader, "duration": duration, "tags": tags, "url": url},
            content_type="youtube",
            url=url,
        )


def extract_instagram(url: str) -> ExtractResult:
    # Try yt-dlp for transcript (works for reels with auto-captions)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["yt-dlp", "--skip-download", "--write-auto-subs", "--sub-format", "vtt",
             "--sub-langs", "es,en", "--dump-json", "--no-playlist",
             "--cookies-from-browser", "chrome", url],
            capture_output=True, text=True, timeout=60, cwd=tmpdir,
        )
        meta: dict = {}
        if result.returncode == 0 and result.stdout.strip():
            try:
                meta = json.loads(result.stdout.strip().splitlines()[0])
            except Exception:
                pass

        title = meta.get("title", "") or meta.get("description", "")[:80] or url
        description = meta.get("description", "")[:1000] or ""

        transcript = ""
        for vtt_file in Path(tmpdir).glob("*.vtt"):
            raw = vtt_file.read_text(encoding="utf-8", errors="replace")
            lines = []
            seen: set[str] = set()
            for line in raw.splitlines():
                line = re.sub(r"<[^>]+>", "", line).strip()
                if line and "-->" not in line and line not in seen:
                    seen.add(line)
                    lines.append(line)
            transcript = " ".join(lines)[:4000]
            break

        text = transcript or description or "No transcript available."
        return ExtractResult(
            text=text,
            title=title[:120],
            metadata={"url": url},
            content_type="instagram",
            url=url,
        )


def extract_github(url: str) -> ExtractResult:
    # Parse owner/repo from URL
    m = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git|/|$)", url)
    if not m:
        raise ValueError(f"Cannot parse GitHub owner/repo from: {url}")
    repo = m.group(1).rstrip("/")

    result = subprocess.run(
        ["gh", "repo", "view", repo, "--json",
         "name,description,languages,stargazerCount"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh repo view failed: {result.stderr[:200]}")

    data = json.loads(result.stdout)
    title = data.get("name", repo)
    description = data.get("description", "")
    # languages is a list of {"size": N, "node": {"name": "Python"}} in gh v2.4
    lang_raw = data.get("languages") or []
    if lang_raw and isinstance(lang_raw[0], dict) and "node" in lang_raw[0]:
        languages = [l["node"]["name"] for l in lang_raw[:8]]
    else:
        languages = list(lang_raw)[:8]
    topics: list[str] = []
    stars = data.get("stargazerCount", 0)

    # Fetch README via gh api (works on all gh versions)
    readme = ""
    readme_result = subprocess.run(
        ["gh", "api", f"repos/{repo}/readme", "--jq", ".content"],
        capture_output=True, text=True, timeout=15,
    )
    if readme_result.returncode == 0 and readme_result.stdout.strip():
        import base64
        try:
            readme = base64.b64decode(readme_result.stdout.strip().replace("\\n", "\n")).decode("utf-8", errors="replace")[:6000]
        except Exception:
            pass

    text_parts = []
    if description:
        text_parts.append(f"## Description\n{description}")
    if languages:
        text_parts.append(f"## Languages\n{', '.join(languages)}")
    if topics:
        text_parts.append(f"## Topics\n{', '.join(topics)}")
    if readme:
        text_parts.append(f"## README\n{readme}")

    return ExtractResult(
        text="\n\n".join(text_parts),
        title=title,
        metadata={"repo": repo, "languages": languages, "topics": topics, "stars": stars, "url": url},
        content_type="github",
        url=url,
    )


def extract_article(url: str) -> ExtractResult:
    import urllib.request as urlreq
    try:
        req = urlreq.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; JarvisBot/1.0)"})
        with urlreq.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc

    try:
        from readability import Document  # type: ignore
        doc = Document(html)
        title = doc.title()
        content_html = doc.summary()
        text = re.sub(r"<[^>]+>", " ", content_html)
        text = re.sub(r"\s{2,}", "\n", text).strip()[:8000]
    except Exception:
        # Fallback: strip all tags
        title = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
        title = title.group(1).strip() if title else url
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s{2,}", "\n", text).strip()[:8000]

    return ExtractResult(
        text=text,
        title=title[:120],
        metadata={"url": url},
        content_type="article",
        url=url,
    )


def extract_pdf(path: str) -> ExtractResult:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError("pypdf not installed. Run: pip install pypdf") from exc

    reader = PdfReader(path)
    pages = [(p.extract_text() or "") for p in reader.pages]
    text = "\n\n".join(p.strip() for p in pages if p.strip())[:10000]
    title = Path(path).stem.replace("-", " ").replace("_", " ").title()
    return ExtractResult(
        text=text or "No extractable text.",
        title=title,
        metadata={"path": path, "pages": len(reader.pages)},
        content_type="pdf",
        url=path,
    )


def extract_local(path: str) -> ExtractResult:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        return extract_pdf(path)
    text = p.read_text(encoding="utf-8", errors="replace")[:10000]
    title = p.stem.replace("-", " ").replace("_", " ").title()
    return ExtractResult(
        text=text,
        title=title,
        metadata={"path": path},
        content_type="local",
        url=path,
    )


def extract_chat(path: str) -> ExtractResult:
    """Extract WhatsApp / chat export (.txt or .zip)."""
    import zipfile
    p = Path(path)
    text = ""

    if p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as zf:
            for name in zf.namelist():
                if name.endswith(".txt"):
                    text = zf.read(name).decode("utf-8", errors="replace")
                    break
    else:
        text = p.read_text(encoding="utf-8", errors="replace")

    # Strip WhatsApp header lines and media omitted markers
    lines = [l for l in text.splitlines()
             if not re.match(r"^\[?\d{1,2}/\d{1,2}/\d{2,4}", l) or
             not l.strip().endswith("omitted")]
    clean = "\n".join(lines)

    # Extract URLs from the chat
    urls = re.findall(r"https?://[^\s\)\]>\"']+", clean)
    url_set: list[str] = []
    seen: set[str] = set()
    for u in urls:
        u = u.rstrip(".,;)>")
        if u not in seen:
            seen.add(u)
            url_set.append(u)

    title = p.stem.replace("-", " ").replace("_", " ").title()
    return ExtractResult(
        text=clean[:12000],
        title=title,
        metadata={"path": str(p), "urls_found": url_set[:50]},
        content_type="chat",
        url=str(p),
    )


# ── LLM analysis ───────────────────────────────────────────────────────────────

PROMPTS = {
    "youtube": (
        "Analiza este contenido de YouTube. Extrae en JSON:\n"
        "- title: título limpio\n"
        "- topic: tema principal (1 línea)\n"
        "- key_points: lista de 3-5 puntos clave\n"
        "- concepts: conceptos técnicos o términos notables\n"
        "- domain: bjj|ml|programming|health|other\n"
        "- summary: resumen de 2-3 frases\n"
        "- tags: lista de 4-6 tags kebab-case\n"
        "Devuelve SOLO el JSON, sin texto extra."
    ),
    "instagram": (
        "Analiza este contenido de Instagram. Extrae en JSON:\n"
        "- title: título descriptivo\n"
        "- topic: tema principal\n"
        "- key_points: lista de 2-4 puntos\n"
        "- technique: si es BJJ, nombre de la técnica (o null)\n"
        "- domain: bjj|fitness|other\n"
        "- summary: resumen de 1-2 frases\n"
        "- tags: lista de 4-6 tags kebab-case\n"
        "Devuelve SOLO el JSON."
    ),
    "github": (
        "Analiza este repositorio de GitHub. Extrae en JSON:\n"
        "- title: nombre del repo\n"
        "- purpose: qué hace (1-2 frases)\n"
        "- stack: tecnologías principales\n"
        "- patterns: patrones de implementación notables (lista)\n"
        "- reusable: true|false (¿se puede reutilizar en otros proyectos?)\n"
        "- domain: ai|web|devops|data|mobile|other\n"
        "- summary: descripción de 2-3 frases\n"
        "- tags: lista de 4-6 tags kebab-case\n"
        "Devuelve SOLO el JSON."
    ),
    "article": (
        "Analiza este artículo. Extrae en JSON:\n"
        "- title: título limpio\n"
        "- thesis: tesis o argumento principal (1 frase)\n"
        "- key_points: lista de 3-5 puntos clave\n"
        "- concepts: conceptos nuevos o términos técnicos\n"
        "- domain: tech|science|bjj|business|other\n"
        "- summary: resumen de 2-3 frases\n"
        "- tags: lista de 4-6 tags kebab-case\n"
        "Devuelve SOLO el JSON."
    ),
    "pdf": (
        "Analiza este documento PDF. Extrae en JSON:\n"
        "- title: título limpio\n"
        "- doc_type: paper|manual|report|book|other\n"
        "- key_points: lista de 3-5 puntos principales\n"
        "- concepts: conceptos o términos técnicos clave\n"
        "- domain: tech|science|bjj|other\n"
        "- summary: resumen ejecutivo de 2-3 frases\n"
        "- tags: lista de 4-6 tags kebab-case\n"
        "Devuelve SOLO el JSON."
    ),
    "local": (
        "Analiza este documento. Extrae en JSON:\n"
        "- title: título descriptivo\n"
        "- key_points: lista de 3-5 puntos clave\n"
        "- concepts: términos o conceptos importantes\n"
        "- summary: resumen de 2-3 frases\n"
        "- tags: lista de 4-6 tags kebab-case\n"
        "Devuelve SOLO el JSON."
    ),
    "chat": (
        "Analiza esta conversación/chat exportado. Extrae en JSON:\n"
        "- title: título descriptivo del tema principal\n"
        "- summary: resumen de 2-3 frases del contenido de la conversación\n"
        "- actions: lista de cosas concretas a hacer mencionadas o implícitas (máx 10)\n"
        "- concepts: conceptos técnicos, temas o términos importantes mencionados\n"
        "- questions: preguntas abiertas o temas que necesitan investigación\n"
        "- decisions: decisiones tomadas o conclusiones alcanzadas\n"
        "- domains: lista de dominios relevantes (bjj, ml, programming, health, other)\n"
        "- tags: lista de 5-8 tags kebab-case\n"
        "Devuelve SOLO el JSON."
    ),
}


def analyze_with_llm(extracted: ExtractResult, model: str) -> dict:
    sys.path.insert(0, str(Path(__file__).parent))
    from jarvis_llm import JarvisLLM  # type: ignore

    llm = JarvisLLM(model)
    prompt = PROMPTS.get(extracted.content_type, PROMPTS["article"])
    user_msg = f"{prompt}\n\n---\nTitle: {extracted.title}\nURL: {extracted.url}\n\n{extracted.text[:6000]}"

    resp = llm.complete(user_msg, system="You are a content analyst. Always respond with valid JSON only.")

    # Parse JSON from response
    text = resp.text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Best-effort: extract partial JSON
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        # Fallback: minimal analysis
        return {
            "title": extracted.title,
            "summary": extracted.text[:200],
            "tags": [extracted.content_type],
        }


# ── Note builder ───────────────────────────────────────────────────────────────

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:60] or "untitled"


def yaml_list(values: list) -> str:
    if not values:
        return "[]"
    items = [f"  - \"{str(v)}\"" for v in values]
    return "\n" + "\n".join(items)


def build_note(extracted: ExtractResult, analysis: dict, out_folder: str,
               relevance_section: str = "") -> tuple[Path, str]:
    today = date.today().isoformat()

    title = analysis.get("title") or extracted.title
    summary = analysis.get("summary", "")
    tags = analysis.get("tags", [extracted.content_type])
    key_points = analysis.get("key_points", [])
    concepts = analysis.get("concepts", [])
    domain = analysis.get("domain", "") or ", ".join(analysis.get("domains", []))

    # Ensure content type is in tags
    if extracted.content_type not in tags:
        tags = [extracted.content_type] + list(tags)

    frontmatter_lines = [
        "---",
        f'title: "{title}"',
        "type: source",
        "status: NEW",
        f"tags:{yaml_list(tags)}",
        f"created: {today}",
        f"updated: {today}",
        f"tokens_consumed: {max(1, len(extracted.text.split()) * 4 // 3)}",
        f'sources:\n  - "{extracted.url}"',
        f'Summary: "{summary}"',
        "requires_verification: true",
        "validated: ~",
        "---",
    ]

    body_lines = [
        f"# {title}",
        "",
        f"> {summary}",
        "",
    ]

    if key_points:
        body_lines += ["## Key Points", ""]
        for pt in key_points:
            body_lines.append(f"- {pt}")
        body_lines.append("")

    if concepts:
        body_lines += ["## Concepts", ""]
        concepts_list = concepts if isinstance(concepts, list) else [concepts]
        for c in concepts_list:
            body_lines.append(f"- {c}")
        body_lines.append("")

    # GitHub-specific: patterns section
    patterns = analysis.get("patterns", [])
    if patterns:
        body_lines += ["## Implementation Patterns", ""]
        for p in patterns:
            body_lines.append(f"- {p}")
        body_lines.append("")

    # Chat-specific sections
    questions = analysis.get("questions", [])
    if questions:
        body_lines += ["## Open Questions", ""]
        for q in questions:
            body_lines.append(f"- {q}")
        body_lines.append("")

    decisions = analysis.get("decisions", [])
    if decisions:
        body_lines += ["## Decisions / Conclusions", ""]
        for d in decisions:
            body_lines.append(f"- {d}")
        body_lines.append("")

    # Relevance section (injected by relevance_mapper)
    if relevance_section:
        body_lines += ["", relevance_section]

    body_lines += [
        "## Source",
        "",
        f"- URL: {extracted.url}",
        f"- Type: {extracted.content_type}",
    ]
    if domain:
        body_lines.append(f"- Domain: {domain}")
    body_lines += ["", "## Raw Extract (excerpt)", "", extracted.text[:2000]]

    content = "\n".join(frontmatter_lines) + "\n\n" + "\n".join(body_lines) + "\n"

    # Choose output directory
    if out_folder == "patterns":
        folder = WIKI_PATTERNS
    elif out_folder == "concepts":
        folder = WIKI_CONCEPTS
    else:
        folder = WIKI_SOURCES

    folder.mkdir(parents=True, exist_ok=True)
    base = slugify(title or extracted.content_type)
    out_path = folder / f"{base}.md"
    counter = 2
    while out_path.exists():
        out_path = folder / f"{base}-{counter}.md"
        counter += 1

    return out_path, content


def build_tasks_note(extracted: ExtractResult, analysis: dict) -> tuple[Path, str] | None:
    """Create a separate wiki/tasks/ note from chat action items."""
    actions = analysis.get("actions", [])
    if not actions:
        return None

    today = date.today().isoformat()
    title = analysis.get("title", extracted.title)
    tags = analysis.get("tags", ["chat"])
    summary = f"Action items extracted from: {title}"

    frontmatter_lines = [
        "---",
        f'title: "Actions: {title}"',
        "type: tasks",
        "status: NEW",
        f"tags:{yaml_list(tags + ['actions'])}",
        f"created: {today}",
        f"updated: {today}",
        "tokens_consumed: 0",
        f'sources:\n  - "{extracted.url}"',
        f'Summary: "{summary}"',
        "---",
    ]

    body_lines = [f"# Actions: {title}", "", f"> From: {extracted.url}", ""]
    body_lines += ["## Action Items", ""]
    for action in actions:
        body_lines.append(f"- [ ] {action}")
    body_lines.append("")

    questions = analysis.get("questions", [])
    if questions:
        body_lines += ["## Open Questions", ""]
        for q in questions:
            body_lines.append(f"- [ ] Research: {q}")
        body_lines.append("")

    content = "\n".join(frontmatter_lines) + "\n\n" + "\n".join(body_lines) + "\n"

    WIKI_TASKS.mkdir(parents=True, exist_ok=True)
    base = slugify(f"actions-{title}")
    out_path = WIKI_TASKS / f"{base}.md"
    counter = 2
    while out_path.exists():
        out_path = WIKI_TASKS / f"{base}-{counter}.md"
        counter += 1

    return out_path, content


# ── Main ───────────────────────────────────────────────────────────────────────

EXTRACTORS = {
    "youtube": extract_youtube,
    "instagram": extract_instagram,
    "github": extract_github,
    "article": extract_article,
    "pdf": extract_pdf,
    "local": extract_local,
    "chat": extract_chat,
}


def analyze(target: str, content_type: str = "auto", model: str = "local",
            out_folder: str = "sources", no_llm: bool = False,
            no_relevance: bool = False) -> dict:

    if content_type == "auto":
        content_type = detect_type(target)

    extractor = EXTRACTORS.get(content_type)
    if not extractor:
        raise ValueError(f"Unknown content type: {content_type}")

    extracted = extractor(target)

    if no_llm:
        analysis = {"title": extracted.title, "summary": extracted.text[:200], "tags": [content_type]}
    else:
        analysis = analyze_with_llm(extracted, model)

    # Build relevance section — map content to active projects
    relevance_section = ""
    if not no_relevance and not no_llm:
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from relevance_mapper import map_relevance, format_relevance_section  # type: ignore
            concepts = analysis.get("concepts", [])
            if isinstance(concepts, str):
                concepts = [concepts]
            tags = analysis.get("tags", [])
            mappings = map_relevance(
                content_title=analysis.get("title", extracted.title),
                content_summary=analysis.get("summary", ""),
                concepts=concepts,
                tags=tags,
                model=model,
            )
            relevance_section = format_relevance_section(mappings)
        except Exception:
            pass

    # For GitHub repos with patterns, also save to wiki/patterns/
    if content_type == "github" and analysis.get("reusable") and out_folder == "sources":
        pattern_path, pattern_content = build_note(extracted, analysis, "patterns", relevance_section)
        pattern_path.write_text(pattern_content, encoding="utf-8")

    out_path, content = build_note(extracted, analysis, out_folder, relevance_section)
    out_path.write_text(content, encoding="utf-8")

    extra_outputs: list[str] = []

    # For chat exports: also create a tasks note with action items
    if content_type == "chat":
        tasks_result = build_tasks_note(extracted, analysis)
        if tasks_result:
            tasks_path, tasks_content = tasks_result
            tasks_path.write_text(tasks_content, encoding="utf-8")
            extra_outputs.append(str(tasks_path.relative_to(ROOT)))

    result: dict = {
        "status": "ok",
        "output": str(out_path.relative_to(ROOT)),
        "type": content_type,
        "title": analysis.get("title", extracted.title),
        "summary": analysis.get("summary", ""),
    }
    if extra_outputs:
        result["extra_outputs"] = extra_outputs
    if relevance_section:
        result["relevance_mapped"] = True

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="URL or file path to analyze")
    parser.add_argument("--type", dest="content_type", default="auto",
                        choices=["auto", "youtube", "instagram", "github", "pdf", "article", "local", "chat"])
    parser.add_argument("--model", default=None, help="LLM backend (default: $JARVIS_DEFAULT_MODEL or local)")
    parser.add_argument("--out", dest="out_folder", default="sources",
                        choices=["sources", "patterns", "concepts"])
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM analysis, save raw extract only")
    parser.add_argument("--no-relevance", action="store_true", help="Skip project relevance mapping")
    args = parser.parse_args()

    import os
    model = args.model or os.environ.get("JARVIS_DEFAULT_MODEL", "local")

    try:
        result = analyze(
            target=args.target,
            content_type=args.content_type,
            model=model,
            out_folder=args.out_folder,
            no_llm=args.no_llm,
            no_relevance=args.no_relevance,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "detail": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
