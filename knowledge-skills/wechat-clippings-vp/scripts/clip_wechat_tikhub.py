#!/usr/bin/env python
"""Clip WeChat Official Account articles through TikHub into Markdown bundles."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows fallback
    winreg = None

DEFAULT_OUTPUT_DIR = Path(r"E:\LLM_wiki\LLM_wiki\01.raw\01.Inbox")
DEFAULT_CACHE_DIR = Path.cwd() / ".llmwiki-cache" / "wechat-clippings-vp"
TIKHUB_BASE_URL = "https://api.tikhub.io"
DEFAULT_ACCOUNT_SEARCH_PATH = "/api/v1/wechat_mp/web/fetch_search_official_account"
DEFAULT_ARTICLE_SEARCH_PATH = "/api/v1/wechat_mp/web/fetch_search_article"
DEFAULT_ARTICLE_LIST_PATH = "/api/v1/wechat_mp/web/fetch_mp_article_list"
DEFAULT_ARTICLE_DETAIL_PATHS = (
    "/api/v1/wechat_mp/web/fetch_mp_article_detail_html",
    "/api/v1/wechat_mp/web/fetch_mp_article_detail_json",
)
CHINESE_NUMERALS = "零一二三四五六七八九十"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class Article:
    title: str
    author: str
    url: str
    published: str = ""
    content: str = ""
    source_api: str = ""
    raw: dict[str, Any] | None = None
    source_table_count: int = 0
    markdown_table_count: int = 0


class BodyHTMLParser(HTMLParser):
    BLOCK_TAGS = {"p", "div", "section", "article", "blockquote", "pre", "ul", "ol", "li"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.link_stack: list[str] = []
        self.list_depth = 0
        self.in_pre = False
        self.skip_depth = 0
        self.table_depth = 0
        self.table_rows: list[list[str]] = []
        self.table_row: list[str] = []
        self.table_cell_parts: list[str] = []
        self.table_cell_is_header = False
        self.table_cell_had_pre = False
        self.table_had_pre = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag in {"script", "style", "svg"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "table":
            if self.table_depth == 0:
                self._newline()
                self.table_rows = []
                self.table_row = []
                self.table_cell_parts = []
                self.table_had_pre = False
            self.table_depth += 1
            return
        if self.table_depth:
            if tag == "tr" and self.table_depth == 1:
                self.table_row = []
            elif tag in {"td", "th"} and self.table_depth == 1:
                self.table_cell_parts = []
                self.table_cell_is_header = tag == "th"
                self.table_cell_had_pre = False
            elif tag == "br":
                self._append("\n")
            elif tag in {"strong", "b"}:
                self._append("**")
            elif tag in {"em", "i"}:
                self._append("*")
            elif tag == "a":
                href = attrs_dict.get("href", "").strip()
                self.link_stack.append(href)
                self._append("[")
            elif tag == "img":
                src = attrs_dict.get("data-src") or attrs_dict.get("src") or attrs_dict.get("data-original")
                alt = attrs_dict.get("alt") or attrs_dict.get("title") or "image"
                if src:
                    self._append(f"![{clean_inline(alt)}]({src.strip()})")
            elif tag == "pre":
                self.in_pre = True
                self.table_cell_had_pre = True
                self.table_had_pre = True
            return
        if tag in self.BLOCK_TAGS:
            self._newline()
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = max(3, min(5, int(tag[1]) + 1))
            self._newline()
            self.parts.append("#" * level + " ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "a":
            href = attrs_dict.get("href", "").strip()
            self.link_stack.append(href)
            self.parts.append("[")
        elif tag == "img":
            src = attrs_dict.get("data-src") or attrs_dict.get("src") or attrs_dict.get("data-original")
            alt = attrs_dict.get("alt") or attrs_dict.get("title") or "image"
            if src:
                self._newline()
                self.parts.append(f"![{clean_inline(alt)}]({src.strip()})")
                self._newline()
        elif tag == "li":
            self.parts.append("- ")
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
        elif tag == "pre":
            self.in_pre = True
            self._newline()
            self.parts.append("```text\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "svg"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "table" and self.table_depth:
            self.table_depth -= 1
            if self.table_depth == 0:
                rendered = self.render_table()
                if rendered:
                    self._newline()
                    self.parts.append(rendered)
                    self._newline()
            return
        if self.table_depth:
            if tag in {"strong", "b"}:
                self._append("**")
            elif tag in {"em", "i"}:
                self._append("*")
            elif tag == "a":
                href = self.link_stack.pop() if self.link_stack else ""
                self._append(f"]({href})" if href else "]")
            elif tag == "pre":
                self.in_pre = False
            elif tag in {"td", "th"} and self.table_depth == 1:
                cell = self.normalize_table_cell("".join(self.table_cell_parts))
                if cell or self.table_cell_had_pre or self.table_cell_is_header:
                    self.table_row.append(cell)
                self.table_cell_parts = []
                self.table_cell_is_header = False
                self.table_cell_had_pre = False
            elif tag == "tr" and self.table_depth == 1:
                if any(cell.strip() for cell in self.table_row):
                    self.table_rows.append(self.table_row)
                self.table_row = []
            return
        if tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else ""
            self.parts.append(f"]({href})" if href else "]")
        elif tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)
            self._newline()
        elif tag == "pre":
            self.in_pre = False
            if self.parts and not str(self.parts[-1]).endswith("\n"):
                self.parts.append("\n")
            self.parts.append("```\n")
        elif tag in self.BLOCK_TAGS or tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        self._append(data if self.in_pre else re.sub(r"\s+", " ", data))

    def markdown(self) -> str:
        text = html.unescape("".join(self.parts))
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\n(- .+)\n\n(?=- )", r"\n\1\n", text)
        return text.strip()

    def _newline(self) -> None:
        if self.parts and not "".join(self.parts[-2:]).endswith("\n"):
            self.parts.append("\n")

    def _append(self, value: str) -> None:
        if self.table_depth:
            self.table_cell_parts.append(value)
        else:
            self.parts.append(value)

    def normalize_table_cell(self, value: str) -> str:
        text = html.unescape(value or "").replace("\xa0", " ")
        if not self.in_pre:
            text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def render_table(self) -> str:
        rows = [row for row in self.table_rows if any(cell.strip() for cell in row)]
        if not rows:
            return ""
        max_cols = max(len(row) for row in rows)
        if max_cols >= 2 and len(rows) >= 2:
            return self.render_markdown_table(rows, max_cols)
        single_text = "\n".join(cell for row in rows for cell in row if cell.strip()).strip()
        return self.render_single_cell_table(single_text)

    def render_markdown_table(self, rows: list[list[str]], max_cols: int) -> str:
        normalized = [row + [""] * (max_cols - len(row)) for row in rows]
        header = [self.escape_table_cell(cell) for cell in normalized[0]]
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join([":---"] * max_cols) + " |",
        ]
        for row in normalized[1:]:
            lines.append("| " + " | ".join(self.escape_table_cell(cell) for cell in row) + " |")
        return "\n".join(lines)

    def render_single_cell_table(self, text: str) -> str:
        if not text:
            return ""
        lang = infer_fence_language(text)
        if self.table_had_pre or lang != "text":
            return f"```{lang}\n{text.strip()}\n```"
        return "> " + re.sub(r"\n+", "\n> ", text.strip())

    def escape_table_cell(self, value: str) -> str:
        text = re.sub(r"\s+", " ", value or "").strip()
        return text.replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clip WeChat Official Account articles through TikHub.")
    parser.add_argument("input", help="Official account name, article URL, article title, screenshot OCR text, or mixed clue.")
    parser.add_argument("-n", "--count", type=int, default=5, help="Maximum article candidates to keep.")
    parser.add_argument("--author", default=None, help="Known account/author name.")
    parser.add_argument("--title-source", default=None, help="UTF-8 OCR/page text file or raw text used to discover titles.")
    parser.add_argument("--extra-query", action="append", default=[], help="Additional title/account query. Can be repeated.")
    parser.add_argument("--extra-query-file", default=None, help="UTF-8 text file with one additional query per line.")
    parser.add_argument("--article-url", action="append", default=[], help="Specific mp.weixin.qq.com URL. Can be repeated.")
    parser.add_argument("--account-id", default=None, help="Known account identifier from TikHub response.")
    parser.add_argument("--group-size", "--batch-size", dest="group_size", type=int, default=5, help="Articles per Markdown bundle.")
    parser.add_argument("--ranges", default=None, help='Custom 1-based article ranges, for example "1", "2-3", or "1-4".')
    parser.add_argument("--filename-template", default="微信_{author}_{summary}_公众号文章剪藏_{date}_{range}.md")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for Markdown bundle files.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Directory for raw API response cache.")
    parser.add_argument("--tikhub-api-key", default=None, help="TikHub API key. Defaults to TIKHUB_API_KEY.")
    parser.add_argument("--base-url", default=TIKHUB_BASE_URL, help="TikHub base URL.")
    parser.add_argument("--account-search-path", default=DEFAULT_ACCOUNT_SEARCH_PATH)
    parser.add_argument("--article-search-path", default=DEFAULT_ARTICLE_SEARCH_PATH)
    parser.add_argument("--article-list-path", default=DEFAULT_ARTICLE_LIST_PATH)
    parser.add_argument("--article-detail-path", action="append", default=list(DEFAULT_ARTICLE_DETAIL_PATHS))
    parser.add_argument(
        "--format-mode",
        choices=["plain", "readable"],
        default="plain",
        help="Markdown formatting mode. plain preserves clipping text; readable adds conservative emphasis and list/table structure.",
    )
    parser.add_argument("--retry", type=int, default=4, help="Retries for TikHub calls.")
    parser.add_argument("--retry-delay", type=float, default=1.5, help="Initial retry delay in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print summary without writing Markdown.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_args(args)
    key = get_tikhub_key(args.tikhub_api_key)
    output_dir = Path(args.output_dir)
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    explicit_urls = list(args.article_url) + extract_wechat_urls(args.input)
    title_queries = collect_queries(args)
    articles: list[Article] = []

    for url in explicit_urls:
        articles.append(Article(title="", author=args.author or "微信公众号", url=url, source_api="direct-url"))

    if not articles:
        articles.extend(fetch_candidates(args, key, title_queries, cache_dir))

    articles = dedupe_articles(articles)[: args.count]
    if not articles:
        raise RuntimeError("No WeChat article candidates were found. Add a direct article URL, --title-source, or --extra-query.")

    enriched: list[Article] = []
    for article in articles:
        enriched.append(fetch_article_detail(args, key, article, cache_dir))

    if args.dry_run:
        for index, article in enumerate(enriched, 1):
            print(f"{index}. {article.title or '(untitled)'} | {article.author} | {article.url}")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    written = write_bundles(enriched, args, output_dir)
    for path in written:
        print(path)
    return 0


def get_tikhub_key(explicit: str | None) -> str:
    key = explicit or os.environ.get("TIKHUB_API_KEY") or read_user_env("TIKHUB_API_KEY")
    if not key:
        raise RuntimeError("TIKHUB_API_KEY is not set. Pass --tikhub-api-key or set the user environment variable.")
    key = key.strip()
    if key.upper().startswith("API:"):
        key = key.split(":", 1)[1].strip()
    return key


def read_user_env(name: str) -> str | None:
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
    except OSError:
        return None


def validate_args(args: argparse.Namespace) -> None:
    if args.count < 1:
        raise RuntimeError("--count must be >= 1")
    if args.group_size < 1:
        raise RuntimeError("--group-size must be >= 1")
    if args.retry < 1:
        raise RuntimeError("--retry must be >= 1")
    if args.retry_delay < 0:
        raise RuntimeError("--retry-delay must be >= 0")
    parsed = urlparse(args.base_url)
    if parsed.scheme != "https" or parsed.netloc != "api.tikhub.io":
        raise RuntimeError("--base-url is restricted to https://api.tikhub.io to avoid leaking TIKHUB_API_KEY")


def collect_queries(args: argparse.Namespace) -> list[str]:
    queries = [args.input]
    queries.extend(args.extra_query)
    if args.extra_query_file:
        queries.extend(read_lines_or_text(args.extra_query_file))
    if args.title_source:
        source_text = "\n".join(read_lines_or_text(args.title_source))
        queries.extend(discover_title_queries(source_text))
    return unique([clean_inline(q) for q in queries if clean_inline(q)])


def read_lines_or_text(value: str) -> list[str]:
    path = Path(value)
    if path.exists():
        return [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    return [line.strip() for line in value.splitlines() if line.strip()]


def discover_title_queries(text: str) -> list[str]:
    candidates: list[str] = []
    for line in text.splitlines():
        line = clean_inline(line)
        if 8 <= len(line) <= 80 and not re.search(r"(赞|阅读|转发|评论|小时前|\d{4}-\d{2}-\d{2})$", line):
            candidates.append(line)
    return candidates[:20]


def fetch_candidates(args: argparse.Namespace, key: str, queries: list[str], cache_dir: Path) -> list[Article]:
    articles: list[Article] = []
    account_ids = [args.account_id] if args.account_id else []
    account_queries = [args.author] if args.author else []
    if not account_queries and not extract_wechat_urls(args.input):
        account_queries.append(args.input)
    for account_query in unique([q for q in account_queries if q]):
        if not account_ids:
            try:
                account_ids.extend(search_accounts(args, key, account_query, cache_dir))
            except RuntimeError as exc:
                print(f"Warning: account search failed for {account_query!r}: {exc}", file=sys.stderr)

    for account_id in account_ids[:3]:
        account_articles = fetch_account_articles(args, key, account_id, cache_dir, queries)
        articles.extend(rank_articles(account_articles, queries))

    for query in queries:
        try:
            data = tikhub_get(args, key, args.article_search_path, {"keyword": query, "offset": 0, "sort_type": "_0"}, cache_dir)
        except RuntimeError as exc:
            print(f"Warning: article search failed for {query!r}: {exc}", file=sys.stderr)
            continue
        articles.extend(rank_articles(extract_articles(data, args.author, args.article_search_path), queries))
        if len(articles) >= args.count:
            break
    return articles


def fetch_account_articles(
    args: argparse.Namespace,
    key: str,
    account_id: str,
    cache_dir: Path,
    queries: list[str],
) -> list[Article]:
    articles: list[Article] = []
    offset: Any = ""
    seen_offsets: set[str] = set()
    for _ in range(30):
        offset_key = json.dumps(offset, ensure_ascii=False, sort_keys=True) if isinstance(offset, dict) else str(offset)
        if offset_key in seen_offsets:
            break
        seen_offsets.add(offset_key)
        data = tikhub_get(args, key, args.article_list_path, {"ghid": account_id, "offset": offset}, cache_dir)
        if not has_structured_article_data(data):
            break
        articles.extend(extract_articles(data, args.author, args.article_list_path))
        if len(rank_articles(articles, queries)) >= args.count:
            break
        offset = next_list_offset(data)
        if not offset:
            break
        time.sleep(max(args.retry_delay, 0.8))
    return articles


def search_accounts(args: argparse.Namespace, key: str, query: str, cache_dir: Path) -> list[str]:
    data = tikhub_get(args, key, args.account_search_path, {"keyword": query, "offset": 0, "sort_type": "_0"}, cache_dir)
    account_ids: list[str] = []
    for item in iter_dicts(data):
        jump_info = item.get("jumpInfo")
        if isinstance(jump_info, dict):
            value = jump_info.get("userName")
            if isinstance(value, str) and value.startswith("gh_"):
                account_ids.append(value.strip())
                continue
        for key_name in ("ghid", "userName", "username", "account_id", "fakeid", "biz", "wechat_id"):
            value = item.get(key_name)
            if isinstance(value, str) and value.strip():
                account_ids.append(value.strip())
                break
    return unique(account_ids)


def has_structured_article_data(data: Any) -> bool:
    payload = data.get("data") if isinstance(data, dict) else data
    if isinstance(payload, list):
        return True
    if isinstance(payload, dict):
        return any(isinstance(payload.get(key), list) for key in ("items", "list", "articles", "app_msg_list"))
    return False


def fetch_article_detail(args: argparse.Namespace, key: str, article: Article, cache_dir: Path) -> Article:
    if article.content and not article.url:
        return article
    params = detail_params(article)
    last_error: Exception | None = None
    for path in args.article_detail_path:
        try:
            data = tikhub_get(args, key, path, params, cache_dir)
            detail = extract_detail(data, article)
            detail.source_api = path
            return detail
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        print(f"Warning: detail fetch failed for {article.url or article.title}: {last_error}", file=sys.stderr)
    article.content = article.content or ""
    return article


def detail_params(article: Article) -> dict[str, str]:
    params: dict[str, str] = {}
    if article.url:
        params.update({"url": article.url, "article_url": article.url})
        parsed = urlparse(article.url)
        query = parsed.query
        if "__biz=" in query:
            params["__biz"] = re.search(r"__biz=([^&]+)", query).group(1)  # type: ignore[union-attr]
        if "mid=" in query:
            params["mid"] = re.search(r"mid=([^&]+)", query).group(1)  # type: ignore[union-attr]
        if "idx=" in query:
            params["idx"] = re.search(r"idx=([^&]+)", query).group(1)  # type: ignore[union-attr]
        if "sn=" in query:
            params["sn"] = re.search(r"sn=([^&]+)", query).group(1)  # type: ignore[union-attr]
    if article.raw:
        for key in ("__biz", "mid", "idx", "sn", "appmsgid", "itemidx", "aid"):
            value = article.raw.get(key)
            if value not in (None, ""):
                params[key] = str(value)
    return params


def tikhub_get(args: argparse.Namespace, key: str, path: str, params: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    url = args.base_url.rstrip("/") + "/" + path.lstrip("/")
    clean_params = {k: v for k, v in params.items() if v not in (None, "")}
    full_url = url + ("?" + urlencode(clean_params) if clean_params else "")
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    last_error: Exception | None = None
    search_path = path in {args.account_search_path, args.article_search_path}
    for attempt in range(1, args.retry + 1):
        try:
            request = Request(full_url, headers=headers)
            with urlopen(request, timeout=90) as response:
                raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            cache_response(cache_dir, path, clean_params, data)
            return data
        except HTTPError as exc:
            last_error = exc
            if exc.code in {401, 403, 404, 422} or (exc.code == 400 and not search_path):
                break
            if attempt < args.retry:
                time.sleep(args.retry_delay * attempt + random.uniform(0.2, 1.2))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < args.retry:
                time.sleep(args.retry_delay * attempt + random.uniform(0.2, 1.2))
    raise RuntimeError(f"TikHub request failed for {path}: {last_error}")


def cache_response(cache_dir: Path, path: str, params: dict[str, Any], data: dict[str, Any]) -> None:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = safe_filename_part(path.strip("/").replace("/", "_"), "tikhub")
    query = safe_filename_part("_".join(str(v) for v in params.values())[:60], "query")
    target = cache_dir / f"{stamp}_{stem}_{query}.json"
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_articles(data: Any, default_author: str | None, source_api: str) -> list[Article]:
    articles: list[Article] = []
    for item in iter_dicts(data):
        url = first_str(item, ["url", "article_url", "link", "content_url", "appmsg_url", "ContentUrl", "SourceUrl"])
        title = first_str(item, ["title", "Title", "text_title", "appmsg_title", "name", "digest", "Digest"])
        if not url and not title:
            continue
        if url and "mp.weixin.qq.com" not in url:
            continue
        author = first_str(item, ["author", "nickname", "NickName", "account_name", "source", "user_name"]) or default_author or "微信公众号"
        content = first_str(item, ["content", "html", "article_content", "content_html", "text", "ori_content", "Content"])
        articles.append(
            Article(
                title=clean_inline(title) or "未命名公众号文章",
                author=clean_inline(author),
                url=url,
                published=parse_date(first_present(item, ["publish_time", "create_time", "datetime", "date", "time", "send_time"])),
                content=html_to_markdown(content) if looks_like_html(content) else clean_markdown(content),
                source_api=source_api,
                raw=item,
            )
        )
    return articles


def extract_detail(data: Any, fallback: Article) -> Article:
    best: dict[str, Any] = {}
    for item in iter_dicts(data):
        if any(key in item for key in ("content", "html", "article_content", "content_html", "title")):
            best = item
            break
    title = clean_inline(first_str(best, ["title", "appmsg_title", "name"]) or fallback.title or "????????")
    author = clean_inline(first_str(best, ["author", "nickname", "account_name", "username", "source"]) or fallback.author or "?????")
    url = first_str(best, ["url", "article_url", "link", "content_url", "appmsg_url"]) or fallback.url
    raw_content = select_detail_content(best, fallback.content)
    if looks_like_html(raw_content):
        content = html_to_markdown(raw_content)
    elif looks_like_structured_markdown(raw_content):
        content = clean_wechat_chrome(clean_markdown(raw_content))
        content = repair_plain_text_headings(content)
    else:
        content = plain_wechat_text_to_markdown(raw_content, title)
    if not content:
        html_body = find_longest_html(data)
        raw_content = html_body or raw_content
        content = html_to_markdown(html_body) if html_body else ""
    return Article(
        title=title,
        author=author,
        url=url,
        published=parse_date(first_present(best, ["publish_time", "create_time", "datetime", "date", "time", "send_time"])) or fallback.published,
        content=content,
        raw=best or fallback.raw,
        source_table_count=count_source_data_tables(raw_content),
        markdown_table_count=count_markdown_tables(content),
    )


def select_detail_content(item: dict[str, Any], fallback: str = "") -> str:
    html_keys = ["content_html", "article_content", "html", "source", "Content"]
    text_keys = ["content", "text", "ori_content"]
    html_candidates = [first_str(item, [key]) for key in html_keys]
    html_candidates = [value for value in html_candidates if looks_like_html(value)]
    table_candidates = [value for value in html_candidates if re.search(r"<table\b", value, re.I)]
    if table_candidates:
        return max(table_candidates, key=len)
    if html_candidates:
        return max(html_candidates, key=len)
    for key in text_keys:
        if key in item:
            rendered = render_structured_content(item.get(key))
            if rendered:
                return rendered
    return fallback


def render_structured_content(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        if isinstance(value.get("raw_content"), list):
            rendered = render_structured_content(value.get("raw_content"))
            if rendered:
                return rendered
        if isinstance(value.get("article"), dict):
            article = value.get("article")
            article_text = render_structured_content(article)
            if article_text:
                return article_text
            if isinstance(article, dict) and isinstance(article.get("full_text"), str):
                return article.get("full_text", "").strip()
        if isinstance(value.get("sections"), list):
            rendered = render_article_sections(value.get("sections", []))
            if rendered:
                return rendered
        if isinstance(value.get("text"), str):
            return value.get("text", "").strip()
        parts = []
        title = clean_inline(str(value.get("title", "")))
        text = render_structured_content(value.get("content") or value.get("body") or "")
        if title:
            parts.append(title)
        if text:
            parts.append(text)
        return "\n\n".join(parts).strip()
    if isinstance(value, list):
        parts: list[str] = []
        sequence = value
        if (
            len(sequence) > 1
            and isinstance(sequence[0], dict)
            and isinstance(sequence[0].get("text"), str)
            and len(sequence[0].get("text", "")) > 1000
        ):
            sequence = sequence[1:]
        numbered_section_count = sum(
            1
            for item in sequence
            if isinstance(item, dict)
            and item.get("type") == "section"
            and re.match(r"^\s*\d{1,3}[.、．]\s+\S+", str(item.get("text") or ""))
        )
        preserve_numbered_sections = numbered_section_count >= 5
        for item in sequence:
            rendered = (
                render_raw_content_item(item, preserve_numbered_sections=preserve_numbered_sections)
                if isinstance(item, dict)
                else render_structured_content(item)
            )
            if rendered:
                parts.append(rendered)
        return "\n\n".join(parts).strip()
    return ""


def render_raw_content_item(item: dict[str, Any], preserve_numbered_sections: bool = False) -> str:
    text = clean_inline(str(item.get("text") or "").strip())
    if not text:
        return ""
    if preserve_numbered_sections and item.get("type") == "section" and re.match(r"^\d{1,3}[.、．]\s+\S+", text):
        return normalize_ordered_marker(text)
    if item.get("type") == "section" and len(text) <= 120:
        return format_structured_heading(text)
    if is_heading_like_text(text):
        return format_structured_heading(text)
    if is_formula_like_text(text):
        return f"$$\n{text}\n$$"
    return text


def normalize_ordered_marker(text: str) -> str:
    return re.sub(r"^(\d{1,3})[、．]\s*", r"\1. ", text.strip())


def is_heading_like_text(text: str) -> bool:
    if not text or len(text) > 80:
        return False
    return bool(
        re.match(r"^[一二三四五六七八九十]+[、.．]\s*\S+", text)
        or re.match(r"^\d+(?:\.\d+)*[、.．]\s*\S+", text)
    )


def format_structured_heading(text: str) -> str:
    title = normalize_heading_number(text)
    if not title or title.lower() == "none":
        return ""
    level = 3
    if re.match(r"^\d+\.\d+(?:\.\d+)*\s+", title):
        level = 4
    elif re.match(r"^\d+\.\s+", title):
        level = 3
    return "#" * level + f" {title}"


def is_formula_like_text(text: str) -> bool:
    if len(text) > 160 or "\n" in text:
        return False
    if len(re.findall(r"[\u4e00-\u9fff]", text)) > 8:
        return False
    if re.search(
        r"Attention(?:_[A-Za-z0-9]+)?\s*\(|MultiHead\s*\(|head_[A-Za-z0-9]+\s*=|=\s*softmax|softmax\s*(?:\(|\(\()|sqrt\s*\(|√\s*d_k|QK\^T|[A-Z]W_[A-Za-z0-9]+\^[A-Za-z]|W\^[A-Za-z]|d_k|d_h|\\frac|\\sqrt|\\sum|\\begin",
        text,
    ):
        return True
    if re.search(r"\b[A-Z]\s*=\s*\[.+\]", text):
        return True
    return False


def looks_like_structured_markdown(value: str) -> bool:
    text = value or ""
    numbered_lines = re.findall(r"(?m)^\d{1,3}\.\s+\S+", text)
    return bool(re.search(r"(?m)^#{3,5}\s+\S+", text) or "$$\n" in text or len(numbered_lines) >= 5)


def render_article_sections(sections: list[Any]) -> str:
    parts: list[str] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        title = clean_inline(str(section.get("title", "")).strip())
        text = render_structured_content(section.get("text") or "")
        if title and title != "引言":
            heading = f"### {title}"
            if re.match(r"^\d+\.\d+(?:\.\d+)*\s+", title):
                heading = f"#### {title}"
            parts.append(heading)
        if text:
            parts.append(text)
    return "\n\n".join(part.strip() for part in parts if part and part.strip()).strip()


def find_longest_html(value: Any) -> str:
    candidates: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, str) and looks_like_html(node):
            candidates.append(node)

    walk(value)
    return max(candidates, key=len) if candidates else ""


def next_list_offset(data: Any) -> Any:
    if not isinstance(data, dict):
        return ""
    payload = data.get("data")
    if not isinstance(payload, dict):
        return ""
    raw_offset = payload.get("next_offset") or payload.get("offset") or payload.get("ContinueFlag") or ""
    if isinstance(raw_offset, dict):
        if raw_offset.get("IsEnd") == 1:
            return ""
        return raw_offset.get("Offset") or ""
    return raw_offset


def rank_articles(articles: list[Article], queries: list[str]) -> list[Article]:
    scored: list[tuple[int, int, Article]] = []
    title_queries = [query for query in queries if 6 <= len(query) <= 100]
    for index, article in enumerate(articles):
        haystack = normalize_title("\n".join([article.title, article.content, article.url]))
        score = 0
        for query in title_queries:
            normalized = normalize_title(query)
            if normalized and normalized in haystack:
                score += 100
            else:
                score += sum(1 for token in split_query_tokens(query) if normalize_title(token) in haystack)
        scored.append((score, -index, article))
    scored.sort(reverse=True)
    matched = [article for score, _, article in scored if score >= 3]
    return matched if title_queries else articles


def iter_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            found.append(node)
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return found


def first_str(item: dict[str, Any], keys: list[str]) -> str:
    value = first_present(item, keys)
    return value.strip() if isinstance(value, str) else ""


def first_present(item: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def write_bundles(articles: list[Article], args: argparse.Namespace, output_dir: Path) -> list[Path]:
    ranges = parse_ranges(args.ranges, len(articles), args.group_size)
    written: list[Path] = []
    for start, end, label in ranges:
        selected = articles[start:end]
        author = selected[0].author if selected else args.author or "微信公众号"
        summary = infer_bundle_summary(selected)
        filename = args.filename_template.format(
            author=safe_filename_part(author, "wechat"),
            summary=safe_filename_part(summary, "AI总结内容"),
            date=today(),
            range=label,
        )
        path = unique_path(output_dir / safe_text(filename, "wechat-clippings-vp.md"))
        path.write_text(render_bundle(selected, author, summary, label, len(articles), args.format_mode), encoding="utf-8")
        warn_table_loss(selected, path)
        written.append(path)
    return written


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a unique output path for {path}")


def render_bundle(
    articles: list[Article],
    author: str,
    summary: str,
    label: str,
    total: int,
    format_mode: str = "plain",
) -> str:
    title = f"微信_{author}_{summary}_公众号文章剪藏_{today()}_{label}"
    source = articles[0].source_api if articles else "https://api.tikhub.io/"
    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"source: {yaml_quote(source)}",
        "author:",
        f"  - {yaml_quote(author)}",
        f"published: {yaml_quote(articles[0].published if articles else '')}",
        f"created: {today()}",
        f"description: {yaml_quote(f'TikHub 命中的微信公众号文章候选，共 {total} 条，本文档收录 {len(articles)} 条')}",
        "tags:",
        '  - "clippings"',
        '  - "wechat"',
        f"  - {yaml_quote(author)}",
        "---",
        "",
    ]
    for index, article in enumerate(articles, 1):
        article_number = f"0x{index:02d}"
        lines.append(f"## {article_number}. {article.title or '未命名公众号文章'}")
        if article.published or article.url:
            if article.published:
                lines.append(f"> 发布日期：{article.published}  ")
            if article.url:
                lines.append(f"> 原文链接：[{article.title or '原文'}]({article.url})")
            lines.append("")
        body = article.content.strip() or f"> 未能从 TikHub 详情接口解析到正文。原文链接：{article.url}"
        body = downgrade_body_headings(body)
        body = demote_list_heading_artifacts(body)
        if format_mode == "readable":
            body = enhance_readability(body)
        lines.append(body)
        lines.append("")
    return remove_blank_lines_after_headings("\n".join(lines)).rstrip() + "\n"


def warn_table_loss(articles: list[Article], path: Path) -> None:
    for article in articles:
        if article.source_table_count and article.markdown_table_count < article.source_table_count:
            print(
                "Warning: table preservation check: "
                f"{article.title} source data tables={article.source_table_count}, "
                f"markdown tables={article.markdown_table_count}, file={path}",
                file=sys.stderr,
            )


def enhance_readability(value: str) -> str:
    text = value.strip()
    text = split_glued_heading_summary(text)
    text = enforce_numbered_heading_levels(text)
    text = emphasize_interview_labels(text)
    text = convert_memory_dimension_block(text)
    text = convert_cot_react_tot_block(text)
    text = convert_inline_ordinal_series_to_lists(text)
    text = convert_colon_series_to_lists(text)
    text = convert_definition_runs_to_lists(text)
    text = convert_named_colon_series_to_lists(text)
    text = cleanup_readable_markdown(text)
    text = normalize_block_spacing(clean_markdown(text))
    text = cleanup_readable_markdown(text)
    return text.strip()


def emphasize_interview_labels(value: str) -> str:
    labels = [
        "考察意图",
        "回答框架",
        "核心区别",
        "关键设计要点",
        "核心设计原则",
        "工程实现上",
        "实践中推荐的策略",
        "两者的根本权衡",
        "选择依据可以简化为",
    ]
    text = value
    for label in labels:
        text = re.sub(rf"(?m)^(?!\*\*)({re.escape(label)})([:：])", rf"**\1\2**", text)
    return text


def convert_colon_series_to_lists(value: str) -> str:
    labels = "第一|第二|第三|第四|第五"
    pattern = re.compile(rf"(?m)^([^\n：:。]{{4,80}}[:：])\s*((?:{labels})是.+)$")

    def repl(match: re.Match[str]) -> str:
        intro = match.group(1).strip()
        body = match.group(2).strip()
        items = split_chinese_ordinal_items(body)
        if len(items) < 2:
            return match.group(0)
        return intro + "\n" + "\n".join(f"{index}. {strip_ordinal_prefix(item)}" for index, item in enumerate(items, 1))

    return pattern.sub(repl, value)


def convert_inline_ordinal_series_to_lists(value: str) -> str:
    pattern = re.compile(r"(?m)^(.{0,80}?)(第一(?:层)?是.+第二(?:层)?是.+)$")

    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1).strip()
        body = match.group(2).strip()
        items = split_chinese_ordinal_items(body)
        if len(items) < 2:
            return match.group(0)
        lines = [f"{prefix}" if prefix else ""]
        lines.extend(f"{index}. {strip_ordinal_prefix(item)}" for index, item in enumerate(items, 1))
        return "\n".join(line for line in lines if line)

    return pattern.sub(repl, value)


def convert_named_colon_series_to_lists(value: str) -> str:
    pattern = re.compile(r"(?m)^([^\n：:。]{4,80}[:：])\s*((?:[A-Za-z][A-Za-z0-9 /+-]*[：:].+?)(?:[A-Za-z][A-Za-z0-9 /+-]*[：:].+)+)$")

    def repl(match: re.Match[str]) -> str:
        intro = match.group(1).strip()
        body = match.group(2).strip()
        items = split_named_colon_items(body)
        if len(items) < 2:
            return match.group(0)
        return intro + "\n" + "\n".join(f"- {item}" for item in items)

    return pattern.sub(repl, value)


def convert_definition_runs_to_lists(value: str) -> str:
    lines = value.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        if not previous_nonempty_line_is_definition_intro(output):
            output.append(lines[index])
            index += 1
            continue
        run: list[str] = []
        cursor = index
        while cursor < len(lines):
            line = lines[cursor].strip()
            if is_definition_line(line):
                run.append(line)
                cursor += 1
                continue
            if not line and run:
                cursor += 1
                continue
            break
        if len(run) >= 3:
            output.extend(format_definition_item(line) for line in run)
            index = cursor
            continue
        output.append(lines[index])
        index += 1
    return "\n".join(output)


def previous_nonempty_line_is_definition_intro(lines: list[str]) -> bool:
    for line in reversed(lines):
        stripped = line.strip()
        if stripped:
            return is_definition_intro(stripped)
    return False


def is_definition_intro(line: str) -> bool:
    return bool(re.search(r"(包含|包括|拆成|分为|有|如下|包括：|包括:|步骤|模块|机制|方案|维度|环节|考点)", line or ""))


def is_definition_line(line: str) -> bool:
    if not line or line.startswith(("#", ">", "-", "|", "**")):
        return False
    if len(line) > 360 or "：" not in line and ":" not in line:
        return False
    head = re.split(r"[:：]", line, maxsplit=1)[0].strip()
    if not 2 <= len(head) <= 45:
        return False
    if head.endswith(("是", "在于")):
        return False
    return bool(re.search(r"[A-Za-z\u4e00-\u9fff]", head))


def format_definition_item(line: str) -> str:
    head, sep, tail = re.split(r"([:：])", line, maxsplit=1)
    return f"- **{head.strip()}{sep}** {tail.strip()}"


def cleanup_readable_markdown(value: str) -> str:
    text = value
    text = re.sub(r"(?m)^-\s+(\d+\.\s+)", r"\1", text)
    text = re.sub(r"(?m)^-\s+\*\*(\d+\.\s+)([^*\n]+[:：]\*\*)", r"- **\2", text)
    text = re.sub(r"(?m)^(\d+\.\s+)\*\*([^*\n]+[:：]\*\*)", r"- **\2", text)
    text = re.sub(r"(\*\*[^*\n]+[:：]\*\*)(?=\S)", r"\1 ", text)
    text = re.sub(r"(\*\*考察意图[:：]\*\*\s+[^\n]+?)(\*\*回答框架[:：]\*\*)", r"\1\n\n\2", text)
    text = re.sub(r"(?m)^(- \*\*[^*\n]+：\*\*)-", r"\1\n- ", text)
    text = re.sub(r"(?m)^(- \*\*[^*\n]+：\*\*)\s*(?=- \*\*)", r"\1\n", text)
    text = re.sub(r"(?m)^(- \*\*[^*\n]+：\*\*)$", lambda m: m.group(1)[2:-2] + "：", text)
    text = re.sub(r"\*\*\|", "|", text)
    text = re.sub(r"\|\*\*", "|", text)
    text = re.sub(r"(?m)^(\| ToT \|[^\n]+?)(?<!\|)$", r"\1 |", text)
    text = re.sub(r"(?m)^\*\*\|\*\*", "", text)
    text = re.sub(r"(?m)^\*\*\|\*\*(选择依据可以简化为：\*\*)", r"**\1", text)
    text = re.sub(r"(?m)^\*\*\|\*\*(.+)$", r"**\1", text)
    text = re.sub(r"\*\*\*\*", "**", text)
    return text


def split_chinese_ordinal_items(value: str) -> list[str]:
    starts = list(re.finditer(r"(第一|第二|第三|第四|第五)(?:层)?是", value))
    if len(starts) < 2:
        return []
    items: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(value)
        item = value[start.start() : end].strip(" ；;。")
        if item:
            items.append(item)
    return items


def strip_ordinal_prefix(value: str) -> str:
    return re.sub(r"^(第一|第二|第三|第四|第五)(?:层)?是", "", value).strip()


def split_named_colon_items(value: str) -> list[str]:
    starts = list(re.finditer(r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9 /+-]{1,40})[：:]", value))
    if len(starts) < 2:
        return []
    items: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(value)
        item = value[start.start() : end].strip(" ；;。")
        if item:
            items.append(item)
    return items


def convert_cot_react_tot_block(value: str) -> str:
    pattern = re.compile(
        r"(?s)三者的根本差异在于推理结构和搜索空间的形状：\n\n"
        r"CoT[（(]Chain-of-Thought[）)]是线性链式推理，(.+?)"
        r"ReAct是带外部交互的线性推理。(.+?)"
        r"ToT[（(]Tree-of-Thought[）)]将搜索空间从线性扩展为树状。(.+?)"
        r"选择依据可以简化为：(.+?)(?=\n###|\n####|\Z)"
    )

    def repl(match: re.Match[str]) -> str:
        return (
            "三者的根本差异在于推理结构和搜索空间的形状：\n\n"
            "| 范式 | 推理结构 | 核心特点 |\n"
            "| :--- | :--- | :--- |\n"
            f"| CoT | 线性链式推理 | {match.group(1).strip()} |\n"
            f"| ReAct | 带外部交互的线性推理 | {match.group(2).strip()} |\n"
            f"| ToT | 树状搜索 | {match.group(3).strip()} |\n\n"
            f"**选择依据可以简化为：**{match.group(4).strip()}"
        )

    return pattern.sub(repl, value)


def convert_memory_dimension_block(value: str) -> str:
    pattern = re.compile(
        r"(?s)两者在三个维度上有本质差异：\n\n"
        r"(?:维度\s*)?短期记忆\s*长期记忆\s*信息生命周期\s*当前会话/任务内有效\s*跨会话持久化\s*存储机制\s*上下文窗口[（(]token 序列[）)]\s*向量数据库 / 知识图谱 / 结构化 DB\s*访问方式\s*自动包含在每次 LLM 调用中\s*按需检索[（(]语义搜索、关键词匹配[）)]"
    )
    table = (
        "两者在三个维度上有本质差异：\n\n"
        "| 维度 | 短期记忆 | 长期记忆 |\n"
        "| :--- | :--- | :--- |\n"
        "| 信息生命周期 | 当前会话/任务内有效 | 跨会话持久化 |\n"
        "| 存储机制 | 上下文窗口（token 序列） | 向量数据库 / 知识图谱 / 结构化 DB |\n"
        "| 访问方式 | 自动包含在每次 LLM 调用中 | 按需检索（语义搜索、关键词匹配） |"
    )
    return pattern.sub(table, value)


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
            ranges.append((start - 1, end, str(start) if start == end else f"{start}-{end}"))
        if not ranges:
            raise RuntimeError(f"--ranges did not select any article from {total} available results")
        return ranges
    return [(start, min(start + group_size, total), f"{start + 1}-{min(start + group_size, total)}") for start in range(0, total, group_size)]


def extract_wechat_urls(text: str) -> list[str]:
    urls = []
    for match in re.finditer(r"https?://[^\s)>\]]+", text):
        url = match.group(0).strip().rstrip(".,;，。；")
        if "mp.weixin.qq.com" in url:
            urls.append(url)
    return unique(urls)


def dedupe_articles(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    result: list[Article] = []
    for article in articles:
        key = article.url or normalize_title(article.title)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(article)
    return result


def html_to_markdown(value: str) -> str:
    value = extract_js_content(value)
    parser = BodyHTMLParser()
    parser.feed(value or "")
    return clean_wechat_chrome(clean_markdown(parser.markdown()))


def extract_js_content(value: str) -> str:
    match = re.search(r'<div[^>]+id=["\']js_content["\'][^>]*>(.*?)</div>\s*<script', value or "", flags=re.I | re.S)
    if match:
        return match.group(1)
    match = re.search(r'<div[^>]+id=["\']js_content["\'][^>]*>(.*)', value or "", flags=re.I | re.S)
    return match.group(1) if match else value


def clean_wechat_chrome(value: str) -> str:
    stop_markers = [
        "\n 预览时标签不可点",
        "\n 微信扫一扫",
        "\n    继续滑动看下一个",
        "\n  继续滑动看下一个",
        "\n    向上滑动看下一个",
        "\n 轻触阅读原文",
        "\n [ 知道了 ]",
    ]
    cut = len(value)
    for marker in stop_markers:
        pos = value.find(marker)
        if pos >= 0:
            cut = min(cut, pos)
    lines: list[str] = []
    noisy_patterns = [
        r"^\s*(原创|乔木mq|乔木|在小说阅读器读本章|去阅读|在小说阅读器中沉浸阅读)\s*$",
        r"^\s*(预览时标签不可点|微信扫一扫|继续滑动看下一个|向上滑动看下一个|轻触阅读原文|关注该公众号)\s*$",
        r"^\s*(取消|允许|知道了|分析|收藏|听过)\s*$",
        r"^\s*(今日题目|第[一二三四五六七八九十\d]+题)[:：]?.*$",
        r"^\s*(微信扫一扫|关注该公众号|使用小程序|取消|允许|分析|收藏|听过)\s*$",
        r"^\s*\[?\s*(取消|允许|知道了)\s*\]?",
        r"^\s*×\s*分析\s*$",
        r"^\s*>?\s*/\s*作者[:：].*$",
        r"^\s*\*\*我是\*\*.*?(训练营|Burger_AI|了解可\+v).*$",
        r"^\s*\*\*【.*?训练营.*?(Burger_AI|了解可\+v|详情).*$",
    ]
    raw_lines = value[:cut].splitlines()
    index = 0
    while index < len(raw_lines):
        line = raw_lines[index]
        if "Burger_AI" in line:
            line = re.sub(r"^.*?Burger_AI\*{0,2}\s*", "", line)
        if is_wechat_promo_line(line):
            index += 1
            while index < len(raw_lines) and (not raw_lines[index].strip() or is_markdown_image(raw_lines[index])):
                index += 1
            continue
        if any(re.search(pattern, line) for pattern in noisy_patterns):
            index += 1
            continue
        lines.append(line.rstrip())
        index += 1
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return normalize_link_lines(text)


def is_wechat_promo_line(line: str) -> bool:
    compact = re.sub(r"\s+", "", line)
    if not compact:
        return False
    promo_keywords = ("欢迎关注", "加我微信", "交个朋友", "感兴趣的朋友", "二维码", "扫码")
    identity_keywords = ("我是", "AI算法", "AI全栈", "深耕")
    return any(keyword in compact for keyword in promo_keywords) and (
        any(keyword in compact for keyword in identity_keywords) or "微信" in compact
    )


def is_markdown_image(line: str) -> bool:
    return bool(re.match(r"^\s*!\[[^\]]*\]\([^)]+\)\s*$", line))


def normalize_link_lines(value: str) -> str:
    lines = value.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        same_line = re.match(r"^(\s*)([^：:\n]{2,80}?)(?:地址|官网|链接|开源地址)[:：]\s*(https?://\S+)\s*$", line)
        if same_line:
            indent, label, url = same_line.groups()
            output.append(f"{indent}[{label.strip()}]({url.strip()})")
            index += 1
            continue
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        split_line = re.match(r"^(\s*)([^：:\n]{2,80}?)(?:地址|官网|链接|开源地址)[:：]\s*$", line)
        split_url = re.match(r"^\s*(https?://\S+)\s*$", next_line)
        if split_line and split_url:
            indent, label = split_line.groups()
            output.append(f"{indent}[{label.strip()}]({split_url.group(1).strip()})")
            index += 2
            continue
        line = re.sub(r"\]\(\s*(https?://[^)\s]+)\s*\)", r"](\1)", line)
        output.append(line)
        index += 1
    return "\n".join(output)


def looks_like_html(value: str) -> bool:
    return bool(re.search(r"</?(p|div|section|article|h\d|img|br|span|strong|table)\b", value or "", re.I))


def count_source_data_tables(value: str) -> int:
    body = extract_js_content(value or "")
    count = 0
    for table_match in re.finditer(r"<table\b[^>]*>(.*?)</table>", body, flags=re.I | re.S):
        rows = []
        for tr_match in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", table_match.group(1), flags=re.I | re.S):
            cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr_match.group(1), flags=re.I | re.S)
            clean_cells = [clean_inline(re.sub(r"<[^>]+>", " ", cell)) for cell in cells]
            if any(clean_cells):
                rows.append(clean_cells)
        if len(rows) >= 2 and max((len(row) for row in rows), default=0) >= 2:
            count += 1
    return count


def count_markdown_tables(value: str) -> int:
    return len(re.findall(r"(?m)^\|\s*:---", value or ""))


def clean_markdown(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if looks_like_dense_ordered_list(text):
        return normalize_dense_ordered_list(text)
    text = normalize_inline_markdown(text)
    text = remove_repeated_toc_blocks(text)
    text = wrap_standalone_formula_lines(text)
    text = demote_list_heading_artifacts(text)
    text = normalize_block_spacing(text)
    return remove_blank_lines_after_headings(text).strip()


def wrap_standalone_formula_lines(value: str) -> str:
    lines = value.splitlines()
    output: list[str] = []
    in_fence = False
    in_math = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            output.append(line)
            continue
        if stripped == "$$":
            in_math = not in_math
            output.append(line)
            continue
        if not in_fence and not in_math and is_formula_like_text(stripped):
            output.extend(["$$", stripped, "$$"])
            continue
        output.append(line)
    return "\n".join(output)


def looks_like_dense_ordered_list(value: str) -> bool:
    lines = [line.strip() for line in (value or "").splitlines() if line.strip()]
    numbered = [line for line in lines if re.match(r"^\d{1,3}[.??]\s+\S+", line)]
    if len(numbered) < 8 or len(numbered) < max(5, int(len(lines) * 0.6)):
        return False
    nums = [int(re.match(r"^(\d{1,3})", line).group(1)) for line in numbered if re.match(r"^(\d{1,3})", line)]
    if len(nums) < 8:
        return False
    return nums == sorted(nums) and len(set(nums)) == len(nums) and nums[0] in {1, 0}


def normalize_dense_ordered_list(value: str) -> str:
    out: list[str] = []
    for line in (value or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        stripped = normalize_ordered_marker(stripped)
        out.append(stripped)
    return "\n".join(out).strip()


def remove_blank_lines_after_headings(value: str) -> str:
    return re.sub(r"(?m)^(#{1,6}\s+\S[^\n]*)\n[ \t]*\n", r"\1\n", value or "")


def demote_list_heading_artifacts(value: str) -> str:
    """Demote WeChat list items that were accidentally promoted to headings."""
    text = value or ""
    text = re.sub(r"(?m)^###\s*•\s*", "- ", text)
    text = re.sub(r"(?m)^###\s+(\d+)\.([^\s].*)$", lambda m: f"{m.group(1)}. {m.group(2).strip()}", text)
    text = re.sub(r"(?m)^###\s+(\d+)\.\s+(.{70,})$", lambda m: f"{m.group(1)}. {m.group(2).strip()}", text)
    text = re.sub(r"(- [^\n]+)\n\n(?=- )", r"\1\n", text)
    text = re.sub(r"(\d+\. [^\n]+)\n\n(?=\d+\. )", r"\1\n", text)
    return text


def remove_repeated_toc_blocks(value: str) -> str:
    lines = (value or "").splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped in {"今日全部题目", "#### 今日全部题目"}:
            end = index + 1
            while end < len(lines) and not lines[end].strip():
                end += 1
            numbered_end = end
            while numbered_end < len(lines) and re.match(r"^\s*\d{1,2}\.\s*大模型算法：", lines[numbered_end]):
                numbered_end += 1
            if numbered_end - end >= 2:
                while output and not output[-1].strip():
                    output.pop()
                index = numbered_end
                continue
        if stripped.startswith("今日全部题目"):
            match = re.search(r"8\.\s*大模型算法：错误数据的掩码处理", lines[index])
            if match:
                rest = lines[index][match.end() :].lstrip()
                if rest:
                    output.append(rest)
                index += 1
                continue
        if re.match(r"^###\s+•\s+\S+", lines[index]):
            end = index
            while end < len(lines) and (re.match(r"^###\s+•\s+\S+", lines[end]) or not lines[end].strip()):
                end += 1
            toc_count = sum(1 for line in lines[index:end] if re.match(r"^###\s+•\s+\S+", line))
            if toc_count >= 2:
                while output and not output[-1].strip():
                    output.pop()
                index = end
                continue
        output.append(lines[index])
        index += 1
    return "\n".join(output)


def plain_wechat_text_to_markdown(value: str, title: str = "") -> str:
    text = html.unescape(value or "")
    text = restore_escaped_newlines(text)
    text = re.sub(r"\r\n?", "\n", text)
    text = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()).strip()
    text = strip_plain_wechat_header(text, title)
    text = cut_plain_wechat_tail(text)
    text = normalize_plain_markers(text)
    dense_ordered = looks_like_dense_ordered_list(text)
    text = clean_wechat_chrome(clean_markdown(text))
    if not dense_ordered:
        text = repair_plain_text_headings(text)
        text = remove_blank_lines_after_headings(text)
    return text.strip()


def restore_escaped_newlines(value: str) -> str:
    text = value or ""
    if "\\n" in text or "\\r" in text or "\\t" in text:
        text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n").replace("\\t", "\t")
    return text


def strip_plain_wechat_header(value: str, title: str = "") -> str:
    text = value.strip()
    if title:
        text = re.sub(r"^" + re.escape(title.strip()) + r"\s+", "", text)
    text = re.sub(
        r"^原创\s+\S+\s+\S+\s+\S+\s+在小说阅读器读本章\s+去阅读\s+在小说阅读器中沉浸阅读\s+",
        "",
        text,
    )
    text = re.sub(r"^.*?今日题目：.*?第[一二三四五六七八九十\d]+题\s+", "", text, count=1)
    match = re.search(r"(?<!\S)(一、\S+)", text)
    if match and match.start() > 0:
        text = text[match.start() :]
    return text.strip()


def cut_plain_wechat_tail(value: str) -> str:
    stop_markers = [
        "预览时标签不可点",
        "微信扫一扫",
        "继续滑动看下一个",
        "向上滑动看下一个",
        "轻触阅读原文",
        "使用小程序",
        "取消",
        "允许",
        "知道了",
    ]
    promo_patterns = [
        r"\)；\s*\)；\s*\(2\)加入DailyLLM社群",
        r"\)；\s*\(2\)加入DailyLLM社群",
        r"加入DailyLLM社群\(见文末二维码\).*?写在前面",
    ]
    cut = len(value)
    for marker in stop_markers:
        pos = value.find(marker)
        if pos >= 0:
            cut = min(cut, pos)
    for pattern in promo_patterns:
        match = re.search(pattern, value, flags=re.S)
        if match:
            cut = min(cut, match.start())
    return value[:cut].strip()


def normalize_plain_markers(value: str) -> str:
    text = value.replace("（", "(").replace("）", ")")
    text = re.sub(r"\s*[•●]\s*", "\n- ", text)
    text = re.sub(r"\s+(?=[一二三四五六七八九十]+、)", "\n", text)
    text = re.sub(r"\s+(?=\d{1,2}、)", "\n", text)
    text = re.sub(r"\s+(?=\(\d+\))", "\n", text)
    text = re.sub(r"\s+(?=①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩)", "\n", text)
    text = re.sub(r"(?m)^\s*([一二三四五六七八九十]+、)([^\n]{2,60}?)(?:\s{2,}|\n|$)", normalize_chinese_heading, text)
    text = re.sub(r"(?m)^\s*(\d{1,2}[、.．])(.+?)(?=\n\s*\(\d+\)|\n\s*①|\n\s*②|\n\s*③|\n\s*④|\n\s*⑤|\n\s*⑥|\n\s*⑦|\n\s*⑧|\n\s*⑨|\n\s*⑩|$)", normalize_numeric_heading, text)
    text = re.sub(r"(?m)^\((\d+)\)\s*", r"\1. ", text)
    text = normalize_ordered_text(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n{2,}(?=\d+\. )", "\n", text)
    return text.strip()


def normalize_chinese_heading(match: re.Match[str]) -> str:
    heading = re.sub(r"\s+", " ", match.group(2)).strip()
    return f"### {match.group(1)}{heading}"


def normalize_numeric_heading(match: re.Match[str]) -> str:
    marker = match.group(1).replace("、", ".")
    body = re.sub(r"\s+", " ", match.group(2)).strip()
    if not body:
        return f"#### {marker}"
    parts = re.split(r"\s+(?=\d+\. |\(\d+\)|[①②③④⑤⑥⑦⑧⑨⑩])", body, maxsplit=1)
    heading = parts[0].strip()
    rest = parts[1].strip() if len(parts) > 1 else ""
    return f"#### {marker} {heading}" + (f"\n{rest}" if rest else "")


def repair_plain_text_headings(value: str) -> str:
    text = value
    text = re.sub(r"(?m)^#\s*$\n?", "", text)
    text = split_glued_heading_summary(text)
    text = re.sub(r"(?m)^(###\s+\d+\.\s+.+?)(?=###\s+\d+\.\d+\s+)", r"\1\n", text)
    text = re.sub(r"(?m)^(###\s+\d+\.\d+\s+.+?)(?=###\s+\d+\.\d+\s+)", r"\1\n", text)
    text = enforce_numbered_heading_levels(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def enforce_numbered_heading_levels(value: str) -> str:
    lines: list[str] = []
    current_major = ""
    for line in value.splitlines():
        match = re.match(r"^(#{3,5})\s+(\d+)\.(\d+(?:\.\d+)*)\s+(.+)$", line)
        if match:
            current_major = match.group(2)
            lines.append(f"#### {match.group(2)}.{match.group(3)} {match.group(4).strip()}")
            continue
        match = re.match(r"^(#{3,5})\s+(\d+)\.\s+(.+)$", line)
        if match:
            number = match.group(2)
            title = match.group(3).strip()
            if current_major and int(number) != int(current_major) and len(title) <= 90:
                lines.append(f"#### {current_major}.{number} {title}")
            else:
                current_major = number
                lines.append(f"### {number}. {title}")
            continue
        lines.append(line)
    return "\n".join(lines)


def split_glued_heading_summary(value: str) -> str:
    lines: list[str] = []
    for line in value.splitlines():
        stripped = line.strip()
        match = re.match(r"^(#{3,4}\s+\d+(?:\.\d+)?\.?\s+)(.+)$", stripped)
        if not match:
            lines.append(line)
            continue
        body = match.group(2).strip()
        split_at = find_heading_summary_split(body)
        if split_at <= 0:
            lines.append(line)
            continue
        heading = body[:split_at].strip()
        rest = body[split_at:].strip()
        if rest:
            lines.append(f"{match.group(1)}{heading}")
            lines.append(rest)
        else:
            lines.append(line)
    return "\n".join(lines)


def find_heading_summary_split(body: str) -> int:
    for marker in ("考察意图：", "回答框架："):
        pos = body.find(marker)
        if pos > 0:
            return pos
    patterns = [
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=(?:LoRA|SFT|RLHF|DPO|KTO|MOE|MoE|KV Cache|PagedAttention|GQA|MQA|MHA|FlashAttention|Self-Attention|Transformer|Embedding|Tokenizer|RoPE|RAG|Agent)(?:\s|在|是|相关|\())",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=在这份题库中)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=这类题)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=位置编码)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=归一化)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=是所有)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=是\s)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=之?后的)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=作为)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=它)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=这是)",
        r"(?<=[\u4e00-\u9fffA-Za-z0-9）)])(?=面试)",
    ]
    candidates: list[int] = []
    for pattern in patterns:
        for match in re.finditer(pattern, body):
            pos = match.start()
            if 6 <= pos <= 70:
                candidates.append(pos)
                break
    return min(candidates) if candidates else -1


def normalize_inline_markdown(value: str) -> str:
    text = re.sub(r"\*\*\s+([^*\n]+?)\s+\*\*", lambda m: f"**{m.group(1).strip()}**", value)
    text = re.sub(r"(?<!\*)\*\s+([^*\n]+?)\s+\*(?!\*)", lambda m: f"*{m.group(1).strip()}*", text)
    text = re.sub(r"(\*\*[^*\n]+\*\*)\s{2,}", r"\1 ", text)
    text = re.sub(r"\*\*([^\n*]+?)\*\*\s+([，。！？；：,.!?;:）)])", r"**\1**\2", text)
    text = protect_inline_html_examples(text)
    text = normalize_fence_boundaries(text)
    text = normalize_code_fence_languages(text)
    text = re.sub(r"(?m)^#{1,6}\s*$\n?", "", text)
    text = re.sub(r"([。！？：:])!\[", r"\1\n\n![", text)
    text = re.sub(r"(###\s+[^\n]+)!\[", r"\1\n\n![", text)
    text = re.sub(r"^(#{3,5})\s+(.+)$", lambda m: f"{m.group(1)} {m.group(2).strip()}", text, flags=re.M)
    text = re.sub(r"^(#{3,5}\s+.+?)\s*\n{2,}(?=[ \t]*[^\s#!])", r"\1\n", text, flags=re.M)
    text = normalize_block_spacing(text)
    text = re.sub(r"(?m)^[ \t]*-[ \t]*\n", "", text)
    text = re.sub(r"\s{2,}([，。！？；：,.!?;:）)])", r"\1", text)
    text = normalize_ordered_text(text)
    return text


def normalize_code_fence_languages(value: str) -> str:
    fence_re = re.compile(r"```([A-Za-z0-9_+-]*)\n(.*?)\n```", re.S)

    def repl(match: re.Match[str]) -> str:
        lang = (match.group(1) or "").strip().lower()
        body = match.group(2)
        body = re.sub(r"^\s*(?:`{3,}|'{3,})\s*([A-Za-z0-9_+-]+)?\s*\n?", "", body)
        body = re.sub(r"\n?\s*(?:`{3,}|'{3,})\s*$", "", body)
        inferred = infer_fence_language(body)
        final_lang = inferred if lang in {"", "text", "txt", "plain"} or inferred != "text" else lang
        final_lang = "text" if final_lang in {"", "txt", "plain"} else final_lang
        return f"```{final_lang}\n{body.strip()}\n```"

    return fence_re.sub(repl, value)


def normalize_fence_boundaries(value: str) -> str:
    text = value
    text = re.sub(r"(?m)([^\n])\s*(```(?:text|python|bash|json|javascript|typescript|sql|yaml|cpp|cuda|mermaid)?)\s*$", r"\1\n\2", text)
    text = re.sub(r"(?m)^(\s*)(```(?:text|python|bash|json|javascript|typescript|sql|yaml|cpp|cuda|mermaid)?)\s+([^\n]+)$", r"\1\2\n\3", text)
    text = re.sub(r"(?m)([^\n])\s*(```)\s*$", r"\1\n\2", text)
    text = re.sub(r"\n{3,}(```)", r"\n\n\1", text)
    return text


def protect_inline_html_examples(value: str) -> str:
    example_tags = (
        "a",
        "blockquote",
        "br",
        "code",
        "div",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "img",
        "li",
        "ol",
        "p",
        "pre",
        "section",
        "span",
        "strong",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
    )
    tag_pattern = "|".join(example_tags)
    pattern = re.compile(rf"(?<![`\\])</?(?:{tag_pattern})(?:\s+[^<>`]*?)?>", re.I)

    def protect_line(line: str) -> str:
        stripped = line.lstrip()
        if (
            not stripped
            or stripped.startswith(("```", "|", "!", ">"))
            or re.match(r"^#{1,6}\s", stripped)
            or re.match(r"^\s*</?(?:table|tr|td|th|div|section|p)\b", line, re.I)
        ):
            return line
        return pattern.sub(lambda m: f"`{m.group(0)}`", line)

    return "\n".join(protect_line(line) for line in value.splitlines())


def normalize_ordered_text(value: str) -> str:
    circled = {
        "①": "1.",
        "②": "2.",
        "③": "3.",
        "④": "4.",
        "⑤": "5.",
        "⑥": "6.",
        "⑦": "7.",
        "⑧": "8.",
        "⑨": "9.",
        "⑩": "10.",
    }
    text = value.replace("（", "(").replace("）", ")")
    for source, target in circled.items():
        text = text.replace(source, target)
    text = re.sub(r"(?m)^([ \t]*)(\d+)、", r"\1\2. ", text)
    text = re.sub(r"(?m)^([ \t]*\(\d+\))", lambda m: m.group(1).replace("(", "(").replace(")", ")"), text)
    text = re.sub(r"\n{2,}(?=[ \t]*(?:\d+\.|\(\d+\)))", "\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.replace("q̃ * m", "q̃_m").replace("R * {n−m}", "R_{n−m}")
    return text


def normalize_block_spacing(value: str) -> str:
    text = value
    text = re.sub(r"\n{2,}(\s*!\[[^\n]*\]\([^)]+\))", r"\n\1", text)
    text = re.sub(r"(\s*!\[[^\n]*\]\([^)]+\))\n{2,}", r"\1\n", text)
    text = re.sub(r"\n{2,}(```[^\n]*\n)", r"\n\1", text)
    text = re.sub(r"(\n```\s*)\n{2,}", r"\1\n", text)
    text = re.sub(r"\n{2,}(\$\$\n)", r"\n\1", text)
    text = re.sub(r"(\n\$\$\n)\n{2,}", r"\1", text)
    text = re.sub(r"(?m)^(\$\$)\n(.+?)\n\$\$\n\n", r"\1\n\2\n$$\n", text)
    return text


def downgrade_body_headings(value: str) -> str:
    lines = []
    last_major = ""
    for line in value.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            level = max(3, min(4, len(match.group(1))))
            title = normalize_heading_number(match.group(2).strip())
            if re.match(r"^\d+\.\d+(?:\.\d+)*\s+", title):
                level = 4
                last_major = title.split(".", 1)[0]
            elif re.match(r"^\d+\.\s+", title):
                current_num = int(title.split(".", 1)[0])
                heading_text = title.split(".", 1)[1].strip()
                if last_major and current_num != int(last_major) and len(heading_text) <= 90:
                    title = f"{last_major}.{current_num} {heading_text}"
                    level = 4
                else:
                    level = 3
                    last_major = str(current_num)
            lines.append("#" * level + f" {title}")
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def normalize_heading_number(value: str) -> str:
    chinese = re.match(r"^([一二三四五六七八九十]+)[、.．]\s*(.+)$", value)
    if chinese:
        number = chinese_numeral_to_int(chinese.group(1))
        if number:
            return f"{number}. {chinese.group(2).strip()}"
    arabic = re.match(r"^(\d+)[、．]\s*(.+)$", value)
    if arabic:
        return f"{arabic.group(1)}. {arabic.group(2).strip()}"
    return value.strip()


def chinese_numeral_to_int(value: str) -> int | None:
    mapping = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
    }
    if value in mapping:
        return mapping[value]
    if value.startswith("十") and len(value) == 2 and value[1] in mapping:
        return 10 + mapping[value[1]]
    if value.endswith("十") and len(value) == 2 and value[0] in mapping:
        return mapping[value[0]] * 10
    if "十" in value and len(value) == 3 and value[0] in mapping and value[2] in mapping:
        return mapping[value[0]] * 10 + mapping[value[2]]
    return None


def parse_date(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)) or str(value).isdigit():
        raw = int(value)
        if raw > 10_000_000_000:
            raw //= 1000
        try:
            return dt.datetime.fromtimestamp(raw, tz=dt.timezone.utc).astimezone().date().isoformat()
        except Exception:
            return ""
    text = str(value).strip()
    match = re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", text)
    return match.group(0).replace("/", "-") if match else text[:20]


def yaml_quote(value: Any) -> str:
    text = "" if value is None else str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def clean_inline(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def infer_fence_language(value: str) -> str:
    text = (value or "").strip()
    compact = re.sub(r"\s+", " ", text)
    if re.search(r"(?m)^\s*graph\s+(TB|TD|BT|LR|RL)\b|^\s*sequenceDiagram\b|^\s*flowchart\s+", text):
        return "mermaid"
    if re.search(r"\b(async\s+def|def|class)\s+\w+|from\s+\S+\s+import\s+|import\s+\S+|return\s+", text):
        return "python"
    if re.search(r"\b(async\s+function|function|const|let|=>|interface|fetch\s*\(|JSON\.stringify|TextDecoder|crypto\.randomUUID)\b", text):
        return "typescript" if "interface " in text else "javascript"
    if re.search(r"\b(curl|grep|docker|kubectl|npm|pnpm|git\s+|pytest|uvicorn)\b", text):
        return "bash"
    if re.search(r"\b(SELECT|CREATE\s+TABLE|INSERT\s+INTO|UPDATE\s+\w+\s+SET)\b", text, re.I):
        return "sql"
    if re.match(r"^[\[{]", text) and re.search(r'"[^"\n]+"\s*:', text):
        return "json"
    if re.search(r"(?m)^\s*[\w.-]+:\s+\S+", text) and "\n" in text:
        return "yaml"
    if re.search(r"\b(__global__|cudaMalloc|#include|std::)\b", text):
        return "cpp"
    if len(compact) > 240 or "\n" in text:
        return "text"
    return "text"


def safe_text(value: str, fallback: str) -> str:
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value).strip()
    text = re.sub(r"\s+", " ", text)
    return text or fallback


def safe_filename_part(value: str, fallback: str) -> str:
    text = safe_text(value, fallback)
    text = re.sub(r"\s+", "_", text)
    return text[:90].rstrip("._ ") or fallback


def infer_bundle_summary(articles: list[Article]) -> str:
    titles = [clean_inline(article.title) for article in articles if article.title]
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
    if re.search(r"Prefill|Decode|KV\s*Cache|GEMM|GEMV|compute[-\s]?bound|memory[-\s]?bound|推理", joined, re.I):
        topics.append("推理算法")
    if re.search(r"CNN|卷积|MobileNet|ShuffleNet|SqueezeNet|ResNet|LeNet|AlexNet|VGG", joined, re.I):
        topics.append("CNN")
    if re.search(r"轻量化|小模型|模型压缩|剪枝|量化|蒸馏", joined, re.I):
        topics.append("轻量化模型")

    if topics:
        if "大模型" in topics and "推理算法" in topics and re.search(r"Decode", joined, re.I):
            return "大模型Decode推理"
        if "大模型" in topics and "推理算法" in topics:
            return "大模型推理算法"
        if "CNN" in topics and "轻量化模型" in topics:
            return "CNN基础与轻量化模型"
        if "大模型" in topics and "架构" in topics and "注意力机制" in topics:
            return "大模型架构与注意力机制"
        return "与".join(unique(topics[:3]))

    cleaned_titles = [strip_title_prefix(title) for title in titles]
    prefix = common_chinese_prefix(cleaned_titles)
    if 4 <= len(prefix) <= 18:
        return prefix

    tokens: list[str] = []
    for title in cleaned_titles:
        tokens.extend(token for token in split_query_tokens(title) if not re.fullmatch(r"\d+", token))
    if tokens:
        return "与".join(unique(tokens)[:3])[:24]
    return clean_inline(cleaned_titles[0])[:24] or "AI总结内容"


def strip_title_prefix(title: str) -> str:
    text = clean_inline(title)
    return re.sub(r"^(大模型|算法专栏|AI|AIGC|LLM|Agent)[：:丨｜\-\s]+", "", text, flags=re.I).strip() or text


def common_chinese_prefix(values: list[str]) -> str:
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


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", "", clean_inline(value)).lower()


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def split_query_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[\s:：，,。；;、+\-_/｜|（）()【】\[\]《》]+", value) if len(token) >= 2]


def today() -> str:
    return dt.date.today().isoformat()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
