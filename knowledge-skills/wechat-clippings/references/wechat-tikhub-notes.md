# WeChat TikHub Notes

## Scope

This skill targets arbitrary WeChat Official Account articles through TikHub. It is different from WeChat Official Account owner APIs, which are mainly for managing the authenticated account's own materials, drafts, and publishing workflow.

## Public TikHub Documentation Checked

TikHub currently exposes WeChat public-account documentation pages for:

- `GET /api/v1/wechat_mp/web/fetch_search_official_account`
- `GET /api/v1/wechat_mp/web/fetch_official_account_detail`
- `GET /api/v1/wechat_mp/web/fetch_mp_article_list`
- `GET /api/v1/wechat_mp/web/fetch_search_article`
- `GET /api/v1/wechat_mp/web/fetch_mp_article_detail_json`
- `GET /api/v1/wechat_mp/web/fetch_mp_article_detail_html`

The documentation is under:

```text
https://docs.tikhub.io/
```

Use the script defaults first. If an endpoint response changes, inspect the cached JSON in the skill cache directory and adjust field extraction rather than guessing.

The TikHub docs note that WeChat search resources are limited and recommend client-side retries. Use retry settings and avoid tight repeated calls.

## Input Strategy

User input may include:

- Official account name.
- Author/person name.
- Article title or title fragment.
- Direct `https://mp.weixin.qq.com/s/...` URL.
- Screenshot OCR text with visible titles.
- Copied public-account page text.

Prefer direct article URLs when present. Otherwise combine account clue and title clues to search candidate articles. For screenshot input, extract visible article titles into a UTF-8 text file and pass it through `--title-source`.

## Cost Control

TikHub bills successful requests and some failed attempts can still consume time or quota. Prefer the lowest-discovery input available:

1. Direct `mp.weixin.qq.com` article URLs: usually one HTML detail call per article.
2. Known `gh_...` account id plus target titles: article-list pagination plus detail calls.
3. Account name plus screenshot/OCR titles: account search plus article-list pagination plus detail calls.
4. Broad author/topic-only clues: highest uncertainty and highest likely call count.

Avoid speculative endpoint combinations. Do not retry nonrecoverable 400/401/403/404/422 responses.

## Recommended Resolution Path

After the 2026-05-26 live test on `AI编程实验室`, the most reliable path is:

1. Search official account with `fetch_search_official_account`.
2. Use `jumpInfo.userName` as `ghid`; it has the `gh_...` shape and worked with `fetch_mp_article_list`.
3. Do not use `__biz`, numeric `bizuin`, or base64 `Mz...` ids as the first article-list id. They returned `gzid错误` in the live test.
4. Fetch article list pages with `ghid` and `offset`.
5. The next page token is `data.offset.Offset`; stop when `data.offset.IsEnd == 1`.
6. Match requested articles against list records by exact title or strong keywords from screenshot/OCR.
7. Use list records as candidates only. Call detail endpoints for final body.
8. Use `fetch_mp_article_detail_html` first for normal clipping. HTML returned full content for all four live-test articles when JSON returned 400.
9. Extract `#js_content` from HTML and remove WeChat UI chrome before writing Markdown.

Direct long-title `fetch_search_article` can return 400 even for real articles. Treat it as a secondary fallback, not the main route for screenshot title batches.

## Output Strategy

Write Markdown for reading and long-term knowledge storage:

- Clean the article body before adding metadata.
- Keep body headings natural, but normalize top article headings to `## 0x01. ...`.
- Preserve image URLs when available.
- Keep source URL in frontmatter.
- Do not include API response dumps in Markdown output.
- Remove WeChat UI chrome such as `继续滑动看下一个`, `微信扫一扫`, `允许`, `取消`, and `知道了`.
- Remove tail QR/contact promotion blocks such as `欢迎关注`, `加我微信`, `交个朋友`, `二维码`, `扫码` plus the following QR/contact-card image. Use LLM judgment when a promotional tail cannot be identified by simple patterns.
- Normalize link labels: `xxx地址: https://...` or `xxx地址:` followed by a URL should become `[xxx地址](https://...)`.
- Normalize inline Markdown emphasis from HTML: `** 关键词 **` should become `**关键词**`.
- Remove the blank line immediately after article-internal `###` to `#####` headings.
- Remove extra blank lines immediately around Markdown images, fenced code blocks, and `$$` display math blocks.
- Remove standalone empty list items such as `-` lines.

## Compliance Boundary

Use the output for personal knowledge management. Do not bypass access controls, login walls, paywalls, captcha, or copyright restrictions. If an article is unavailable from TikHub, report the limitation instead of scraping a logged-in browser session.
