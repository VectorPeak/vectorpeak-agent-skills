# Explanation Style

Use this reference when producing deep explanations, learning notes, glossaries, or project reports.

## Preferred Explanation Shape

Start with the whole picture, then zoom in:

1. What problem this concept solves
2. Where it sits in the project
3. How it works internally
4. What it is often confused with
5. What can go wrong in practice

Do not start with a narrow textbook definition unless the user explicitly asks for one.

## Analogy and Contrast

Use analogy when it reduces cognitive load:

- BM25: a careful keyword librarian
- Embedding retrieval: a semantic map
- Fine-tuning: teaching a generalist a company-specific job
- Hard negative: a wrong answer that looks dangerously plausible

Use contrast to define boundaries:

- Classification answers "what category is this"
- Retrieval answers "what similar evidence exists"
- RAG answers "what should a language model say using retrieved evidence"

## Mathematical Supplements

Use LaTeX only for helpful precision.

Good examples:

```latex
f(x) \rightarrow y
```

for classification

```latex
sim(a, p) > sim(a, n)
```

for contrastive learning

```latex
L = L_1 + \lambda L_2
```

for weighted multi-task loss

## Unknown Unknowns

For important concepts, include one or two things the user may not realize they need to check:

- Label leakage
- Synthetic-data template bias
- Train/test split leakage
- Metric mismatch
- Retrieval evaluation bias toward keyword methods
- Large file storage and Git history bloat
- Confusing raw noisy labels with clean semantic classes

## Tone

Use Chinese when the user uses Chinese. Be pragmatic, precise, and project-aware.

Avoid empty phrases like "this is very important" unless explaining why.
