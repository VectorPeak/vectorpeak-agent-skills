# WeChat Clippings

WeChat Clippings is an agent skill for clipping public WeChat Official Account articles into Obsidian-friendly Markdown bundles through TikHub.

## Scope

- Locate articles from account names, article titles, OCR text, or `mp.weixin.qq.com` URLs
- Prefer direct article URLs when available to reduce API calls
- Fetch article detail through TikHub
- Convert article HTML into Markdown
- Write Markdown bundles to `.\clippings` by default, or to a user-provided Obsidian vault folder

TikHub is a third-party provider, not an official WeChat API. Response shape, quota, and coverage may change.

## Folder Layout

```text
wechat-clippings/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── wechat-tikhub-notes.md
└── scripts/
    └── clip_wechat_tikhub.py
```

## Credentials

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key>", "User")
```

Do not commit real API keys to this repository.

## Typical Commands

```powershell
python scripts\clip_wechat_tikhub.py "https://mp.weixin.qq.com/s/xxxx" --count 1 --ranges "1"
```

```powershell
python scripts\clip_wechat_tikhub.py "account name or article topic" --count 3
```

```powershell
python scripts\clip_wechat_tikhub.py "account name" --count 3 --output-dir ".\clippings\wechat"
```

## Public Repository Notes

The default output directory is `.\clippings` so cloned copies do not depend on a personal Obsidian vault path.

Large generated Markdown files, raw API caches, and private vault contents should not be committed unless intentionally published as examples.
