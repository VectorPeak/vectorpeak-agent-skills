#!/usr/bin/env python3
"""Render VectorPeak's bilingual GitHub profile README."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_BADGES = [
    ("Python", "3776AB", "python", "white"),
    ("Go", "00ADD8", "go", "white"),
    ("TypeScript", "3178C6", "typescript", "white"),
    ("React", "20232A", "react", "61DAFB"),
    ("Node.js", "339933", "node.js", "white"),
    ("FastAPI", "009688", "fastapi", "white"),
    ("RAG", "0F172A", "googlegemini", "white"),
    ("Hugging Face", "FFD21E", "huggingface", "111"),
    ("LangChain", "1C3C3C", "langchain", "white"),
    ("GitHub", "181717", "github", "white"),
]

PROJECT_AREAS = {
    "Coding agents",
    "CI / PR tooling",
    "MCP / protocol tooling",
    "Codebase maps",
    "Applied agents",
    "LLM tooling",
    "Research",
}

CONTRIBUTION_AREAS = [
    "AI infrastructure / model systems",
    "Agent frameworks / protocols / evals",
    "Applied AI / RAG / observability",
    "Recommender systems",
]


def load_data(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def number(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    text = str(value).replace(",", "").replace("+", "").replace(" stars", "").strip()
    if text.lower().endswith("k"):
        return int(float(text[:-1]) * 1000)
    return int(text or 0)


def format_stars(value: Any) -> str:
    return f"{number(value):,}+"


def format_compact_stars(value: Any) -> str:
    stars = number(value)
    if stars >= 1000:
        return f"{stars / 1000:.1f}k stars"
    return f"{stars} stars"


def badge(label: str, color: str, logo: str, logo_color: str) -> str:
    safe_label = label.replace("-", "--").replace(" ", "%20")
    safe_logo = logo.replace(" ", "%20")
    return (
        f"![{label}](https://img.shields.io/badge/{safe_label}-{color}"
        f"?logo={safe_logo}&logoColor={logo_color})"
    )


def md_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def localized(project: dict[str, Any], key: str, lang: str) -> Any:
    if key == "area":
        return project.get(key)
    if lang == "zh":
        return project.get(f"zh_{key}") or project.get(key)
    return project.get(f"en_{key}") or project.get(key)


def project_link(project: dict[str, Any]) -> str:
    name = str(project["name"])
    url = project.get("url")
    return f"[{name}]({url})" if url else name


def contribution_project_link(item: dict[str, Any]) -> str:
    display = f"{item['project']} ({format_compact_stars(item.get('stars'))})"
    url = item.get("repo_url")
    return f"[{display}]({url})" if url else display


def contribution_pr_link(item: dict[str, Any]) -> str:
    pr = str(item["pr"])
    label = pr if pr.startswith("#") else f"#{pr}"
    url = item.get("pr_url")
    return f"[{label}]({url})" if url else label


def sorted_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(projects, key=lambda item: (-number(item.get("stars")), str(item.get("name", "")).lower()))


def sorted_contributions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: (-number(item.get("stars")), -number(item.get("pr")), str(item.get("project", "")).lower()))


def contribution_summary_from_data(data: dict[str, Any], contributions: list[dict[str, Any]], limit: int, lang: str) -> str | None:
    merged_count = data.get("merged_pr_count")
    summary_repos = data.get("upstream_repos")
    if merged_count is None and not contributions:
        return None
    if merged_count is not None and number(merged_count) <= 0 and not contributions:
        return None

    if summary_repos:
        ordered_repos = sorted(
            summary_repos,
            key=lambda repo: (
                -number(repo.get("stars")),
                -number(repo.get("count")),
                str(repo.get("display") or repo.get("name") or repo).lower(),
            ),
        )
        names = [str(repo.get("display") or repo.get("name") or repo) for repo in ordered_repos[:limit]]
    else:
        counts = Counter(str(item["project"]) for item in contributions)
        repo_stars: dict[str, int] = defaultdict(int)
        for item in contributions:
            project = str(item["project"])
            repo_stars[project] = max(repo_stars[project], number(item.get("stars")))
        ordered = sorted(counts, key=lambda project: (-repo_stars[project], -counts[project], project.lower()))
        names = ordered[:limit]

    count = number(merged_count) if merged_count is not None else len(contributions)
    joined = ", ".join(names)
    if lang == "zh":
        return f"{count}+ 个 merged upstream PR，覆盖 {joined}。"
    return f"{count}+ merged upstream PRs, including fixes in {joined}."


def project_summary(projects: list[dict[str, Any]], limit: int, data: dict[str, Any], lang: str) -> str:
    public_repos = data.get("public_repos") or []
    summary_source = public_repos if public_repos else projects
    ordered = sorted_projects(summary_source)
    names = [str(project["name"]) for project in ordered[:limit]]
    count = number(data.get("public_project_count")) if data.get("public_project_count") is not None else len(summary_source)
    joined = ", ".join(names)
    if lang == "zh":
        return f"{count} 个公开项目，代表项目包括 {joined}。"
    return f"{count} public projects, led by {joined}."


def validate_projects(projects: list[dict[str, Any]]) -> None:
    for project in projects:
        missing = [key for key in ("area", "name", "stars", "notes") if key not in project]
        if missing:
            raise ValueError(f"Project {project!r} missing required fields: {', '.join(missing)}")
        area = str(project["area"])
        if area not in PROJECT_AREAS:
            raise ValueError(f"Unsupported project area {area!r} for {project.get('name')!r}")


def validate_contributions(contributions: list[dict[str, Any]]) -> None:
    allowed = set(CONTRIBUTION_AREAS)
    for item in contributions:
        missing = [key for key in ("area", "project", "stars", "pr", "fixed") if key not in item]
        if missing:
            raise ValueError(f"Contribution {item!r} missing required fields: {', '.join(missing)}")
        area = str(item["area"])
        if area not in allowed:
            raise ValueError(f"Unsupported contribution area {area!r} for {item.get('project')!r}")


def render_projects(lines: list[str], projects: list[dict[str, Any]], lang: str) -> None:
    if lang == "zh":
        lines.extend([
            "### 项目",
            "",
            "| Area&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Project | Stars | Notes |",
            "| --- | --- | --- | --- |",
        ])
    else:
        lines.extend([
            "### Projects",
            "",
            "| Area&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Project | Stars | Notes |",
            "| --- | --- | --- | --- |",
        ])

    for project in sorted_projects(projects):
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(localized(project, "area", lang)),
                    project_link(project),
                    format_stars(project.get("stars")),
                    md_escape(localized(project, "notes", lang)),
                ]
            )
            + " |"
        )


def render_contributions(lines: list[str], contributions: list[dict[str, Any]], lang: str) -> None:
    if not contributions:
        return

    title = "### 开源贡献" if lang == "zh" else "### Open Source Contributions"
    fixed_header = "修复内容" if lang == "zh" else "What I Fixed"
    lines.extend(["", title, ""])
    by_area: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in contributions:
        by_area[str(item["area"])].append(item)

    for area in CONTRIBUTION_AREAS:
        items = by_area.get(area, [])
        if not items:
            continue
        lines.extend([
            f"#### {area}",
            "",
            f"| Project | PR | {fixed_header} |",
            "| --- | --- | --- |",
        ])
        for item in sorted_contributions(items):
            fixed = item.get("zh_fixed") if lang == "zh" else item.get("en_fixed")
            lines.append(
                "| "
                + " | ".join(
                    [
                        contribution_project_link(item),
                        contribution_pr_link(item),
                        md_escape(fixed or item["fixed"]),
                    ]
                )
                + " |"
            )
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()


def render_section(
    lines: list[str],
    data: dict[str, Any],
    projects: list[dict[str, Any]],
    contributions: list[dict[str, Any]],
    lang: str,
    include_badges: bool,
) -> None:
    identity = data.get("identity", "AI Programmer | BS CS @ Xidian University | 2x CCF-C")
    contribution_limit = int(data.get("contribution_summary_limit", 12))
    project_limit = int(data.get("project_summary_limit", 12))
    heading = data.get("zh_heading" if lang == "zh" else "en_heading")
    heading = heading or "## Hey, I'm VectorPeak 👋"

    lines.extend([str(heading), ""])
    if include_badges:
        badges = data.get("badges") or DEFAULT_BADGES
        badge_parts = []
        linkedin = data.get("linkedin")
        if linkedin:
            badge_parts.append(f"[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)]({linkedin})")
        badge_parts.extend(badge(*item) for item in badges)
        badge_line = " ".join(badge_parts)
        lines.extend([badge_line, ""])

    lines.extend([str(identity), ""])
    summary = contribution_summary_from_data(data, contributions, contribution_limit, lang)
    if summary:
        lines.append(f"- {summary}")

    if projects:
        lines.extend([f"- {project_summary(projects, project_limit, data, lang)}", ""])

    render_projects(lines, projects, lang)
    render_contributions(lines, contributions, lang)


def render(data: dict[str, Any]) -> str:
    projects = list(data.get("projects", []))
    min_upstream_stars = number(data.get("min_upstream_repo_stars", 500))
    contributions = [
        contribution
        for contribution in list(data.get("contributions", []))
        if number(contribution.get("stars")) >= min_upstream_stars
    ]
    validate_projects(projects)
    validate_contributions(contributions)

    lines: list[str] = []
    render_section(lines, data, projects, contributions, "zh", include_badges=True)
    lines.extend(["", "---", ""])
    render_section(lines, data, projects, contributions, "en", include_badges=False)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render VectorPeak's bilingual GitHub profile README.")
    parser.add_argument("--data", required=True, type=Path, help="JSON data file.")
    parser.add_argument("--facts", type=Path, help="Optional GitHub-collected facts JSON.")
    parser.add_argument("--out", required=True, type=Path, help="README output path.")
    args = parser.parse_args()

    data = load_data(args.data)
    if args.facts:
        data = deep_merge(data, load_data(args.facts))
    args.out.write_text(render(data), encoding="utf-8", newline="\n")
    print(f"wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
