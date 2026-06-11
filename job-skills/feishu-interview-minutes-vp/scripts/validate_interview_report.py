#!/usr/bin/env python3
"""Lightweight validation for generated interview question-chain Markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MOJIBAKE_PATTERNS = [
    "璇",
    "绋",
    "鐩",
    "濡欒",
    "闈㈣",
]


def validate(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        errors.append("missing YAML frontmatter")
    if "\n# " not in text:
        errors.append("missing level-1 title")
    if "**主问题：**" not in text:
        errors.append("missing **主问题：** entries")
    if "- **追问" not in text:
        errors.append("missing follow-up entries")
    if re.search(r"^#{3,}\s", text, flags=re.MULTILINE):
        errors.append("unexpected heading depth; use # and ## only unless necessary")
    for pattern in MOJIBAKE_PATTERNS:
        if pattern in text:
            errors.append(f"possible mojibake pattern: {pattern}")
            break
    if "obcn" in text and "related_minutes:" not in text:
        errors.append("raw minute token appears outside related_minutes metadata")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()

    text = Path(args.report).read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
