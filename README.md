# VectorPeak Agent Skills

Personal agent skills by VectorPeak for software development and knowledge work.

This repository is a long-term home for reusable skills distilled from day-to-day work. A skill should capture a repeatable workflow, decision rule, checklist, or tool pattern that is worth using again, rather than a one-off prompt.

## Structure

```text
vectorpeak-agent-skills/
├── dev-skills/
│   └── README.md
├── knowledge-skills/
│   └── README.md
└── README.md
```

## Categories

### `dev-skills/`

Skills for engineering work: coding, debugging, testing, code review, architecture analysis, build fixes, release workflows, CI/CD, repository maintenance, and local automation.

### `knowledge-skills/`

Skills for knowledge work: top-down learning, concept explanation, note processing, paper reading, article summarization, knowledge-base organization, learning checks, and writing workflows.

## Skill Naming

Use short, lowercase, hyphen-separated names:

```text
debug-failing-build
review-pr-comments
explain-paper-top-down
extract-concept-map
```

Prefer names that describe the repeatable action, not the tool used internally.

## Skill Folder Convention

Each skill should live in its own folder:

```text
dev-skills/example-skill/
├── SKILL.md
├── scripts/
├── references/
└── templates/
```

Only `SKILL.md` is required. Add `scripts/`, `references/`, or `templates/` only when they make the skill easier to run and maintain.

## Quality Bar

A useful skill should answer:

- When should an agent use it?
- What exact workflow should the agent follow?
- What inputs does it need?
- What output should it produce?
- What should it avoid doing?

If a note cannot answer these questions yet, keep it as a draft before promoting it into a skill.
