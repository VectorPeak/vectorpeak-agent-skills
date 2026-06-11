#!/usr/bin/env python3
"""Extract Feishu/Lark related links from an intelligent note Markdown file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


LINK_RE = re.compile(r"\[([^\]]+)\]\(\s*(<https?://[^>]+>|https?://[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)")
URL_RE = re.compile(r"https?://[^\s)>\"]+")
FEISHU_HOST_RE = re.compile(r"(^|\.)((feishu\.cn)|(larksuite\.com))$", re.IGNORECASE)


def normalize_url(url: str) -> str:
    url = url.strip().strip("<>")
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def is_feishu_url(url: str) -> bool:
    host = urlsplit(url).netloc.split("@")[-1].split(":")[0]
    return bool(FEISHU_HOST_RE.search(host))


def line_context(line: str) -> str:
    stripped = line.strip()
    if "文字记录" in stripped:
        return "文字记录"
    if "妙记" in stripped:
        return "妙记"
    return ""


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

    parent_context = ""
    parent_indent = 0
    for line in search_text.splitlines():
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        current_context = line_context(line)
        has_link = bool(LINK_RE.search(line))

        if current_context and not has_link:
            parent_context = current_context
            parent_indent = indent
            continue
        if parent_context and stripped.startswith(("-", "*")) and indent <= parent_indent and not current_context:
            parent_context = ""
        if parent_context and stripped and indent <= parent_indent and not stripped.startswith(("-", "*")):
            parent_context = ""

        effective_context = current_context or parent_context
        for match in LINK_RE.finditer(line):
            label = match.group(1).strip()
            url = normalize_url(match.group(2))
            if not is_feishu_url(url) or url in seen:
                continue
            seen.add(url)
            effective_label = f"{effective_context} {label}".strip()
            links.append({"type": classify(effective_label, url), "label": label, "url": url})

    for match in URL_RE.finditer(search_text):
        url = normalize_url(match.group(0))
        if not is_feishu_url(url) or url in seen:
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
