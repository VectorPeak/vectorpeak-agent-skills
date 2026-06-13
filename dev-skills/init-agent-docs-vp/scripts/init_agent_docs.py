#!/usr/bin/env python3
"""Initialize lightweight README.md, AGENTS.md, and progressive .docs files."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


BASE_FILES = {
    "README.md": """\
# Project

This repository is ready for project documentation. Update this README with the product purpose, setup instructions, and key links for human contributors.

## Agent Documentation

Coding-agent guidance starts in [AGENTS.md](AGENTS.md). Deeper project context is progressively disclosed through [.docs/](.docs/).
""",
    "AGENTS.md": """\
# Agent Guide

Use progressive disclosure. Read only the smallest document needed for the current task.

Keep this file under 300 lines. Move detailed guidance into `.docs/`.

## Read By Task

- Understand the project: `.docs/overview.md`
- Run, build, or configure locally: `.docs/development.md`
- Check early decisions and trade-offs: `.docs/decisions.md`

## Highest Priority Rules

- Preserve user changes.
- Do not overwrite existing files unless explicitly asked.
- Ask before destructive actions or broad dependency changes.
- Run relevant verification before claiming work is complete.
""",
    ".docs/overview.md": """\
# Overview

Use this document when you need project context before changing behavior.

## Purpose

- What problem does this project solve?
- Who uses it?
- What outcome should it create?

## Domain Terms

Add project-specific concepts, acronyms, and business rules here.

## Important Links

- Repository:
- Product/design notes:
- External docs:
""",
    ".docs/development.md": """\
# Development

Use this document when installing, running, building, linting, formatting, or configuring the project.

## Common Commands

- Install:
- Run:
- Build:
- Lint:
- Format:
- Test:

## Environment

- Required variables:
- Local services:
- Ports:
""",
    ".docs/decisions.md": """\
# Decisions

Use this document for early product, scope, naming, architecture, and trade-off decisions.

Keep decisions lightweight while the project is young. Split into `.docs/decisions/0001-*.md` only when this file becomes hard to scan or decisions need formal ADR-style history.

## Active Decisions

### YYYY-MM-DD: Decision Title

Decision:

Reason:

Status: proposed | accepted | superseded

## Open Questions

- 
""",
}


FULL_ONLY_FILES = {
    ".docs/architecture.md": """\
# Architecture

Use this document before making cross-module or architecture-sensitive changes.

## Structure

Describe the main directories, modules, and ownership boundaries.

## Data Flow

Describe how data moves through the system.

## External Systems

List APIs, databases, queues, storage, auth providers, or other integrations.

## Design Decisions

Record durable decisions that future agents should preserve.
""",
    ".docs/testing.md": """\
# Testing

Use this document when adding, fixing, or running tests.

## Commands

- Unit:
- Integration:
- End-to-end:
- All checks:

## Strategy

Describe what should be tested at each layer and which fixtures, mocks, or helpers are preferred.

## CI Notes

Document known CI behavior, flaky tests, timeouts, and required services.
""",
    ".docs/conventions.md": """\
# Conventions

Use this document when writing code, naming files, adding dependencies, or following local project patterns.

## Code Style

- Naming:
- Formatting:
- Error handling:
- Logging:

## Project Patterns

Document preferred helpers, abstractions, folder conventions, and framework-specific practices.

## Contributions

Document branch, commit, PR, or review conventions if they matter for this project.
""",
    ".docs/agent-boundaries.md": """\
# Agent Boundaries

Use this document before risky, broad, destructive, or policy-sensitive work.

## Always

- Preserve user changes.
- Prefer existing project patterns.
- Keep changes scoped to the request.

## Ask First

- Before deleting files.
- Before changing public APIs.
- Before adding major dependencies.
- Before running destructive commands.

## Never

- Do not commit secrets.
- Do not overwrite unrelated work.
- Do not claim verification passed without running the relevant command.
""",
    ".docs/progressive-disclosure.md": """\
# Progressive Disclosure

Use this document when deciding which project docs to read.

## Layers

