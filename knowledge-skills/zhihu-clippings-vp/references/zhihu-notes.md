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

Use `ContentText` as the clipping body/description. Convert `EditTime` from Unix timestamp to `YYYY-MM-DD`.

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

## Removed Browser Mode

Browser scraping is removed from this skill. Do not reintroduce Playwright, cookies, captcha handling, profile-page scraping, or undocumented web APIs unless the user explicitly asks for a separate non-official scraping skill.
