from __future__ import annotations

import re
from pathlib import Path

from ..config import Settings
from ..schemas import SecurityFinding, SecurityScanRequest, SecurityScanResult


class SecurityRegexScanner:
    PATTERNS = [
        ("ipv4", "IPv4 address", "info", re.compile(r"\b([0-9]{1,3}\.){3}[0-9]{1,3}\b")),
        ("email", "Email address", "info", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
        ("url", "URL/domain", "info", re.compile(r"https?://[a-zA-Z0-9._-]+(/\S*)?")),
        ("hash-md5", "MD5 hash", "warning", re.compile(r"\b[a-fA-F0-9]{32}\b")),
        ("aws-key", "AWS access key", "high", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("base64", "Base64 payload", "warning", re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")),
        ("jwt", "JWT token", "high", re.compile(r"ey[A-Za-z0-9+/=_-]{10,}\.ey[A-Za-z0-9+/=_-]{10,}\.[A-Za-z0-9+/=_-]+")),
    ]

    SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "tools/local"}

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def scan(self, request: SecurityScanRequest) -> SecurityScanResult:
        root = Path(request.path)
        if not root.is_absolute():
            root = self.settings.root_dir / root
        files = [root] if root.is_file() else self._iter_files(root)
        findings: list[SecurityFinding] = []
        scanned = 0
        for path in files:
            if not request.include_binary and self._looks_binary(path):
                continue
            scanned += 1
            findings.extend(self._scan_file(path))
        return SecurityScanResult(
            scanned_path=str(root),
            findings=findings[:500],
            files_scanned=scanned,
        )

    def precommit_hook(self) -> str:
        return """#!/bin/bash
FILES=$(git diff --cached --name-only)

echo "$FILES" | xargs grep -lE 'AKIA[0-9A-Z]{16}' 2>/dev/null && echo "ERROR: AWS key detected" && exit 1
echo "$FILES" | xargs grep -lE 'ey[A-Za-z0-9+/=_-]{10,}\\.ey' 2>/dev/null && echo "ERROR: JWT-like token detected" && exit 1
echo "$FILES" | xargs grep -lE '[A-Za-z0-9+/]{80,}={0,2}' 2>/dev/null && echo "WARN: suspicious base64 blob detected" && exit 1

exit 0
"""

    def _iter_files(self, root: Path) -> list[Path]:
        results: list[Path] = []
        if not root.exists():
            return results
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            rel_parts = set(path.relative_to(self.settings.root_dir).parts) if path.is_relative_to(self.settings.root_dir) else set(path.parts)
            if rel_parts.intersection(self.SKIP_DIRS):
                continue
            results.append(path)
        return results

    def _scan_file(self, path: Path) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return findings
        rel = str(path.relative_to(self.settings.root_dir)) if path.is_relative_to(self.settings.root_dir) else str(path)
        for number, line in enumerate(lines, 1):
            for pattern_id, label, severity, regex in self.PATTERNS:
                for match in regex.finditer(line):
                    findings.append(
                        SecurityFinding(
                            pattern_id=pattern_id,
                            label=label,
                            severity=severity,  # type: ignore[arg-type]
                            path=rel,
                            line=number,
                            match=match.group(0)[:160],
                            context=line.strip()[:220],
                        )
                    )
        return findings

    @staticmethod
    def _looks_binary(path: Path) -> bool:
        try:
            return b"\0" in path.read_bytes()[:1024]
        except OSError:
            return True
