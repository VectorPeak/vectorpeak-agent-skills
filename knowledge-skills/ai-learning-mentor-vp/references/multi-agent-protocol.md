# Multi-Agent Protocol

Use this reference only when the user explicitly requests multi-agent work or when a learning task needs broad local retrieval plus synthesis.

## Roles

| Role | Responsibility | Output |
|---|---|---|
| Context Scout | Search LLM_wiki for known concepts, weak points, old sessions, local evidence | paths, snippets, uncertainties |
| Concept Tutor | Explain What / Why / How and interview answer | concise explanation |
| Feynman Examiner | Ask follow-up questions and grade learner output | gap list, interview risks |
| Analogy Mapper | Build known-concept diff analogies | analogy anchors, diff, failure boundary |
| Practice Coach | Generate and adapt drills | question set, grading rubric |
| Graph Synthesizer | Build landscape, relation table, Mermaid graph | graph and learning path |
| Memory Curator | Propose DailyNotes, mastery, question_bank, Wiki candidates | update candidates only |

## Coordination Rules

- Use one coordinator to merge all findings.
- Do not let every role write a final essay.
- Ask sub-agents for structured findings only.
- De-duplicate repeated concepts and links.
- Keep memory writes opt-in.

## Suggested Sub-Agent Output Shape

```markdown
## Findings

## Evidence / Local Paths

## Uncertainties

## Suggested Updates
```

## Mode-Specific Splits

### Analogy Learning

- Context Scout: find known concepts.
- Analogy Mapper: choose anchors and build diff.
- Concept Tutor: explain the resulting model.
- Memory Curator: propose DailyNotes/Wiki candidates.

### Knowledge Graph

- Context Scout: find existing nodes.
- Graph Synthesizer: build relation table and graph.
- Concept Tutor: explain key route.
- Memory Curator: suggest links and candidates.

### Deliberate Practice

- Context Scout: find weak points and old questions.
- Practice Coach: generate drills.
- Feynman Examiner: grade answers.
- Memory Curator: propose question_bank/mastery updates.