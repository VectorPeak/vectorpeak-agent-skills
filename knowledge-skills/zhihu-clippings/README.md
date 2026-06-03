# Zhihu Clippings

Zhihu Clippings is an agent skill for clipping Zhihu articles into Obsidian-friendly Markdown bundles. It uses the Zhihu Developer Platform for coarse positioning and identity verification, then can use TikHub to fetch fuller article or answer content when the official API only returns summaries.

## Scope

- Locate authors, articles, questions, or answers from names, URLs, titles, OCR text, or mixed clues
- Use the official Zhihu developer API for search and verification
- Use TikHub as a fulltext provider when available
- Preserve formulas, images, tables, code blocks, and heading hierarchy where possible
- Write Markdown bundles to `.\clippings` by default, or to a user-provided Obsidian vault folder

## Folder Layout

```text
zhihu-clippings/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── zhihu-notes.md
└── scripts/
    └── clip_zhihu_official.py
```

## Credentials

```powershell
[Environment]::SetEnvironmentVariable("ZHIHU_ACCESS_SECRET", "<access_secret>", "User")
```

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key>", "User")
```

Do not commit real API keys to this repository.

## Typical Commands

```powershell
python scripts\clip_zhihu_official.py "https://www.zhihu.com/people/example-author Some Author" --author "Some Author" --count 10 --ranges "1-5,6-10"
```

```powershell
python scripts\clip_zhihu_official.py "https://www.zhihu.com/people/example-author" --author "Some Author" --content-provider tikhub --user-url-token example-author --count 10
```

```powershell
python scripts\clip_zhihu_official.py "Some Author" --author "Some Author" --count 10 --output-dir ".\clippings\zhihu"
```

## Public Repository Notes

The default output directory is `.\clippings` so cloned copies do not depend on a personal Obsidian vault path.

Large generated Markdown files, raw API caches, and private vault contents should not be committed unless intentionally published as examples.
