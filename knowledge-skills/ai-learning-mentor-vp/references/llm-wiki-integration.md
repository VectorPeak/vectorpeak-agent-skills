# LLM Wiki Integration

Use this reference when the user asks to connect learning to LLM_wiki, use known concepts, build a knowledge graph, or generate Wiki candidates.

## Read Priority

1. `05.Mentor/30_active_learning_dashboard.md` - current active tracks, weak points, next actions.
2. `05.Mentor/mastery/` - concept or skill mastery cards.
3. `02.wiki/concepts/` - durable concept notes.
4. `05.Mentor/question_bank/` - questions, wrong-answer patterns, interview variants.
5. `05.Mentor/20_session_index.md` - compressed session history.
6. `01.raw/02.DailyNotes/` - raw learning trace.
7. `02.wiki/projects/`, `02.wiki/entities/`, `02.wiki/decisions/`, `02.wiki/reviews/` - use when project/entity/decision context matters.

## Read Rules

- Use local matches as evidence, not decoration.
- Cite local paths in the answer when using local knowledge.
- If multiple local notes conflict, state the conflict and avoid silently choosing one.
- If no local note is found, say so and proceed with general CS/AI knowledge.

## Wiki Candidate Rules

Use `02.wiki/` only for stable conceptual knowledge.

Suggest a Wiki candidate when:

- The concept is reusable across future learning.
- It has multiple links to existing concepts.
- It clarifies a recurring confusion or weak point.
- It is mature enough to be more than a raw DailyNotes fragment.

Candidate format:

```markdown
## Wiki Candidate
- 是否建议进入 wiki 层：yes/no
- 建议位置：`02.wiki/concepts/<Concept>.md`
- 建议类型：new note / update existing note / add backlink / add misconception
- 建议 wikilinks：
  - [[...]]
- 建议写入内容：
```

Do not write to wiki files unless the user explicitly asks.

## Layer Boundary

- DailyNotes: raw trace of what happened today.
- Mentor sessions/index/dashboard: learning process, weak points, next actions.
- Mastery/question bank: review and practice assets.
- Wiki: durable conceptual graph.