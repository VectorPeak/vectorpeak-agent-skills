---
name: project-concept-explainer-vp
description: Explain project-specific concepts, technical terms, models, algorithms, configuration items, dataset fields, architecture decisions, and codebase terminology while working in a repository. Use when the user asks to explain a term, understand a project, generate a project knowledge map, build a glossary, compare related concepts, clarify technologies in README/docs/scripts/configs/notebooks/reports, or study key project ideas top-down.
---

# Project Concept Explainer

## Overview

Use this skill as a project companion for technical learning. It helps explain important project-specific concepts and can generate a project knowledge map from repository files.

Prefer Chinese when the user communicates in Chinese. Keep explanations grounded in the current project, not generic encyclopedia summaries.

## Mode Selection

Choose one mode from the user's request:

1. **Term Explanation Mode**: Use when the user asks about one or several concepts, such as "BM25 是什么", "解释 train_config.yaml 里的 warmup", or "这个项目里的多任务分类是什么意思"
2. **Knowledge Map Mode**: Use when the user asks to understand the project, scan key concepts, generate a glossary, summarize technical terms, or produce learning notes
3. **Comparison Mode**: Use when the user asks for differences, trade-offs, "A 和 B 有什么区别", or "为什么不用另一个方案"
4. **Report Mode**: Use when the user wants a reusable Markdown document, such as a project concept map, glossary, or research note

## Context Gathering

Before explaining project-specific concepts, inspect the repository lightly:

- Read `README.md`, `AGENTS.md`, `docs/`, `data/reports/`, `configs/`, and relevant `scripts/` when present
- Prefer `rg --files` and targeted reads over broad file dumps
- If the concept comes from a specific file, cite the file path and line when practical
- If the project does not contain enough evidence, say what is inferred and what is uncertain

Do not over-scan. Load only enough context to answer the user's question.

## Explanation Structure

For important concepts, use this structure unless the user asks for a very short answer:

1. **One-sentence intuition**: Explain what it does in plain language
2. **Project role**: Explain why it appears in this specific project
3. **Formal definition**: Give a precise definition, using math when helpful
4. **Nearby concepts**: Compare related, opposite, or easily confused concepts
5. **Concrete example**: Use an example from the project or a realistic project-shaped example
6. **Common traps**: Mention misconceptions, failure modes, or "unknown unknowns"
7. **Next action**: Suggest what the user should inspect, test, or build next when useful

For formulas, keep the math minimal and practical. Use LaTeX only when it clarifies the idea.

## Knowledge Map Workflow

When generating a project knowledge map:

1. Identify the project domain and main workflow
2. Group concepts into layers:
   - Business/domain concepts
   - Data and labels
   - Cleaning and preprocessing
   - Models and algorithms
   - Training and evaluation
   - Retrieval/RAG
   - Application/API/frontend
   - Git/GitHub/dev workflow
3. For each concept, include:
   - Name
   - Short explanation
   - Why it matters in the project
   - Related files or directories when available
4. Separate "must understand now" from "can learn later"
5. If writing a report, save it under `docs/` or the user-specified location

Read `references/concept_categories.md` before creating a full knowledge map.

## Comparison Workflow

When comparing concepts:

- Explain the shared parent concept first
- Show the key difference in one sentence
- Use a compact table for trade-offs
- State which one fits the current project better and why
- Include failure cases where choosing the wrong one matters

Example comparisons:

- BM25 vs dense retrieval
- BERT classification vs RAG retrieval
- random negative vs hard negative
- training from scratch vs fine-tuning
- raw label count vs cleaned label count

## Style Guide

Read `references/explanation_style.md` when the user asks for a deep explanation, learning note, glossary, or report.

Default style:

- Explain top-down
- Use analogies and contrasts
- Stay pragmatic and project-grounded
- Avoid vague textbook answers
- Call out uncertainty and assumptions
- Prefer concise Chinese explanations when the user uses Chinese

## Output Rules

- Link local files with clickable absolute paths when referencing repository files
- Do not invent project facts; inspect files or label claims as inference
- Do not create or modify files unless the user asks for a report, note, glossary, or persistent artifact
- If creating a Markdown artifact, use UTF-8
- Keep the final answer focused; put detailed reusable explanations in files when they are long
