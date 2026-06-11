#!/usr/bin/env python3
"""Extract Feishu/Lark related links from an intelligent note Markdown file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
URL_RE = re.compile(r"https?://[^\s)>\"]+")


def classify(label: str, url: str) -> str:
    text = f"{label} {url}".lower()
    if "/minutes/" in text or "妙记" in label:
        return "minutes"
    if "/docx/" in text and ("文字记录" in label or "transcript" in text):
        return "transcript_doc"
    if "/docx/" in text:
        return "docx"
    if "/wiki/" in text:
        return "wiki"
    return "other"


def extract_links(text: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()

    related_pos = text.rfind("相关链接")
    search_text = text[related_pos:] if related_pos >= 0 else text

    context = ""
    for line in search_text.splitlines():
        stripped = line.strip()
        if "文字记录" in stripped and not LINK_RE.search(stripped):
            context = "文字记录"
        elif "妙记" in stripped and not LINK_RE.search(stripped):
            context = "妙记"

        for match in LINK_RE.finditer(line):
            label = match.group(1).strip()
            url = match.group(2).strip()
            if url in seen:
                continue
            seen.add(url)
            effective_label = f"{context} {label}".strip()
            links.append({"type": classify(effective_label, url), "label": label, "url": url})

    for match in URL_RE.finditer(search_text):
        url = match.group(0).strip()
        if url in seen or "feishu.cn" not in url and "larksuite.com" not in url:
            continue
        seen.add(url)
        links.append({"type": classify("", url), "label": "", "url": url})

    return links


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Markdown/text file exported from Feishu Docx")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    links = extract_links(text)

    result: dict[str, Any] = {
        "links": links,
        "minutes": [item for item in links if item["type"] == "minutes"],
        "transcript_docs": [item for item in links if item["type"] == "transcript_doc"],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in links:
            print(f"{item['type']}\t{item['label']}\t{item['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
