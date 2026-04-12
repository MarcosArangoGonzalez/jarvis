#!/usr/bin/env python3
"""Daily context aggregator for JarvisOS."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"
WIKI_SOURCES = WIKI / "sources"
INDEX = WIKI / "index.md"


def read_index() -> str:
    return INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""


def unindexed_sources() -> list[Path]:
    index = read_index()
    return [path for path in sorted(WIKI_SOURCES.glob("*.md")) if path.name not in index and str(path.relative_to(ROOT)) not in index]


def github_context() -> list[str]:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        return ["GitHub: no token configured."]
    try:
        completed = subprocess.run(["gh", "pr", "status", "--json", "currentBranch"], capture_output=True, text=True, check=True)
        return [f"GitHub: {completed.stdout.strip()[:500]}"]
    except Exception as exc:
        return [f"GitHub: unavailable ({exc})."]


def linear_context() -> list[str]:
    token = os.getenv("LINEAR_API_KEY")
    if not token:
        return ["Linear: no token configured."]
    query = b'{"query":"query Viewer { viewer { name } }"}'
    request = Request("https://api.linear.app/graphql", data=query, headers={"Content-Type": "application/json", "Authorization": token})
    try:
        with urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        return [f"Linear: authenticated as {data.get('data', {}).get('viewer', {}).get('name', 'unknown')}."]
    except Exception as exc:
        return [f"Linear: unavailable ({exc})."]


def news_context() -> list[str]:
    feed_url = os.getenv("JARVIS_NEWS_FEED_URL")
    if not feed_url:
        return ["News: no JARVIS_NEWS_FEED_URL configured."]
    try:
        with urlopen(feed_url, timeout=5) as response:
            snippet = response.read(800).decode("utf-8", errors="replace")
        return [f"News: feed reachable ({len(snippet)} chars sampled)."]
    except Exception as exc:
        return [f"News: unavailable ({exc})."]


def main() -> None:
    print(f"# Morning Coffee - {date.today().isoformat()}")
    print()
    print("## GitHub")
    print("\n".join(f"- {item}" for item in github_context()))
    print()
    print("## Linear")
    print("\n".join(f"- {item}" for item in linear_context()))
    print()
    print("## News")
    print("\n".join(f"- {item}" for item in news_context()))
    print()
    print("## Wiki Gaps")
    gaps = unindexed_sources()
    if gaps:
        for path in gaps:
            print(f"- Unindexed source: {path.relative_to(ROOT)}")
    else:
        print("- No unindexed source notes found.")


if __name__ == "__main__":
    main()
