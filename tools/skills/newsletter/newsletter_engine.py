#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_os.config import get_settings
from jarvis_os.integrations.newsletter import NewsletterEngine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="today")
    parser.add_argument("--sections", default="")
    parser.add_argument("--output", default="html,md,pdf")
    parser.add_argument("--no-pdf", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    if args.check:
        print(f"vault: {settings.vault_dir.exists()}")
        try:
            import weasyprint  # type: ignore  # noqa: F401
            print("weasyprint: true")
        except Exception:
            print("weasyprint: false")
        return 0

    target_date = date.today() if args.date == "today" else date.fromisoformat(args.date)
    sections = [item.strip() for item in args.sections.split(",") if item.strip()] or None
    result = NewsletterEngine(settings).generate(
        target_date=target_date,
        sections=sections,
        export_pdf=(not args.no_pdf and "pdf" in args.output.split(",")),
    )
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
