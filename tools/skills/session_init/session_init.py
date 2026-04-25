#!/usr/bin/env python3
"""CLI wrapper to call the JarvisOS Session Wizard API and print the generated CLAUDE.md."""
from __future__ import annotations

import argparse
import json
import sys

try:
    import httpx
except ImportError:
    print("httpx required: pip install httpx", file=sys.stderr)
    sys.exit(1)

DEFAULT_URL = "http://127.0.0.1:5055"


def main() -> int:
    parser = argparse.ArgumentParser(description="JarvisOS Session Init — generate CLAUDE.md from contexts")
    parser.add_argument("--host", default=DEFAULT_URL)
    parser.add_argument("--profile", help="Profile path relative to contexts/ (e.g. profiles/backend-dev-day.md)")
    parser.add_argument("--contexts", nargs="*", help="Context paths to include")
    parser.add_argument("--save", action="store_true", help="Save profile to vault")
    parser.add_argument("--name", default="", help="Profile name if saving")
    parser.add_argument("--list", action="store_true", help="List available contexts")
    args = parser.parse_args()

    with httpx.Client(base_url=args.host, timeout=10) as client:
        if args.list:
            resp = client.get("/api/session/contexts")
            resp.raise_for_status()
            data = resp.json()
            for cat, files in data.items():
                print(f"\n## {cat}")
                for f in files:
                    print(f"  {f['path']} — {f['description']}")
            return 0

        payload = {
            "contexts": args.contexts or [],
            "profile": args.profile,
            "save_profile": args.save,
            "profile_name": args.name,
        }
        resp = client.post("/api/session/generate", json=payload)
        resp.raise_for_status()
        result = resp.json()
        print(result["claude_md"])
        if result.get("saved_path"):
            print(f"\n# Saved to: {result['saved_path']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