1. `README.md`: human-facing project summary.
2. `AGENTS.md`: agent-facing router and highest-priority rules.
3. `.docs/*.md`: task-specific project context.
4. `.docs/system/*.md`: generated facts and generation notes.

## Rule

Read the smallest document that can answer the current question. Load more only when the task requires it.

## Task Map

- Project purpose: `overview.md`
- Local commands: `development.md`
- Early decisions: `decisions.md`
- Cross-module behavior: `architecture.md`
- Tests and verification: `testing.md`
- Style and patterns: `conventions.md`
- Risk and permissions: `agent-boundaries.md`
""",
}


STACK_MARKERS = {
    "package.json": "Node.js / JavaScript / TypeScript",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "package-lock.json": "npm",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "Pipfile": "Python",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "composer.json": "PHP",
    "Gemfile": "Ruby",
    "pom.xml": "Java / Maven",
    "build.gradle": "Java / Gradle",
    "Makefile": "Make",
    "docker-compose.yml": "Docker Compose",
    "Dockerfile": "Docker",
}


def detect_facts(root: Path) -> str:
    markers = []
    for marker, label in STACK_MARKERS.items():
        if (root / marker).exists():
            markers.append((marker, label))

    workflow_dir = root / ".github" / "workflows"
    workflows = sorted(p.name for p in workflow_dir.glob("*") if p.is_file()) if workflow_dir.exists() else []

    top_dirs = sorted(
        p.name for p in root.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name not in {"node_modules", "vendor", "target", "dist", "build"}
    )[:20]

    lines = [
        "# Repository Facts",
        "",
        "This file is machine-maintained by `init-agent-docs-vp`. Treat it as a fact snapshot, not a narrative guide.",
        "",
        "## Detected Stack Markers",
        "",
    ]
    if markers:
        lines.extend(f"- `{marker}`: {label}" for marker, label in markers)
    else:
        lines.append("- No common stack marker detected yet.")

    lines.extend(["", "## Top-Level Directories", ""])
    if top_dirs:
        lines.extend(f"- `{name}/`" for name in top_dirs)
    else:
        lines.append("- No top-level project directories detected yet.")

    lines.extend(["", "## GitHub Workflows", ""])
    if workflows:
        lines.extend(f"- `{name}`" for name in workflows)
    else:
        lines.append("- No `.github/workflows/` files detected.")

    return "\n".join(lines) + "\n"


def generation_notes(mode: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return dedent(f"""\
    # Generation Notes

    Generated by `init-agent-docs-vp` at `{now}`.

    Mode: `{mode}`

    ## Assumptions

    - Root `AGENTS.md` is the only global agent entry point.
    - Root `AGENTS.md` should stay under 300 lines.
    - Early decisions live in `.docs/decisions.md`.
    - `.docs/` contains task-specific guidance.
    - `.docs/system/` contains generated or inferred facts.
    - Existing files are preserved unless `--force` is used.

    ## Unknowns To Fill In

    - Project purpose.
    - Exact install, run, build, lint, format, and test commands.
    - Architecture boundaries, if the project has stable architecture.
    - Repository-specific conventions, if they matter.
    """)


def write_with_status(path: Path, content: str, force: bool) -> str:
    existed = path.exists()
    if existed and not force:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content), encoding="utf-8", newline="\n")
    return "updated" if existed else "created"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize project agent docs.")
    parser.add_argument("--target", default=".", help="Project root to write into.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing docs.")
    parser.add_argument("--full", action="store_true", help="Generate the expanded documentation set.")
    parser.add_argument("--update-facts", action="store_true", help="Only refresh .docs/system repo facts and generation notes.")
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    mode = "full" if args.full else "light"
    files = {}
    if not args.update_facts:
        files.update(BASE_FILES)
        if args.full:
            files.update(FULL_ONLY_FILES)

    if args.full or args.update_facts:
        files[".docs/system/repo-facts.md"] = detect_facts(root)
        files[".docs/system/generation-notes.md"] = generation_notes(mode)

    for relative, content in files.items():
        status = write_with_status(root / relative, content, args.force or args.update_facts)
        print(f"{status}: {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
