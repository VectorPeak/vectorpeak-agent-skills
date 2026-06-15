# Zhihu Official API Notes

## Documentation Source

The Zhihu Developer Platform documentation is loaded by:

```text
https://developer.zhihu.com/console/api/v2/docs
```

The relevant official endpoint for this skill is:

```text
GET https://developer.zhihu.com/api/v1/content/zhihu_search
```

## Authentication

Requests must include:

```text
Authorization: Bearer <your_access_secret>
X-Request-Timestamp: <unix_seconds>
Content-Type: application/json
```

The Access Secret is available from:

```text
https://developer.zhihu.com/profile
```

## zhihu_search Parameters

Query parameters:

- `Query`: required string search query.
- `Count`: optional integer. Default is 10. The official documentation states the maximum is 10.

## Response Fields

`Data.Items[]` includes:

- `Title`
- `ContentType`
- `ContentID`
- `ContentText`
- `Url`
- `CommentCount`
- `VoteUpCount`
- `AuthorName`
- `EditTime`

Use `ContentText` only as official search summary/description. Do not treat it as complete final body when the user expects a full article or answer. Convert `EditTime` from Unix timestamp to `YYYY-MM-DD`.

## Author Search Strategy

The skill accepts flexible input:

- person name
- Zhihu people URL
- Zhihu article URL
- article title
- mixed author description

It first normalizes the input into a search query, infers the most likely `AuthorName` from official search results unless `--author` is provided, then runs author-centered probes such as:

- normalized input
- author name
- author name plus `文章`
- author name plus `知乎`
- author name plus `专栏`
- user-provided `--extra-query` values
- user-provided title probes from `--extra-query-file`
- discovered title probes from `--title-source`

It keeps only results where:

```text
AuthorName == target_author
ContentType == Article
```

It deduplicates by `ContentID` or URL and sorts by `EditTime` descending.

If a user provides a screenshot, copied page text, HTML file, or known profile page showing article titles, discover those titles and use them as exact extra queries. The official search endpoint can find title-specific records that broad author queries miss.

## Boundary

The official API is search-oriented. It does not provide a documented endpoint that takes a Zhihu `people` URL and returns that person's complete chronological article list. When users ask for "all articles by a person", treat the result as "all official API search results returned for the query and filters" unless a future official document adds a user timeline endpoint.

TikHub article detail and question-answer endpoints may produce final fulltext. Treat TikHub as third-party content, not official Zhihu verification. Direct `--article-id` or `--answer-id` fetches are allowed when the ID is already known, but they must be described as TikHub direct fetches unless official search also verifies the target.

## Markdown Output QA

Use a body-first clipping layout:

- YAML frontmatter is allowed for Obsidian metadata.
- Do not add an in-body document title, source note, author note, capture date, query list, or per-article metadata block.
- Do not add per-article utility metadata under article headings unless the user explicitly asks for it.
- Do not use level 1 headings in generated clipping bodies.
- Use level 2 headings only for each clipped Zhihu article or answer. Number them as `## 0x01. Title`, `## 0x02. Title`, and so on.
- Use level 3 headings for major sections inside one Zhihu article or answer.
- Use level 4 headings for subheads under major sections, including unnumbered subheads, single-number headings, and decimal headings.
- Use level 5 headings only for implementation variants or methods under a numbered subsection.
- Do not use Chinese article numbering for generated article headings. Convert major Chinese-numbered sections to Arabic numbering when needed, for example `### 1. Section title`.
- Do not leave a blank line after any heading level. A heading should be immediately followed by the next content line.
- Keep adjacent ordinary bullet-list items compact; do not insert blank lines between them.

After generating every Markdown file, make a second pass over fenced code blocks:

- Label all code fences when the language is inferable.
- Correct already labeled fences that are clearly wrong.
- Remove leaked inner language-marker lines such as standalone `python`, `text`, `java`, or extraction residue inside the code block.
- Do not leave real code as `text`.
- Prefer `java`, `python`, `sql`, `text`, `json`, `cpp`, `javascript`, `typescript`, `xml`, `yaml`, and `bash` where appropriate.
- JavaScript/TypeScript cues include `async function`, `const`, `let`, `fetch`, `JSON.stringify`, `TextDecoder`, `crypto.randomUUID`, and `=>`.
- Python cues include `def`, `class`, `import`, `from ... import`, `async def`, and `return`.
- Java cues include `@Service`, `@Configuration`, `@RestController`, `public class`, `List<...>`, and `RestTemplate`.
- If extracted code begins with leaked fence residue such as `'''text` or ```text, remove that marker and set the outer fence to the inferred language.

Preserve formulas, images, and tables when present:

- Convert Zhihu equation images to LaTeX `$...$` or `$$...$$` when the source makes the formula recoverable.
- Convert normal images to Markdown images.
- Convert HTML tables to Markdown tables.

Optional LLM review: pass `--llm-heading-review` to send only the extracted heading list to an OpenAI-compatible model for level corrections. The model must return JSON level changes and must not rewrite body text.

## Removed Browser Mode

Browser scraping is removed from this skill. Do not reintroduce Playwright, cookies, captcha handling, profile-page scraping, or undocumented web APIs unless the user explicitly asks for a separate non-official scraping skill.
