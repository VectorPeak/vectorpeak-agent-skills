# Cache And Corpus Contract

## Directory Choice
Default to a workspace-local staging directory:

```text
<workspace>/.codex-work/source-corpus/<slug>-<yyyymmdd-hhmmss>/
```

Reasons:

- Keeps paid/raw provider responses close to the task that created them.
- Avoids bloating the skill directory with temporary corpora.
- Avoids polluting permanent clipping or blog directories before QA.
- Makes concurrent runs safe because every task has a unique folder.

Use ASCII slugs for folder and file names on Windows. Keep Chinese inside file contents, not necessarily in file names, because some PowerShell/Python paths can become mojibake.

## Required Files
For every nontrivial fetch, create:

```text
cache/
  provider raw responses, one file per request/page/detail call
out/
  source-corpus-clean.md
  source-corpus-raw.json
notes/
  matching-decisions.md
```

`source-corpus-clean.md` is the file used by downstream writing/rewrite skills.

`source-corpus-raw.json` should contain one object per source item:

```json
{
  "platform": "zhihu",
  "source": "https://www.zhihu.com/question/656512469/answer/1994134127503496676",
  "title": "如何让大语言模型输出JSON格式？",
  "author": "Soulflare",
  "id": "1994134127503496676",
  "parent_id": "656512469",
  "published": "",
  "updated": "",
  "voteup_count": 409,
  "comment_count": null,
  "content_need_truncated": false,
  "content_html": "<p>...</p>"
}
```

## Matching Notes
Record how screenshots were resolved:

- visible title/question
- visible author
- visible vote/comment count
- distinctive first paragraph
- distinctive section headings
- final matched URL/id
- rejected candidates when ambiguity mattered

## QA Checklist
Before handing off a corpus:

- All requested items appear in clean Markdown.
- Raw JSON/HTML exists for every item.
- Every item has a source URL.
- No `content_need_truncated: true`.
- Markdown is readable UTF-8.
- No provider debug dict/list stringification.
- No API key or secret is present.
- Any image/formula/table loss is noted.

## Retention
Task-local cache is temporary by default. Keep it during the current writing/rewrite workflow. When the user approves a final article, keep only the clean corpus and raw metadata if they are useful for reproducibility; otherwise the staging folder can be deleted later.
