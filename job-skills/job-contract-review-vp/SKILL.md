---
name: job-contract-review-vp
description: Review job-related contracts or pasted contract text for red flags, warnings, protective clauses, missing protections, fairness score, and negotiation suggestions. Use when the user provides PDF, DOCX, TXT, MD, RTF, or pasted text for employment agreements, offer letters, NDAs, contractor agreements, freelance agreements, internship agreements, non-competes, severance terms, or asks for practical contract risk review.
---

# Job Contract Review

## Purpose

Review job-related contracts from the likely signing party's perspective. Convert files to text, identify contract type, force structured analysis, validate the structure, and render a practical Markdown report.

Default to Chinese for summaries, explanations, suggestions, missing protections, negotiation points, disclaimers, and final Markdown reports. Preserve exact contract quotes in the original contract language.

This skill follows a fixed review workflow: extract document text, analyze against a strict schema, validate the JSON, then render a report.

## Workflow

1. If the user provides a file, extract text with `scripts/extract_contract_text.py`.
2. If the user pasted contract text, save it to a temporary `.txt` only when a script needs a file input.
3. Read `references/review_prompt.md` and use it as the analysis contract.
4. Read `references/contract_type_checks.md` for contract-type-specific risks and missing-protection checks.
5. Have Codex perform the contract analysis directly from the extracted text and produce JSON only, matching `schemas/contract_review.schema.json`. Use Chinese for generated content except exact quotes and schema enum values.
6. Validate the JSON with `scripts/validate_contract_review.py`.
7. If validation fails, ask the LLM to repair the JSON only; do not change the source contract text.
8. Render the final Markdown report using `scripts/render_contract_report.py`, or render directly from the validated JSON when needed.
9. Include a concise legal disclaimer: this is AI-assisted review, not legal advice.

## Analysis Responsibility

Codex performs the risk analysis. Do not require the user to configure OpenAI, OpenRouter, Claude, Kimi, Ollama, or any other external model provider just to use this skill.

The bundled scripts handle deterministic work:

- file text extraction
- JSON validation
- Markdown rendering

Codex handles judgment work:

- identifying red flags
- distinguishing warnings from severe risks
- recognizing protective clauses
- spotting missing protections
- assigning fairness score and grade
- writing negotiation suggestions

This skill does not ship a standalone legal rule engine. If the user asks for fully offline local-model execution, explain that extraction, validation, and rendering scripts are offline, but legal-risk judgment still needs Codex or another capable LLM.

## Optional Multi-Agent Review

Use multi-agent review only when the user explicitly allows it, the contract is long/high-value/high-risk, or an independent second pass would materially reduce risk.

Recommended split:

1. Primary reviewer: identify contract type, key terms, red flags, warnings, protections, missing protections, and draft the review JSON.
2. Adversarial reviewer: look only for missed risks, overclaims, weak clause references, jurisdiction assumptions, and missing protections.
3. Synthesizer: merge findings, remove duplicates, keep only defensible issues, validate JSON, and render the final report.

Do not give sub-agents hidden expected answers. Pass the extracted contract text or relevant raw chunks, not a prewritten diagnosis.

## File Extraction

Use:

```bash
python scripts/extract_contract_text.py \
  --input "<contract-file>" \
  --output "<contract.extracted.json>"
```

Supported inputs:

- `.pdf`: use `pdfplumber`, preserve page labels.
- `.docx`: use `python-docx`, preserve paragraph and table order.
- `.txt`, `.md`, `.rtf`: read text with UTF-8 first and fallback encodings.

If a PDF has no extractable text, report that it is likely scanned/image-based and needs OCR first.

## Review Dimensions

Always review these four dimensions:

- Red flags: severe clauses that can cause financial loss, legal exposure, loss of rights, one-sided obligations, or hard-to-escape commitments.
- Warnings: moderate risks worth negotiating but not necessarily deal breakers.
- Protections: clauses that help the signing party and should usually be preserved.
- Missing protections: common safeguards that are absent or materially incomplete.

Also produce:

- contract type
- parties
- key terms
- fairness score from 0 to 100
- fairness grade
- top negotiation points
- whether lawyer review is recommended

## Output Rules

For analysis, produce JSON first. Do not produce Markdown until the JSON validates. Generated JSON values should be Chinese by default, except `quote`, `contract_type`, `severity`, `fairness_grade`, and proper names that should remain as written.

For the user-facing report, prefer Markdown with Chinese section headings equivalent to:

1. Overall assessment
2. Key terms
3. Red flags
4. Warnings
5. Protections
6. Missing protections
7. Priority negotiation points
8. Lawyer review recommendation
9. Disclaimer

Quote only the shortest relevant contract excerpt for each issue. Keep suggestions concrete and negotiable.

## Safety Boundaries

- Do not claim to provide legal advice.
- Do not invent jurisdiction-specific law if the contract does not specify jurisdiction or the skill has not verified it.
- When jurisdiction matters, say what needs local legal confirmation.
- Do not overstate certainty; distinguish textual risk from legal enforceability.
- Do not upload or share contract contents unless the user explicitly asks and understands the privacy impact.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
