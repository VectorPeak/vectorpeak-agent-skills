#!/usr/bin/env python3
"""Check skill intake rules for pull requests.

This script is intentionally lightweight. It does not replace human or
multi-agent review; it prevents agents from forgetting to record that review.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_CATEGORIES = {"dev-skills", "knowledge-skills", "job-skills"}
REQUIRED_REVIEWERS = {
    "Reviewer A": "workflow clarity",
    "Reviewer B": "safety and scope",
    "Reviewer C": "README and usability",
}


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8")


def changed_files(base: str | None) -> list[str]:
    if base:
        diff_range = f"{base}...HEAD"
        output = run_git(["diff", "--name-only", diff_range])
    else:
        output = run_git(["diff", "--name-only", "--cached"])
        unstaged = run_git(["diff", "--name-only"])
        output = output + "\n" + unstaged
    return sorted({line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()})


def skill_dirs_from_files(files: list[str]) -> set[Path]:
    skill_dirs: set[Path] = set()
    for file in files:
        parts = Path(file).parts
        if len(parts) >= 3 and parts[0] in SKILL_CATEGORIES:
            skill_dirs.add(Path(parts[0]) / parts[1])
    return skill_dirs


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    block = text[4:end]
    data: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return None
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def check_skill_dir(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    abs_dir = ROOT / skill_dir
    skill_md = abs_dir / "SKILL.md"
    readme = abs_dir / "README.md"

    if not skill_md.exists():
        errors.append(f"{skill_dir}: missing SKILL.md")
    else:
        text = skill_md.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            errors.append(f"{skill_dir}: SKILL.md must start with YAML frontmatter")
        else:
            keys = set(frontmatter)
            if keys != {"name", "description"}:
                errors.append(
                    f"{skill_dir}: SKILL.md frontmatter must contain only name and description; got {sorted(keys)}"
                )
            expected_name = skill_dir.name
            if frontmatter.get("name") != expected_name:
                errors.append(
                    f"{skill_dir}: SKILL.md name should be {expected_name!r}, got {frontmatter.get('name')!r}"
                )
            if not frontmatter.get("description"):
                errors.append(f"{skill_dir}: SKILL.md description must not be empty")

    if not readme.exists():
        errors.append(f"{skill_dir}: missing README.md")

    todo_patterns = ["TODO", "TBD", "待补充"]
    for path in [skill_md, readme]:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in todo_patterns:
                if pattern in text:
                    errors.append(f"{skill_dir}: {path.name} still contains placeholder marker {pattern!r}")
                    break

    return errors


def pr_body_from_args(args: argparse.Namespace) -> str:
    if args.pr_body_file:
        path = Path(args.pr_body_file)
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    return os.environ.get("PR_BODY", "")


def check_multi_agent_review(pr_body: str) -> list[str]:
    errors: list[str] = []
    if "## Multi-Agent Review" not in pr_body:
        return [
            "PR body is missing '## Multi-Agent Review'. Agent reminder: record the multi-agent review before merge."
        ]

    for reviewer, label in REQUIRED_REVIEWERS.items():
        pattern = rf"-\s*{re.escape(reviewer)}\s*-\s*{re.escape(label)}\s*:\s*(.+)"
        match = re.search(pattern, pr_body)
        if not match:
            errors.append(
                f"PR body is missing '{reviewer} - {label}'. Agent reminder: add this review line."
            )
            continue
        value = match.group(1).strip().lower()
        if not value:
            errors.append(f"{reviewer} review is blank. Agent reminder: record pass, issues, or pending reason.")
        if value in {":", "-", "todo", "tbd", "pending"}:
            errors.append(f"{reviewer} review is not resolved enough: {value!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check VectorPeak skill intake rules.")
    parser.add_argument("--base", default=os.environ.get("BASE_REF"))
    parser.add_argument("--pr-body-file", default=os.environ.get("PR_BODY_FILE"))
    parser.add_argument("--require-review", action="store_true")
    args = parser.parse_args()

    files = changed_files(args.base)
    skill_dirs = skill_dirs_from_files(files)
    errors: list[str] = []

    for skill_dir in sorted(skill_dirs):
        errors.extend(check_skill_dir(skill_dir))

    if args.require_review:
        errors.extend(check_multi_agent_review(pr_body_from_args(args)))

    if errors:
        print("Skill intake check failed.\n")
        for error in errors:
            print(f"- {error}")
        print("\nAgent reminder: before adding or updating a skill, run multi-agent review and record it in the PR body.")
        return 1

    checked = ", ".join(str(path) for path in sorted(skill_dirs)) or "no skill directories changed"
    print(f"Skill intake check passed: {checked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
