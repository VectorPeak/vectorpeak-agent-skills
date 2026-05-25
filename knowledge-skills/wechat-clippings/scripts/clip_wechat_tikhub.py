#!/usr/bin/env python
"""Clip WeChat Official Account articles through TikHub into Markdown bundles."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
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

DEFAULT_OUTPUT_DIR = Path.cwd() / "Clippings"
DEFAULT_CACHE_DIR = DEFAULT_OUTPUT_DIR / ".llmwiki-cache" / "wechat-clippings"
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


class BodyHTMLParser(HTMLParser):
    BLOCK_TAGS = {"p", "div", "section", "article", "blockquote", "pre", "ul", "ol", "li", "table", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.link_stack: list[str] = []
        self.list_depth = 0
        self.in_pre = False
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag in {"script", "style", "svg"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
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
            self.parts.append("\n```text\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "svg"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
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
            self.parts.append("\n```\n")
        elif tag in self.BLOCK_TAGS or tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        self.parts.append(data if self.in_pre else re.sub(r"\s+", " ", data))

    def markdown(self) -> str:
        text = html.unescape("".join(self.parts))
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\n(- .+)\n\n(?=- )", r"\n\1\n", text)
        return text.strip()

    def _newline(self) -> None:
        if self.parts and not "".join(self.parts[-2:]).endswith("\n"):
            self.parts.append("\n")


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
    parser.add_argument("--filename-template", default="微信_{author}_公众号文章剪藏_{date}_{range}.md")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for Markdown bundle files.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Directory for raw API response cache.")
    parser.add_argument("--tikhub-api-key", default=None, help="TikHub API key. Defaults to TIKHUB_API_KEY.")
    parser.add_argument("--base-url", default=TIKHUB_BASE_URL, help="TikHub base URL.")
    parser.add_argument("--account-search-path", default=DEFAULT_ACCOUNT_SEARCH_PATH)
    parser.add_argument("--article-search-path", default=DEFAULT_ARTICLE_SEARCH_PATH)
    parser.add_argument("--article-list-path", default=DEFAULT_ARTICLE_LIST_PATH)
    parser.add_argument("--article-detail-path", action="append", default=list(DEFAULT_ARTICLE_DETAIL_PATHS))
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
    if not account_ids and args.author:
        account_ids.extend(search_accounts(args, key, args.author, cache_dir))

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
    headers = {"Authorization": f"Bearer {key}", "User-Agent": "wechat-clippings/1.0"}
    last_error: Exception | None = None
    for attempt in range(1, args.retry + 1):
        try:
            request = Request(full_url, headers=headers)
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            cache_response(cache_dir, path, clean_params, data)
            return data
        except HTTPError as exc:
            last_error = exc
            if exc.code in {400, 401, 403, 404, 422}:
                break
            if attempt < args.retry:
                time.sleep(args.retry_delay * attempt)
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < args.retry:
                time.sleep(args.retry_delay * attempt)
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
    html_body = find_longest_html(data)
    if html_body:
        content = html_to_markdown(html_body)
        if content:
            return Article(
                title=fallback.title or "未命名公众号文章",
                author=fallback.author or "微信公众号",
                url=fallback.url,
                published=fallback.published,
                content=content,
                raw=fallback.raw,
            )
    best: dict[str, Any] = {}
    for item in iter_dicts(data):
        if any(key in item for key in ("content", "html", "article_content", "content_html", "title")):
            best = item
            break
    title = clean_inline(first_str(best, ["title", "appmsg_title", "name"]) or fallback.title or "未命名公众号文章")
    author = clean_inline(first_str(best, ["author", "nickname", "account_name", "source"]) or fallback.author or "微信公众号")
    url = first_str(best, ["url", "article_url", "link", "content_url", "appmsg_url"]) or fallback.url
    raw_content = first_str(best, ["content", "html", "article_content", "content_html", "text", "ori_content", "Content"]) or fallback.content
    content = html_to_markdown(raw_content) if looks_like_html(raw_content) else clean_markdown(raw_content)
    return Article(
        title=title,
        author=author,
        url=url,
        published=parse_date(first_present(best, ["publish_time", "create_time", "datetime", "date", "time", "send_time"])) or fallback.published,
        content=content,
        raw=best or fallback.raw,
    )


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
    return [article for score, _, article in scored if score > 0] or articles


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
    return "" if value is None else str(value).strip()


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
        filename = args.filename_template.format(author=safe_filename_part(author, "wechat"), date=today(), range=label)
        path = output_dir / safe_text(filename, "wechat-clippings.md")
        path.write_text(render_bundle(selected, author, label, len(articles)), encoding="utf-8")
        written.append(path)
    return written


def render_bundle(articles: list[Article], author: str, label: str, total: int) -> str:
    title = f"微信_{author}_公众号文章剪藏_{today()}_{label}"
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
        numeral = CHINESE_NUMERALS[index] if index < len(CHINESE_NUMERALS) else str(index)
        lines.append(f"## {numeral}、{article.title or '未命名公众号文章'}")
        lines.append("")
        if article.published or article.url:
            if article.published:
                lines.append(f"> 发布日期：{article.published}  ")
            if article.url:
                lines.append(f"> 原文链接：[{article.title or '原文'}]({article.url})")
            lines.append("")
        body = article.content.strip() or f"> 未能从 TikHub 详情接口解析到正文。原文链接：{article.url}"
        lines.append(downgrade_body_headings(body))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


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
        r"^\s*(微信扫一扫|关注该公众号|使用小程序|取消|允许|分析|收藏|听过)\s*$",
        r"^\s*\[?\s*(取消|允许|知道了)\s*\]?",
        r"^\s*×\s*分析\s*$",
        r"^\s*>?\s*/\s*作者[:：].*$",
    ]
    raw_lines = value[:cut].splitlines()
    index = 0
    while index < len(raw_lines):
        line = raw_lines[index]
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


def clean_markdown(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = normalize_inline_markdown(text)
    return text.strip()


def normalize_inline_markdown(value: str) -> str:
    text = re.sub(r"\*\*\s+([^*\n]+?)\s+\*\*", lambda m: f"**{m.group(1).strip()}**", value)
    text = re.sub(r"(?<!\*)\*\s+([^*\n]+?)\s+\*(?!\*)", lambda m: f"*{m.group(1).strip()}*", text)
    text = re.sub(r"(\*\*[^*\n]+\*\*)\s{2,}", r"\1 ", text)
    text = re.sub(r"\*\*([^\n*]+?)\*\*\s+([，。！？；：,.!?;:）)])", r"**\1**\2", text)
    text = re.sub(r"([。！？：:])!\[", r"\1\n\n![", text)
    text = re.sub(r"(###\s+[^\n]+)!\[", r"\1\n\n![", text)
    text = re.sub(r"^(#{3,5})\s+(.+)$", lambda m: f"{m.group(1)} {m.group(2).strip()}", text, flags=re.M)
    text = re.sub(r"^(#{3,5}\s+.+?)\s*\n{2,}(?=[ \t]*[^\s#!])", r"\1\n", text, flags=re.M)
    text = normalize_block_spacing(text)
    text = re.sub(r"(?m)^[ \t]*-[ \t]*\n", "", text)
    text = re.sub(r"\s{2,}([，。！？；：,.!?;:）)])", r"\1", text)
    return text


def normalize_block_spacing(value: str) -> str:
    text = value
    text = re.sub(r"\n{2,}(\s*!\[[^\n]*\]\([^)]+\))", r"\n\1", text)
    text = re.sub(r"(\s*!\[[^\n]*\]\([^)]+\))\n{2,}", r"\1\n", text)
    text = re.sub(r"\n{2,}(```[^\n]*\n)", r"\n\1", text)
    text = re.sub(r"(\n```\s*)\n{2,}", r"\1\n", text)
    text = re.sub(r"\n{2,}(\$\$\n)", r"\n\1", text)
    text = re.sub(r"(\n\$\$\s*)\n{2,}", r"\1\n", text)
    return text


def downgrade_body_headings(value: str) -> str:
    lines = []
    for line in value.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            level = max(3, min(5, len(match.group(1))))
            lines.append("#" * level + " " + match.group(2).strip())
        else:
            lines.append(line)
    return "\n".join(lines).strip()


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


def safe_text(value: str, fallback: str) -> str:
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value).strip()
    text = re.sub(r"\s+", " ", text)
    return text or fallback


def safe_filename_part(value: str, fallback: str) -> str:
    text = safe_text(value, fallback)
    text = re.sub(r"\s+", "_", text)
    return text[:90].rstrip("._ ") or fallback


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
