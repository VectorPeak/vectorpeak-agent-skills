# Paper Fetcher

Paper Fetcher is an agent skill for research paper intake. It helps an agent identify a paper from a title, screenshot text, URL, or excerpt; prefer official sources; download a verified PDF; rename it consistently; and report an arXiv ID or DOI for Zotero's Add Item by Identifier flow.

## Scope

This skill is intentionally conservative:

- Prefer official PDF sources
- Do not bypass paywalls or access controls
- Do not write Zotero local database files
- Do not store Zotero API credentials
- Do not create hand-written Zotero metadata through the Web API

## Folder Layout

```text
paper-fetcher/
├── SKILL.md
├── README.md
├── scripts/
│   └── paper_postprocess.py
├── examples/
│   ├── arxiv-paper.example.json
│   └── openreview-paper.example.json
└── tests/
    └── test_paper_postprocess.py
```

## Postprocess CLI

After the agent downloads a PDF, run:

```bash
python scripts/paper_postprocess.py \
  --pdf "<downloaded-pdf>" \
  --target-dir "<research-folder>" \
  --title "Paper Title" \
  --field Agent \
  --arxiv-id "2401.00001" \
  --doi "10.1234/example.paper" \
  --source-url "https://example.org/paper.pdf" \
  --zotero
```

Supported fields:

```text
RAG
Agent
SFT
RL
DL_Frameworks
Other
```

Use `--dry-run` to preview the output path without moving or writing files.

## JSON Output

The script emits JSON by default:

```json
{
  "field": "Agent",
  "final_name": "Agent_Example Paper.pdf",
  "saved_path": "<research-folder>/Agent_Example Paper.pdf",
  "pdf_verified": true,
  "dry_run": false,
  "identifier": "2401.00001",
  "zotero_status": {
    "status": "identifier_available",
    "identifier": "2401.00001"
  }
}
```

## Tests

```bash
python -m pytest tests
```

The tests are offline and cover filename sanitization, field validation, duplicate names, PDF header checks, dry-run behavior, and identifier priority.
