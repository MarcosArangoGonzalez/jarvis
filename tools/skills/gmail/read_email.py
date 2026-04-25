#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("message_id")
    args = parser.parse_args()
    auth = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
    if not auth.exists():
        print("Gmail OAuth is not configured. Expected ~/.gmail-mcp/gcp-oauth.keys.json")
        return 2
    print(f"Gmail read placeholder: message_id={args.message_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
