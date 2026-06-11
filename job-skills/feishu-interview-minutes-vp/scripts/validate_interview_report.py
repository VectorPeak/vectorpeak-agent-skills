#!/usr/bin/env python3
"""Lightweight validation for generated interview question-chain Markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_FRONTMATTER = {
    "source",
    "source_type",
    "date",
    "company",
    "position",
    "candidate",
    "tags",
    "type",
}
ALLOWED_SOURCE_TYPES = {"feishu-docx-ai-minutes", "feishu-minutes", "transcript-doc", "pasted"}
MOJIBAKE_PATTERNS = [
    "濡欒",
    "闈㈣",
    "涓婚棶",
    "杩介棶",
    "鐩稿叧",
    "鏂囧瓧",
]


def split_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, text, ["missing YAML frontmatter"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text, ["missing closing YAML frontmatter fence"]

    raw = text[4:end]
    body = text[end + 4 :]
    fields: dict[str, str] = {}
    current_key = ""
    for line in raw.splitlines():
        if not line.strip() or line.startswith("  - "):
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        fields[current_key] = value.strip().strip('"')
    if current_key == "":
        errors.append("empty YAML frontmatter")
    return fields, body, errors


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    fields, body, frontmatter_errors = split_frontmatter(text)
    errors.extend(frontmatter_errors)

    missing = sorted(REQUIRED_FRONTMATTER - set(fields))
    if missing:
        errors.append("missing frontmatter field(s): " + ", ".join(missing))
    source_type = fields.get("source_type", "")
    if source_type and source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"invalid source_type: {source_type}")
    if fields.get("type") and fields["type"] != "interview-question-chain":
        errors.append("type must be interview-question-chain")

    if "\n# " not in text:
        errors.append("missing level-1 title")
    if "**主问题：**" not in body:
        errors.append("missing **主问题：** entries")
    if "- **追问" not in body and "- **质疑" not in body and "- **反问" not in body and "- **边界确认" not in body:
        warnings.append("no follow-up/challenge entries found")
    if re.search(r"^#{3,}\s", body, flags=re.MULTILINE):
        errors.append("unexpected heading depth; use # and ## only unless necessary")
    for pattern in MOJIBAKE_PATTERNS:
        if pattern in text:
            warnings.append(f"possible mojibake pattern: {pattern}")
            break
    if "obcn" in body:
        errors.append("raw minute token appears in report body")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()

    text = Path(args.report).read_text(encoding="utf-8")
    errors, warnings = validate(text)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
