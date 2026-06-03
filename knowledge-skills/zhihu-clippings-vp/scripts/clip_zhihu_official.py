#!/usr/bin/env python
"""Clip Zhihu official API author-search results into grouped Markdown files."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows fallback
    winreg = None

DEFAULT_OUTPUT_DIR = Path.cwd() / "clippings"
DEFAULT_CACHE_DIR = DEFAULT_OUTPUT_DIR / ".llmwiki-cache" / "zhihu-clippings-vp"
API_URL = "https://developer.zhihu.com/api/v1/content/zhihu_search"
TIKHUB_USER_ARTICLES_URL = "https://api.tikhub.io/api/v1/zhihu/web/fetch_user_articles"
TIKHUB_ARTICLE_DETAIL_URL = "https://api.tikhub.io/api/v1/zhihu/web/fetch_column_article_detail"
TIKHUB_QUESTION_ANSWERS_URL = "https://api.tikhub.io/api/v1/zhihu/web/fetch_question_answers"
MAX_COUNT_PER_OFFICIAL_QUERY = 10
DEFAULT_OFFICIAL_DELAY_SECONDS = 1.2
CHINESE_NUMERALS = "零一二三四五六七八九十"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use Zhihu official developer API to find an author and bundle recent Article results."
    )
    parser.add_argument(
        "input",
        help="Person name, Zhihu people URL, article URL, article title, or mixed description.",
    )
    parser.add_argument("-n", "--count", type=int, default=10, help="Maximum article results to keep after filtering.")
    parser.add_argument("--author", default=None, help="Known target author name. Skips author inference when provided.")
    parser.add_argument("--title-source", default=None, help="Screenshot OCR text, HTML file, or text file to discover article titles from.")
    parser.add_argument("--extra-query", action="append", default=[], help="Additional search query. Can be repeated.")
    parser.add_argument("--extra-query-file", default=None, help="UTF-8 text file with one additional search query per line.")
    parser.add_argument("--group-size", "--batch-size", dest="group_size", type=int, default=5, help="Results per Markdown bundle.")
    parser.add_argument("--ranges", default=None, help='Custom 1-based article ranges, for example "1", "2-3", or "1-5,6-10". Overrides --group-size.')
    parser.add_argument(
        "--filename-template",
        default="知乎_{author}_{summary}_知乎文章搜索剪藏_{date}_{range}.md",
        help="Markdown filename template. Available fields: author, summary, date, range.",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for Markdown bundle files.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Directory for raw API response cache.")
    parser.add_argument("--access-secret", default=None, help="Zhihu developer Access Secret. Defaults to ZHIHU_ACCESS_SECRET.")
    parser.add_argument("--tikhub-api-key", default=None, help="TikHub API key. Defaults to TIKHUB_API_KEY.")
    parser.add_argument("--user-url-token", default=None, help="Zhihu people URL token, for example dan-mo-41-42.")
    parser.add_argument("--article-id", action="append", default=[], help="Specific Zhihu zhuanlan article id to fetch through TikHub detail API. Can be repeated.")
    parser.add_argument("--question-id", default=None, help="Zhihu question id for answer fulltext mode.")
    parser.add_argument("--answer-id", action="append", default=[], help="Specific Zhihu answer id to fetch through TikHub question answers API. Can be repeated.")
    parser.add_argument(
        "--content-provider",
        choices=["official", "tikhub", "auto"],
        default="auto",
        help="official keeps official API summaries; tikhub uses TikHub content after official positioning; auto uses TikHub when key and user token are available.",
    )
    parser.add_argument("--tikhub-limit", type=int, default=None, help="Number of TikHub user articles to fetch. Defaults to --count.")
    parser.add_argument("--official-delay", type=float, default=DEFAULT_OFFICIAL_DELAY_SECONDS, help="Delay between official API queries, to avoid per-second rate limits.")
    parser.add_argument("--llm-heading-review", action="store_true", help="Optionally ask an OpenAI-compatible LLM to review generated heading levels.")
    parser.add_argument("--llm-model", default="gpt-4.1-mini", help="Model for --llm-heading-review.")
    parser.add_argument("--llm-base-url", default=None, help="OpenAI-compatible base URL. Defaults to OPENAI_BASE_URL or https://api.openai.com/v1.")
    parser.add_argument("--llm-api-key", default=None, help="API key for --llm-heading-review. Defaults to OPENAI_API_KEY.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print summary without writing Markdown bundles.")
    return parser.parse_args()


def get_secret(explicit: str | None) -> str:
    secret = explicit or os.environ.get("ZHIHU_ACCESS_SECRET") or read_user_env("ZHIHU_ACCESS_SECRET")
    if secret:
        return secret.strip()
    raise RuntimeError(
        "ZHIHU_ACCESS_SECRET is not set. Get an Access Secret from https://developer.zhihu.com/profile "
        "or pass --access-secret."
    )


def get_tikhub_key(explicit: str | None, required: bool) -> str | None:
    key = explicit or os.environ.get("TIKHUB_API_KEY") or read_user_env("TIKHUB_API_KEY")
    if key:
        key = key.strip()
        if key.upper().startswith("API:"):
            key = key.split(":", 1)[1].strip()
        return key
    if required:
        raise RuntimeError("TIKHUB_API_KEY is not set. Pass --tikhub-api-key or set the user environment variable.")
    return None


def read_user_env(name: str) -> str | None:
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
    except OSError:
        return None


def today() -> str:
    return dt.date.today().isoformat()


def iso_date_from_ts(value: Any) -> str:
    if value in (None, "", 0):
        return ""
    try:
        return dt.datetime.fromtimestamp(int(value), tz=dt.timezone.utc).astimezone().date().isoformat()
    except Exception:
        return ""


def yaml_quote(value: Any) -> str:
    text = "" if value is None else str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def strip_html(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?(em|strong|b|i)>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def safe_text(value: str, fallback: str = "zhihu-author") -> str:
    value = value.replace("\ufeff", "")
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value).strip()
    text = re.sub(r"\s+", " ", text)
    return (text or fallback)[:90].rstrip()


def safe_filename_part(value: str, fallback: str = "zhihu") -> str:
    text = safe_text(value, fallback=fallback)
    text = re.sub(r"\s+", "_", text)
    return text or fallback


def normalize_input(raw_input: str) -> str:
    text = unquote(raw_input.strip())
    parsed = urlparse(text)
    if parsed.scheme and parsed.netloc:
        path_parts = [p for p in parsed.path.split("/") if p]
        if parsed.netloc.endswith("zhihu.com") and len(path_parts) >= 2 and path_parts[0] == "people":
            token = path_parts[1]
            return f"{token} 知乎 作者 文章"
        if "zhuanlan.zhihu.com" in parsed.netloc and path_parts:
            return f"{path_parts[-1]} 知乎 文章 作者"
        if parsed.netloc.endswith("zhihu.com"):
            tail = " ".join(path_parts[-3:])
            return f"{tail} 知乎 作者 文章".strip()
    return text


def extract_user_url_token(raw_input: str) -> str | None:
    for match in re.finditer(r"https?://[^\s]+", raw_input):
        parsed = urlparse(unquote(match.group(0).strip()))
        path_parts = [p for p in parsed.path.split("/") if p]
        if parsed.netloc.endswith("zhihu.com") and len(path_parts) >= 2 and path_parts[0] == "people":
            return path_parts[1]
    return None


def article_id_from_url(value: str) -> str:
    match = re.search(r"(?:zhuanlan\.zhihu\.com/p/|zhihu\.com/(?:p|column/p)/)(\d+)", value or "")
    return match.group(1) if match else ""


def question_answer_ids_from_url(value: str) -> tuple[str, str]:
    match = re.search(r"zhihu\.com/question/(\d+)/answer/(\d+)", value or "")
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def normalize_title(value: str) -> str:
    text = strip_html(value or "")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[-_—–|｜]*知乎$", "", text, flags=re.I)
    return text.lower()


def infer_bundle_summary(items: list[dict[str, Any]]) -> str:
    titles = [strip_html(str(item.get("title") or "")).strip() for item in items if item.get("title")]
    if not titles:
        return "AI总结内容"

    joined = " ".join(titles)
    topics: list[str] = []
    if re.search(r"大模型|LLM|Large\s*Language\s*Model", joined, re.I):
        topics.append("大模型")
    if re.search(r"VLM|MLLM|多模态|视觉语言", joined, re.I):
        topics.append("多模态")
    if re.search(r"Agent|智能体|ReAct|工具调用", joined, re.I):
        topics.append("Agent")
    if re.search(r"Attention|注意力|MHA|Multi[-\s]?Head|Multi[-\s]?Query|GQA", joined, re.I):
        topics.append("注意力机制")
    if re.search(r"Encoder|Decoder|Transformer|架构|结构|Prefix|Causal", joined, re.I):
        topics.append("架构")
    if re.search(r"训练|微调|SFT|RLHF|DPO|预训练", joined, re.I):
        topics.append("训练")
    if re.search(r"RAG|检索|向量|Embedding", joined, re.I):
        topics.append("检索增强")
    if re.search(r"LeetCode|算法|动态规划|哈希|二叉树|链表|回溯", joined, re.I):
        topics.append("算法")
    if re.search(r"面试|八股|校招|社招", joined, re.I):
        topics.append("面试")

    if topics:
        if "大模型" in topics and "架构" in topics and "注意力机制" in topics:
            return "大模型架构与注意力机制"
        if "算法" in topics and "面试" in topics:
            return "算法面试"
        return "与".join(unique_preserve_order(topics[:3]))

    cleaned_titles = [strip_title_prefix(title) for title in titles]
    prefix = common_title_prefix(cleaned_titles)
    if 4 <= len(prefix) <= 18:
        return prefix

    tokens: list[str] = []
    for title in cleaned_titles:
        tokens.extend(token for token in split_title_tokens(title) if not re.fullmatch(r"\d+", token))
    if tokens:
        return "与".join(unique_preserve_order(tokens)[:3])[:24]
    return cleaned_titles[0][:24] or "AI总结内容"


def strip_title_prefix(title: str) -> str:
    text = re.sub(r"\s+", " ", strip_html(title or "")).strip()
    return re.sub(r"^(知乎|专栏|大模型|算法专栏|AI|AIGC|LLM|Agent)[：:丨｜\-\s]+", "", text, flags=re.I).strip() or text


def common_title_prefix(values: list[str]) -> str:
    if not values:
        return ""
    prefix = values[0]
    for value in values[1:]:
        index = 0
        limit = min(len(prefix), len(value))
        while index < limit and prefix[index] == value[index]:
            index += 1
        prefix = prefix[:index]
        if not prefix:
            break
    return re.sub(r"[：:丨｜\-\s]+$", "", prefix).strip()


def split_title_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[\s:：，,。；;、+\-_/｜|（）()【】\[\]《》]+", value) if len(token) >= 2]


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def parse_ranges(spec: str | None, total: int, group_size: int) -> list[tuple[int, int, str]]:
    if total <= 0:
        return []
    if spec:
        ranges: list[tuple[int, int, str]] = []
        for raw_part in spec.split(","):
            part = raw_part.strip()
            if not part:
                continue
            if re.fullmatch(r"\d+", part):
                start = end = int(part)
            else:
                match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
                if not match:
                    raise RuntimeError(f"Invalid --ranges part: {part}")
                start, end = int(match.group(1)), int(match.group(2))
            if start < 1 or end < start:
                raise RuntimeError(f"Invalid --ranges part: {part}")
            if start > total:
                continue
            end = min(end, total)
            label = str(start) if start == end else f"{start}-{end}"
            ranges.append((start - 1, end, label))
        if not ranges:
            raise RuntimeError(f"--ranges did not select any article from {total} available results")
        return ranges
    return [
        (start, min(start + group_size, total), f"{start + 1}-{min(start + group_size, total)}")
        for start in range(0, total, group_size)
    ]


def chinese_ordinal(value: int) -> str:
    if value <= 0:
        return str(value)
    if value <= 10:
        return CHINESE_NUMERALS[value]
    if value < 20:
        return "十" + (CHINESE_NUMERALS[value - 10] if value > 10 else "")
    if value < 100:
        tens, ones = divmod(value, 10)
        return CHINESE_NUMERALS[tens] + "十" + (CHINESE_NUMERALS[ones] if ones else "")
    return str(value)


def call_zhihu_search(query: str, secret: str, count: int = MAX_COUNT_PER_OFFICIAL_QUERY) -> dict[str, Any]:
    query = query.strip()
    if not query:
        raise RuntimeError("Empty query is not allowed")
    params = urlencode({"Query": query, "Count": str(min(max(count, 1), MAX_COUNT_PER_OFFICIAL_QUERY))})
    req = Request(
        f"{API_URL}?{params}",
        headers={
            "Authorization": f"Bearer {secret}",
            "X-Request-Timestamp": str(int(time.time())),
            "Content-Type": "application/json",
            "User-Agent": "zhihu-clippings-vp-skill/official-api",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Zhihu official API HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Zhihu official API request failed: {exc}") from exc


def response_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    code = payload.get("Code", payload.get("code"))
    success = payload.get("success")
    if code not in (None, 0) and success is not True:
        raise RuntimeError(f"Zhihu official API returned error: {json.dumps(payload, ensure_ascii=False)[:1000]}")
    data = payload.get("Data") or payload.get("data") or {}
    items = data.get("Items") or data.get("items") or []
    out: list[dict[str, Any]] = []
    for raw in items:
        out.append(
            {
                "title": str(raw.get("Title") or raw.get("title") or "").strip(),
                "content_type": str(raw.get("ContentType") or raw.get("content_type") or "").strip(),
                "content_id": str(raw.get("ContentID") or raw.get("content_id") or "").strip(),
                "description": strip_html(str(raw.get("ContentText") or raw.get("content_text") or "")),
                "source": str(raw.get("Url") or raw.get("url") or "").strip(),
                "article_id": article_id_from_url(str(raw.get("Url") or raw.get("url") or "")),
                "author": str(raw.get("AuthorName") or raw.get("author_name") or "").strip(),
                "published": iso_date_from_ts(raw.get("EditTime") or raw.get("edit_time")),
                "edit_time": int(raw.get("EditTime") or raw.get("edit_time") or 0),
                "comment_count": raw.get("CommentCount"),
                "voteup_count": raw.get("VoteUpCount"),
                "authority_level": str(raw.get("AuthorityLevel") or "").strip(),
                "raw": raw,
            }
        )
    return out


class MarkdownHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.link_stack: list[str] = []
        self.in_pre = False
        self.in_code = False
        self.in_table = False
        self.in_table_cell = False
        self.current_table: list[list[str]] = []
        self.current_row: list[str] = []
        self.current_cell_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        if self.in_table and tag not in {"table", "thead", "tbody", "tr", "th", "td", "br", "a", "strong", "b", "em", "i", "code"}:
            return
        if tag == "table":
            self._block()
            self.in_table = True
            self.current_table = []
            return
        if tag == "tr" and self.in_table:
            self.current_row = []
            return
        if tag in {"th", "td"} and self.in_table:
            self.in_table_cell = True
            self.current_cell_parts = []
            return
        if tag in {"p", "div", "section", "blockquote"}:
            self._block()
            if tag == "blockquote":
                self.parts.append("> ")
        elif tag in {"h1", "h2", "h3", "h4"}:
            self._block()
            level = {"h1": "###", "h2": "###", "h3": "###", "h4": "####"}[tag]
            self.parts.append(f"{level} ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "li":
            self._block()
            self.parts.append("- ")
        elif tag == "pre":
            self._block()
            self.in_pre = True
            self.parts.append("```\n")
        elif tag == "code" and not self.in_pre:
            self.in_code = True
            self.parts.append("`")
        elif tag == "a":
            self.link_stack.append(attrs_dict.get("href", ""))
            self.parts.append("[")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "hr":
            self._block()
            self.parts.append("---")
            self._block()
        elif tag == "img":
            self._handle_image(attrs_dict)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"th", "td"} and self.in_table:
            cell = "".join(self.current_cell_parts)
            cell = re.sub(r"\s+", " ", cell).replace("|", "\\|").strip()
            self.current_row.append(cell)
            self.current_cell_parts = []
            self.in_table_cell = False
            return
        if tag == "tr" and self.in_table:
            if self.current_row:
                self.current_table.append(self.current_row)
            self.current_row = []
            return
        if tag == "table" and self.in_table:
            self.parts.append(self._render_table(self.current_table))
            self.in_table = False
            self.current_table = []
            self._block()
            return
        if tag in {"p", "div", "section", "blockquote", "li", "h1", "h2", "h3", "h4"}:
            self._block()
        elif tag == "pre":
            if not self._endswith("\n"):
                self.parts.append("\n")
            self.parts.append("```")
            self.in_pre = False
            self._block()
        elif tag == "code" and not self.in_pre and self.in_code:
            self.parts.append("`")
            self.in_code = False
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else ""
            self.parts.append(f"]({href})" if href else "]")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")

    def handle_data(self, data: str) -> None:
        if self.in_table_cell:
            self.current_cell_parts.append(data)
            return
        if self.in_pre:
            self.parts.append(data)
        else:
            text = re.sub(r"\s+", " ", data)
            if text:
                self.parts.append(text)

    def _handle_image(self, attrs: dict[str, str]) -> None:
        src = attrs.get("src", "").strip()
        alt = html.unescape(attrs.get("alt", "")).strip()
        eeimg = attrs.get("eeimg", "").strip()
        latex = alt
        if "zhihu.com/equation" in src:
            parsed = urlparse(src)
            query_tex = (parse_qs(parsed.query).get("tex") or [""])[0]
            latex = unquote(query_tex or latex).strip()
        if eeimg or "zhihu.com/equation" in src:
            if not latex:
                return
            if eeimg == "2":
                self._block()
                self.parts.append(f"$$\n{latex}\n$$")
                self._block()
            else:
                self.parts.append(f"${latex}$")
            return
        if src:
            label = alt or "image"
            self._block()
            self.parts.append(f"![{label}]({src})")
            self._block()

    def _render_table(self, rows: list[list[str]]) -> str:
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        normalized = [row + [""] * (width - len(row)) for row in rows]
        header = normalized[0]
        body = normalized[1:]
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(["---"] * width) + " |",
        ]
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)

    def markdown(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\n([ \t]*[-*] )", r"\n\1", text)
        return text.strip()

    def _block(self) -> None:
        if self.parts and not self._endswith("\n\n"):
            if self._endswith("\n"):
                self.parts.append("\n")
            else:
                self.parts.append("\n\n")

    def _endswith(self, suffix: str) -> bool:
        return "".join(self.parts[-3:]).endswith(suffix)


def html_to_markdown(value: str) -> str:
    parser = MarkdownHTMLParser()
    parser.feed(value or "")
    parser.close()
    return compact_markdown(parser.markdown())


def compact_markdown(text: str) -> str:
    text = normalize_heading_levels(text)
    text = re.sub(r"(?m)^((?:GitHub|GitHub 主页)[：:])\s*\n\n(\[[^\]\n]+\]\([^)]+\))$", r"\1 \2", text)
    text = re.sub(r"(?m)^(- .*[：:])\s*\n\n(\[[^\]\n]+\]\([^)]+\))$", r"\1 \2", text)
    text = re.sub(r"(?m)^(- .*[：:])\s*\n\n((?:https?://|[\w.-]+/)[^\n]+)$", r"\1 \2", text)
    text = re.sub(r"(?m)^(#{3,4} .+)\n\n(?=\S)", r"\1\n", text)
    text = re.sub(r"(?m)^(- .+)\n\n(?=- )", r"\1\n", text)
    text = re.sub(r"\n\n(```)", r"\n\1", text)
    text = re.sub(r"(```[^\n]*\n(?:.*?\n)*?```)\\?\n\n(?=\S)", r"\1\n", text)
    text = re.sub(r"\n\n(\$\$)", r"\n\1", text)
    text = re.sub(r"(\$\$\n(?:.*?\n)*?\$\$)\n\n(?=\S)", r"\1\n", text)
    text = re.sub(r"\n\n---\n\n", "\n\n---\n", text)
    text = add_code_fence_languages(text)
    return text


def normalize_heading_levels(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        title = match.group("title").strip()
        title = re.sub(r"^\*\*(.+)\*\*$", r"\1", title).strip()
        if re.match(r"^(方法|方案|解法)[一二三四五六七八九十]+[：:、.．]\s*", title):
            return f"##### {title}"
        if re.match(r"^[一二三四五六七八九十]+[、.．]\s*", title):
            return f"### {title}"
        if re.match(r"^\d+(?:\.\d+)+\s+", title):
            return f"#### {title}"
        if re.match(r"^\d+[、.．]\s*", title):
            return f"#### {title}"
        return f"#### {title}"

    return re.sub(r"(?m)^#{3,4}\s+(?P<title>.+)$", repl, text)


def infer_code_language(code: str) -> str:
    sample = code.strip()
    if not sample:
        return ""
    sample = re.sub(r"(?m)^\s*(?:python|text|java|javascript|typescript|json|sql|xml|cpp|bash)\s*$", "", sample).strip()
    if not sample:
        return ""
    if re.search(r"(?m)^\s*<\?xml|^\s*<dependency>|<groupId>|<artifactId>|</\w+>", sample):
        return "xml"
    if re.match(r"^[\[{]", sample) and re.search(r"[\]}]$", sample):
        return "json"
    if re.search(r"(?m)^\s*(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE TABLE|ALTER TABLE)\b", sample, re.I):
        return "sql"
    if re.search(r"(?m)^\s*(#include|int main\s*\(|std::|using namespace|template\s*<)", sample):
        return "cpp"
    if re.search(r"(?m)^\s*(async\s+function|function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=|import\s+.+\s+from\s+['\"]|export\s+|fetch\s*\(|JSON\.stringify|TextDecoder|crypto\.randomUUID|.*=>)", sample):
        if re.search(r"(?m)^\s*(interface|type\s+\w+\s*=|enum\s+\w+|:\s*(string|number|boolean|unknown|any)\b)", sample):
            return "typescript"
        return "javascript"
    if re.search(r"(?m)^\s*(@Service|@Configuration|@Bean|@RestController|public class|private |public String|List<|Set<|RestTemplate|return new|\.\w+\()", sample):
        return "java"
    if re.search(r"(?m)^\s*(def |class |async def |from \w+ import |import \w+|for .+ in .+:|while .+:|if .+:|elif .+:|else:|return\b|print\()", sample):
        return "python"
    if re.search(r"(?m)^\s*(pip |python |conda |npm |pnpm |yarn |uv |git |curl |wget |export |set |cd |ls |mkdir |cp |mv |rm |grep |find |docker |kubectl |contractguard |anycoder |repowiki |ruleforge |gitsense |batchllm |promptdiff )", sample):
        return "bash"
    if re.search(r"(?m)^\s*[\w.-]+(?:\\|/)[\w./-]+", sample) and not re.search(r"(?m)^\s*(left|right|nums|target|while|if)\b", sample):
        return "bash"
    if re.search(r"(?m)^\s*[A-Za-z_]\w*\s*=|^\s*(while|if|for)\b|^\s*# ", sample):
        return "python"
    return ""


def add_code_fence_languages(text: str) -> str:
    known = {"python", "text", "java", "javascript", "typescript", "json", "sql", "xml", "cpp", "bash", "yaml"}

    def repl(match: re.Match[str]) -> str:
        lang = match.group("lang") or ""
        code = match.group("code")
        code = code.strip("\n")
        code = re.sub(r"(?m)^\\`\\`\\`$", "", code).strip("\n")
        code = re.sub(r"(?m)^\s*(?:python|text|java|javascript|typescript|json|sql|xml|cpp|bash)\s*\n(?=\S)", "", code).strip("\n")
        inferred = infer_code_language(code)
        current = lang.strip().lower()
        final = lang.strip()
        if inferred and (not current or current in {"text", "txt", "plain"} or current in known):
            final = inferred
        return f"```{final}\n{code}\n```" if final else f"```\n{code}\n```"

    return re.sub(r"```(?P<lang>[A-Za-z0-9_+-]*)\n(?P<code>.*?)\n```", repl, text, flags=re.S)


def call_zhihu_search_with_retry(query: str, secret: str, count: int = MAX_COUNT_PER_OFFICIAL_QUERY, retries: int = 4) -> dict[str, Any]:
    last_payload: dict[str, Any] | None = None
    for attempt in range(retries + 1):
        payload = call_zhihu_search(query, secret, count)
        last_payload = payload
        if payload.get("Code") != 30001:
            return payload
        time.sleep(1.5 * (attempt + 1))
    return last_payload or {}


def cached_tikhub_payload(cache_dir: Path, user_url_token: str, limit: int) -> dict[str, Any] | None:
    path = cache_dir / "tikhub-user-articles-latest.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    params = payload.get("params") or {}
    if (
        str(params.get("user_url_token") or "") == user_url_token
        and int(params.get("limit") or 0) >= limit
        and payload.get("code") == 200
    ):
        return payload
    return None


def call_tikhub_user_articles(user_url_token: str, api_key: str, limit: int, cache_dir: Path) -> dict[str, Any]:
    cached = cached_tikhub_payload(cache_dir, user_url_token, limit)
    if cached is not None:
        return cached
    params = urlencode(
        {
            "user_url_token": user_url_token,
            "offset": "0",
            "limit": str(max(limit, 1)),
            "sort_type": "created",
        }
    )
    req = Request(
        f"{TIKHUB_USER_ARTICLES_URL}?{params}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "zhihu-clippings-vp-skill/tikhub-content",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=45) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"TikHub API HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"TikHub API request failed: {exc}") from exc
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "tikhub-user-articles-latest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def tikhub_response_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    code = payload.get("code")
    if code not in (None, 200):
        raise RuntimeError(f"TikHub API returned error: {json.dumps(payload, ensure_ascii=False)[:1000]}")
    data = payload.get("data") or {}
    rows = data.get("data") if isinstance(data, dict) else []
    if not isinstance(rows, list):
        return []
    items: list[dict[str, Any]] = []
    for raw in rows:
        author = raw.get("author") or {}
        article_id = str(raw.get("id") or article_id_from_url(str(raw.get("url") or "")))
        content_html = str(raw.get("content") or "")
        items.append(
            {
                "title": str(raw.get("title") or "").strip(),
                "source": str(raw.get("url") or f"https://zhuanlan.zhihu.com/p/{article_id}").strip(),
                "article_id": article_id,
                "author": str(author.get("name") or "").strip(),
                "published": iso_date_from_ts(raw.get("created")),
                "edit_time": int(raw.get("created") or 0),
                "comment_count": raw.get("comment_count"),
                "voteup_count": raw.get("voteup_count"),
                "content": html_to_markdown(content_html) or strip_html(str(raw.get("excerpt") or "")),
                "content_need_truncated": raw.get("content_need_truncated"),
                "raw": raw,
            }
        )
    return items


def call_tikhub_article_detail(article_id: str, api_key: str, cache_dir: Path) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"tikhub-article-detail-{article_id}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    params = urlencode({"article_id": article_id})
    req = Request(
        f"{TIKHUB_ARTICLE_DETAIL_URL}?{params}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "zhihu-clippings-vp-skill/tikhub-article-detail",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"TikHub article detail API HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"TikHub article detail API request failed: {exc}") from exc
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def tikhub_article_detail_item(payload: dict[str, Any]) -> dict[str, Any]:
    code = payload.get("code")
    if code not in (None, 200):
        raise RuntimeError(f"TikHub article detail API returned error: {json.dumps(payload, ensure_ascii=False)[:1000]}")
    raw = payload.get("data") or {}
    author = raw.get("author") or {}
    article_id = str(raw.get("id") or article_id_from_url(str(raw.get("url") or "")))
    content_html = str(raw.get("content") or "")
    return {
        "title": str(raw.get("title") or "").strip(),
        "source": f"https://zhuanlan.zhihu.com/p/{article_id}" if article_id else str(raw.get("url") or "").strip(),
        "article_id": article_id,
        "author": str(author.get("name") or "").strip(),
        "content_type": "Article",
        "content_id": "",
        "published": iso_date_from_ts(raw.get("created")),
        "edit_time": int(raw.get("created") or 0),
        "comment_count": raw.get("comment_count"),
        "voteup_count": raw.get("voteup_count"),
        "description": html_to_markdown(content_html) or strip_html(str(raw.get("excerpt") or "")),
        "official_matched": False,
        "tikhub_matched": True,
        "content_source": "tikhub_article_detail_content",
        "content_need_truncated": raw.get("content_need_truncated"),
        "raw": raw,
    }


def call_tikhub_question_answers(question_id: str, answer_ids: set[str], api_key: str, cache_dir: Path, limit: int = 20, max_pages: int = 30) -> list[dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cursor = ""
    session_id = ""
    offset = 0
    found: dict[str, dict[str, Any]] = {}
    for page in range(1, max_pages + 1):
        params = {
            "question_id": question_id,
            "limit": limit,
            "offset": offset,
            "order": "default",
            "cursor": cursor,
            "session_id": session_id,
        }
        req = Request(
            f"{TIKHUB_QUESTION_ANSWERS_URL}?{urlencode(params)}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "zhihu-clippings-vp-skill/tikhub-answer-fulltext",
            },
            method="GET",
        )
        try:
            with urlopen(req, timeout=60) as response:
                payload = json.load(response)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
            raise RuntimeError(f"TikHub question answers API HTTP {exc.code}: {body}") from exc
        except URLError as exc:
            raise RuntimeError(f"TikHub question answers API request failed: {exc}") from exc
        (cache_dir / f"tikhub-question-{question_id}-answers-page-{page}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        code = payload.get("code")
        if code not in (None, 200):
            raise RuntimeError(f"TikHub question answers API returned error: {json.dumps(payload, ensure_ascii=False)[:1000]}")
        data = payload.get("data") or {}
        rows = data.get("data") if isinstance(data, dict) else []
        if not isinstance(rows, list):
            rows = []
        for row in rows:
            target = row.get("target") if isinstance(row, dict) else None
            if not isinstance(target, dict):
                continue
            answer_id = str(target.get("id") or target.get("answer_id") or "")
            if answer_id in answer_ids:
                found[answer_id] = target
        if answer_ids.issubset(found):
            break
        paging = data.get("paging") if isinstance(data, dict) else {}
        if not isinstance(paging, dict) or paging.get("is_end"):
            break
        next_url = str(paging.get("next") or "")
        query = parse_qs(urlparse(next_url).query)
        cursor = (query.get("cursor") or [cursor])[0]
        session_id = (query.get("session_id") or [session_id])[0]
        try:
            offset = int((query.get("offset") or [offset + limit])[0])
        except ValueError:
            offset += limit
        time.sleep(0.5)
    missing = sorted(answer_ids - set(found))
    if missing:
        raise RuntimeError(f"TikHub question answers API did not return answer_id(s): {', '.join(missing)}")
    return [found[answer_id] for answer_id in answer_ids]


def tikhub_answer_item(raw: dict[str, Any], question_id: str) -> dict[str, Any]:
    author = raw.get("author") or {}
    question = raw.get("question") or {}
    answer_id = str(raw.get("id") or raw.get("answer_id") or "")
    title = str(question.get("title") or raw.get("title") or f"知乎回答 {answer_id}").strip()
    content_html = str(raw.get("content") or "")
    return {
        "title": title,
        "source": f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}",
        "article_id": answer_id,
        "author": str(author.get("name") or "").strip(),
        "content_type": "Answer",
        "content_id": answer_id,
        "published": iso_date_from_ts(raw.get("created_time")),
        "edit_time": int(raw.get("updated_time") or raw.get("created_time") or 0),
        "comment_count": raw.get("comment_count"),
        "voteup_count": raw.get("voteup_count"),
        "description": html_to_markdown(content_html) or strip_html(str(raw.get("excerpt") or "")),
        "official_matched": False,
        "tikhub_matched": True,
        "content_source": "tikhub_question_answers_content",
        "content_need_truncated": raw.get("content_need_truncated"),
        "raw": raw,
    }


def merge_tikhub_content(official_articles: list[dict[str, Any]], tikhub_articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["article_id"]: item for item in tikhub_articles if item.get("article_id")}
    by_title = {normalize_title(item.get("title", "")): item for item in tikhub_articles if item.get("title")}
    merged: list[dict[str, Any]] = []
    for official in official_articles:
        match = by_id.get(official.get("article_id", "")) or by_title.get(normalize_title(official.get("title", "")))
        item = dict(official)
        item["official_matched"] = True
        if match:
            item["tikhub_matched"] = True
            item["content_source"] = "tikhub_user_articles_content"
            item["description"] = match.get("content") or item.get("description") or ""
            item["source"] = item.get("source") or match.get("source")
            item["article_id"] = item.get("article_id") or match.get("article_id")
            item["published"] = item.get("published") or match.get("published")
            item["voteup_count"] = match.get("voteup_count", item.get("voteup_count"))
            item["comment_count"] = match.get("comment_count", item.get("comment_count"))
            item["content_need_truncated"] = match.get("content_need_truncated")
        else:
            item["tikhub_matched"] = False
            item["content_source"] = "official_api_content_text"
        merged.append(item)
    return merged


def build_tikhub_fulltext_articles(official_articles: list[dict[str, Any]], tikhub_articles: list[dict[str, Any]], author: str) -> list[dict[str, Any]]:
    by_id = {item["article_id"]: item for item in official_articles if item.get("article_id")}
    by_title = {normalize_title(item.get("title", "")): item for item in official_articles if item.get("title")}
    combined: list[dict[str, Any]] = []
    for tikhub in tikhub_articles:
        official = by_id.get(tikhub.get("article_id", "")) or by_title.get(normalize_title(tikhub.get("title", "")))
        item = dict(official or {})
        item.update(
            {
                "title": item.get("title") or tikhub.get("title"),
                "content_type": item.get("content_type") or "Article",
                "content_id": item.get("content_id") or "",
                "article_id": item.get("article_id") or tikhub.get("article_id"),
                "source": item.get("source") or tikhub.get("source"),
                "author": item.get("author") or tikhub.get("author") or author,
                "published": item.get("published") or tikhub.get("published"),
                "edit_time": tikhub.get("edit_time") or item.get("edit_time") or 0,
                "voteup_count": tikhub.get("voteup_count"),
                "comment_count": tikhub.get("comment_count"),
                "description": tikhub.get("content") or item.get("description") or "",
                "official_matched": official is not None,
                "tikhub_matched": True,
                "content_source": "tikhub_user_articles_content",
                "content_need_truncated": tikhub.get("content_need_truncated"),
            }
        )
        combined.append(item)
    combined.sort(key=lambda item: item.get("edit_time") or 0, reverse=True)
    return combined


def infer_author(items: list[dict[str, Any]], user_author: str | None) -> str:
    if user_author:
        return user_author.strip()
    authors = [item["author"] for item in items if item.get("author")]
    if not authors:
        raise RuntimeError("Could not infer an author from official API results. Pass --author explicitly.")
    counts = Counter(authors)
    return counts.most_common(1)[0][0]


def author_candidate_from_input(raw_input: str) -> str | None:
    text = re.sub(r"https?://\S+", " ", raw_input)
    matches = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
    stopwords = {
        "知乎",
        "文章",
        "作者",
        "月之暗面",
        "工程师",
        "居住地",
        "现居香港",
        "曾在北京",
        "北京",
        "香港",
        "专栏",
        "回答",
        "标题",
        "链接",
    }
    for match in matches:
        if match not in stopwords and not any(word in match for word in ["工程", "居住", "文章", "作者"]):
            return match
    return None


def build_author_queries(raw_input: str, normalized: str, author: str, extra: list[str]) -> list[str]:
    candidates = [
        normalized,
        author,
        f"{author} 文章",
        f"{author} 知乎",
        f"{author} 专栏",
        f"{author} 月之暗面",
        f"{author} Kimi",
        raw_input.strip(),
        *extra,
    ]
    seen: set[str] = set()
    queries: list[str] = []
    for query in candidates:
        query = query.strip()
        if query and query not in seen:
            seen.add(query)
            queries.append(query)
    return queries


def read_extra_query_file(path: str | None) -> list[str]:
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        raise RuntimeError(f"--extra-query-file does not exist: {p}")
    return [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def discover_titles(source: str | None) -> list[str]:
    if not source:
        return []
    text = source
    path = Path(source)
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
    text = strip_html(text)
    candidates: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.replace("\ufeff", "").strip()
        if not line:
            continue
        line = re.sub(r"^(赞同|评论|喜欢|分享|阅读全文|他的文章|动态|回答|视频|提问|文章|专栏|想法|收藏|划线)\s*\d*\s*$", "", line).strip()
        line = re.sub(r"^(何宇峰|月之暗面 Kimi AI Agent 工程师)\s*$", "", line).strip()
        if not line:
            continue
        if len(line) < 8 or len(line) > 100:
            continue
        if any(marker in line for marker in ["赞同", "添加评论", "系统繁忙", "重新加载"]):
            continue
        if re.search(r"[，。！？:：、A-Za-z0-9]", line) and not line.startswith(("http://", "https://")):
            candidates.append(line)
    seen: set[str] = set()
    titles: list[str] = []
    for title in candidates:
        title = re.sub(r"\s+", " ", title)
        if title not in seen:
            seen.add(title)
            titles.append(title)
    return titles


def collect_author_articles(raw_input: str, secret: str, target_author: str | None, extra_queries: list[str], cache_dir: Path, official_delay: float, initial_articles: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    normalized = normalize_input(raw_input)
    first_payload = call_zhihu_search_with_retry(normalized, secret)
    first_items = response_items(first_payload)
    author = target_author or author_candidate_from_input(raw_input) or infer_author(first_items, None)
    queries = build_author_queries(raw_input, normalized, author, extra_queries)
    if initial_articles:
        title_queries = [str(item.get("title") or "").strip() for item in initial_articles]
        article_ids = [str(item.get("article_id") or "").strip() for item in initial_articles]
        queries = build_author_queries(raw_input, normalized, author, [*extra_queries, *title_queries, *article_ids])

    raw_payloads: list[dict[str, Any]] = [{"query": normalized, "payload": first_payload}]
    by_id: dict[str, dict[str, Any]] = {}
    for item in first_items:
        if item.get("author") == author and item.get("content_type") == "Article":
            by_id[item.get("content_id") or item.get("source")] = item

    for query in queries:
        if query == normalized:
            continue
        if official_delay > 0:
            time.sleep(official_delay)
        payload = call_zhihu_search_with_retry(query, secret)
        raw_payloads.append({"query": query, "payload": payload})
        for item in response_items(payload):
            if item.get("author") == author and item.get("content_type") == "Article":
                by_id[item.get("content_id") or item.get("source")] = item

    articles = list(by_id.values())
    articles.sort(key=lambda item: item.get("edit_time") or 0, reverse=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "last-official-author-search.json").write_text(
        json.dumps(
            {
                "input": raw_input,
                "normalized_input": normalized,
                "target_author": author,
                "queries": queries,
                "payloads": raw_payloads,
                "article_count": len(articles),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return author, queries, articles


def render_bundle(
    raw_input: str,
    author: str,
    queries: list[str],
    items: list[dict[str, Any]],
    start: int,
    total: int,
    content_provider: str,
    range_label: str,
    summary: str,
) -> str:
    fulltext = content_provider == "tikhub"
    title = f"知乎_{author}_{summary}_知乎文章搜索剪藏_{today()}_{range_label}"
    source = "zhihu official api + tikhub" if fulltext else API_URL
    description = (
        f"知乎官方 API 定位，TikHub 补全文，共 {total} 条，本文件收录第 {range_label} 篇。"
        if fulltext
        else f"知乎官方 API 搜索命中的作者文章候选，共 {total} 条，本文件收录第 {range_label} 篇。"
    )
    tags = ['  - "clippings"', '  - "zhihu"', f"  - {yaml_quote(author)}"]
    frontmatter = [
        "---",
        f"title: {yaml_quote(title)}",
        f"source: {yaml_quote(source)}",
        "author:",
        f"  - {yaml_quote(author)}",
        "published:",
        f"created: {today()}",
        f"range: {yaml_quote(range_label)}",
        f"description: {yaml_quote(description)}",
        "tags:",
        *tags,
        "---",
    ]
    sections: list[str] = []
    for index, item in enumerate(items, start=start + 1):
        article_number = f"0x{index:02d}"
        section = [
            f"## {article_number}. {item.get('title') or '未命名知乎文章'}",
        ]
        section.extend(["", item.get("description") or ""])
        sections.append("\n".join(section).strip())
    return "\n".join(frontmatter + sections) + "\n"


def extract_headings(markdown: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        match = re.match(r"^(#{2,6})\s+(.+)$", line)
        if match:
            headings.append(
                {
                    "index": len(headings),
                    "line": line_no,
                    "level": len(match.group(1)),
                    "title": match.group(2).strip(),
                }
            )
    return headings


def apply_heading_review(markdown: str, adjustments: dict[int, int]) -> str:
    heading_index = 0
    out: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{2,6})\s+(.+)$", line)
        if match:
            new_level = adjustments.get(heading_index)
            if new_level is not None:
                new_level = min(max(int(new_level), 2), 6)
                line = f"{'#' * new_level} {match.group(2).strip()}"
            heading_index += 1
        out.append(line)
    return "\n".join(out) + "\n"


def review_heading_levels_with_llm(markdown: str, model: str, api_key: str | None, base_url: str | None) -> str:
    api_key = api_key or os.environ.get("OPENAI_API_KEY") or read_user_env("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("--llm-heading-review requires OPENAI_API_KEY or --llm-api-key")
    headings = extract_headings(markdown)
    if not headings:
        return markdown
    prompt = {
        "task": "Review Markdown heading levels only. Return JSON array of objects with index and level for headings that should change. Do not rewrite titles.",
        "rules": [
            "Article titles like 一、文章名 should normally be level 2.",
            "Only major Chinese sections like 二、哈希表专题 should normally be level 3.",
            "Unnumbered subheads, Arabic single-number headings like 1. 两数之和, and decimal headings like 1.1 哈希表模板 should normally be level 4.",
            "Implementation variants like 方法一：... should normally be level 5.",
            "Return [] if no changes are needed.",
        ],
        "headings": headings,
    }
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a strict Markdown outline reviewer. Output JSON only."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            "temperature": 0,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    root = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    req = Request(
        f"{root}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "zhihu-clippings-vp-heading-review",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=90) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"LLM heading review HTTP {exc.code}: {detail}") from exc
    content = payload["choices"][0]["message"]["content"].strip()
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.S)
    changes = json.loads(content)
    adjustments: dict[int, int] = {}
    for item in changes:
        if isinstance(item, dict) and "index" in item and "level" in item:
            adjustments[int(item["index"])] = int(item["level"])
    return apply_heading_review(markdown, adjustments)


def write_bundles(raw_input: str, author: str, queries: list[str], articles: list[dict[str, Any]], output_dir: Path, group_size: int, basename: str | None, dry_run: bool, content_provider: str, ranges_spec: str | None, filename_template: str, llm_heading_review: bool = False, llm_model: str = "gpt-4.1-mini", llm_api_key: str | None = None, llm_base_url: str | None = None) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename_author = safe_filename_part(basename or author, fallback="作者")
    paths: list[Path] = []
    for start, end, range_label in parse_ranges(ranges_spec, len(articles), group_size):
        group = articles[start:end]
        summary = infer_bundle_summary(group)
        filename = filename_template.format(
            author=filename_author,
            summary=safe_filename_part(summary, fallback="AI总结内容"),
            date=today(),
            range=range_label,
        )
        filename = safe_text(filename, fallback=f"知乎_{filename_author}_{safe_filename_part(summary, fallback='AI总结内容')}_知乎文章搜索剪藏_{today()}_{range_label}.md")
        if not filename.lower().endswith(".md"):
            filename += ".md"
        path = output_dir / filename
        paths.append(path)
        if not dry_run:
            markdown = render_bundle(raw_input, author, queries, group, start, len(articles), content_provider, range_label, summary)
            if llm_heading_review:
                markdown = review_heading_levels_with_llm(markdown, llm_model, llm_api_key, llm_base_url)
            path.write_text(
                markdown,
                encoding="utf-8",
                newline="\n",
            )
    return paths


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise RuntimeError("--count must be positive")
    if args.group_size <= 0:
        raise RuntimeError("--group-size must be positive")
    secret = get_secret(args.access_secret)
    user_url_token = args.user_url_token or extract_user_url_token(args.input)
    url_question_id, url_answer_id = question_answer_ids_from_url(args.input)
    question_id = args.question_id or url_question_id
    answer_ids = [*args.answer_id]
    if url_answer_id and url_answer_id not in answer_ids:
        answer_ids.append(url_answer_id)
    resolved_provider = args.content_provider
    tikhub_key = get_tikhub_key(args.tikhub_api_key, required=resolved_provider == "tikhub")
    if args.article_id or answer_ids:
        resolved_provider = "tikhub"
    if resolved_provider == "auto":
        resolved_provider = "tikhub" if tikhub_key and user_url_token else "official"
    tikhub_items: list[dict[str, Any]] = []
    if answer_ids:
        if not question_id:
            raise RuntimeError("TikHub answer mode needs --question-id or an input URL like https://www.zhihu.com/question/<id>/answer/<id>.")
        if not tikhub_key:
            raise RuntimeError("TikHub answer mode needs TIKHUB_API_KEY or --tikhub-api-key.")
        raw_answers = call_tikhub_question_answers(question_id, set(answer_ids), tikhub_key, Path(args.cache_dir))
        tikhub_items = [tikhub_answer_item(raw, question_id) for raw in raw_answers]
        author = args.author or next((item.get("author") for item in tikhub_items if item.get("author")), "") or "zhihu-author"
        queries = [args.input, question_id, *answer_ids]
        articles = tikhub_items[: args.count]
        if not articles:
            raise RuntimeError("No TikHub answer fulltext results found.")
        for item in articles:
            if item.get("content_need_truncated") is True:
                raise RuntimeError(f"TikHub returned truncated content for answer_id {item.get('article_id')}.")
        paths = write_bundles(
            args.input,
            author,
            queries,
            articles,
            Path(args.output_dir),
            args.group_size,
            args.author,
            args.dry_run,
            resolved_provider,
            args.ranges,
            args.filename_template,
            args.llm_heading_review,
            args.llm_model,
            args.llm_api_key,
            args.llm_base_url,
        )
        print(f"input={args.input}")
        print(f"target_author={author}")
        print(f"answer_results={len(articles)} content_provider={resolved_provider} output_dir={Path(args.output_dir)}")
        for path in paths:
            print(("DRY-RUN " if args.dry_run else "") + str(path))
        return 0
    if args.article_id:
        if not tikhub_key:
            raise RuntimeError("TikHub article detail mode needs TIKHUB_API_KEY or --tikhub-api-key.")
        tikhub_items = [
            tikhub_article_detail_item(call_tikhub_article_detail(article_id, tikhub_key, Path(args.cache_dir)))
            for article_id in args.article_id
        ]
        author = args.author or next((item.get("author") for item in tikhub_items if item.get("author")), "") or "zhihu-author"
        queries = [args.input, *args.article_id]
        articles = tikhub_items[: args.count]
        if not articles:
            raise RuntimeError("No TikHub article detail results found.")
        for item in articles:
            if item.get("content_need_truncated") is True:
                raise RuntimeError(f"TikHub returned truncated content for article_id {item.get('article_id')}.")
        paths = write_bundles(
            args.input,
            author,
            queries,
            articles,
            Path(args.output_dir),
            args.group_size,
            None,
            args.dry_run,
            resolved_provider,
            args.ranges,
            args.filename_template,
            args.llm_heading_review,
            args.llm_model,
            args.llm_api_key,
            args.llm_base_url,
        )
        print(f"input={args.input}")
        print(f"target_author={author}")
        print(f"article_results={len(articles)} content_provider={resolved_provider} output_dir={Path(args.output_dir)}")
        for path in paths:
            print(("DRY-RUN " if args.dry_run else "") + str(path))
        return 0

    if resolved_provider == "tikhub":
        if not user_url_token:
            raise RuntimeError("TikHub content provider needs a Zhihu people URL token. Pass --user-url-token or include a people URL in input.")
        if not tikhub_key:
            raise RuntimeError("TikHub content provider needs TIKHUB_API_KEY or --tikhub-api-key.")
        tikhub_payload = call_tikhub_user_articles(
            user_url_token,
            tikhub_key,
            args.tikhub_limit or args.count,
            Path(args.cache_dir),
        )
        tikhub_items = tikhub_response_items(tikhub_payload)
    author, queries, articles = collect_author_articles(
        args.input,
        secret,
        args.author,
        [*discover_titles(args.title_source), *args.extra_query, *read_extra_query_file(args.extra_query_file)],
        Path(args.cache_dir),
        args.official_delay,
        tikhub_items if resolved_provider == "tikhub" else None,
    )
    articles = articles[: args.count]
    if not articles:
        raise RuntimeError(
            f"No Article results found for inferred author {author}. Try --author explicitly or add --extra-query."
        )
    if resolved_provider == "tikhub":
        articles = build_tikhub_fulltext_articles(articles, tikhub_items, author)[: args.count]
    paths = write_bundles(
        args.input,
        author,
        queries,
        articles,
        Path(args.output_dir),
        args.group_size,
        None,
        args.dry_run,
        resolved_provider,
        args.ranges,
        args.filename_template,
        args.llm_heading_review,
        args.llm_model,
        args.llm_api_key,
        args.llm_base_url,
    )
    print(f"input={args.input}")
    print(f"target_author={author}")
    print(f"article_results={len(articles)} group_size={args.group_size} content_provider={resolved_provider} output_dir={Path(args.output_dir)}")
    if resolved_provider == "tikhub":
        print(f"user_url_token={user_url_token}")
        print(f"tikhub_matched={sum(1 for item in articles if item.get('tikhub_matched'))}/{len(articles)}")
    print("queries=" + json.dumps(queries, ensure_ascii=False))
    for path in paths:
        print(("DRY-RUN " if args.dry_run else "") + str(path))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
