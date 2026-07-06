#!/usr/bin/env python3
"""Collect GitHub profile facts for profile-readme-vp.

Requires GitHub CLI (`gh`) authenticated with access to public search.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


LANDED_MERGED_PR_OVERRIDES: list[dict[str, Any]] = [
    {
        "author": "VectorPeak",
        "repository_url": "https://api.github.com/repos/pytorch/pytorch",
        "html_url": "https://github.com/pytorch/pytorch/pull/188830",
        "number": 188830,
        "title": "Fix test name detection for Git-style paths",
        "state": "closed",
        "landed_status": "closed_but_landed",
        "repo_stars": 101294,
        "evidence": [
            "PR has PyTorch's Merged label",
            "Associated issue is closed",
            "Patch exists on pytorch/pytorch main",
        ],
    },
]


def gh_json(args: list[str]) -> Any:
    output = subprocess.check_output(["gh", *args], encoding="utf-8")
    return json.loads(output)


def repo_list(owner: str, excluded_names: set[str]) -> list[dict[str, Any]]:
    repos = gh_json([
        "repo",
        "list",
        owner,
        "--public",
        "--limit",
        "200",
        "--json",
        "name,description,stargazerCount,url,isFork,isArchived",
    ])
    repos = [
        repo
        for repo in repos
        if not repo.get("isFork", False) and repo["name"].lower() not in excluded_names
    ]
    return [
        {
            "name": repo["name"],
            "stars": repo.get("stargazerCount", 0),
            "url": repo.get("url"),
            "description": repo.get("description") or "",
            "is_fork": repo.get("isFork", False),
            "is_archived": repo.get("isArchived", False),
        }
        for repo in repos
    ]


def search_merged_prs(owner: str, per_page: int = 100, max_pages: int = 10) -> tuple[int, list[dict[str, Any]]]:
    query = f"author:{owner} type:pr is:merged -user:{owner}"
    first = gh_json(["api", "-X", "GET", "search/issues", "-f", f"q={query}", "-f", f"per_page={per_page}"])
    total = int(first.get("total_count", 0))
    items = list(first.get("items", []))
    for page in range(2, max_pages + 1):
        if len(items) >= total:
            break
        page_data = gh_json([
            "api",
            "-X",
            "GET",
            "search/issues",
            "-f",
            f"q={query}",
            "-f",
            f"per_page={per_page}",
            "-f",
            f"page={page}",
        ])
        items.extend(page_data.get("items", []))
    return total, items


def repo_name_from_api_url(url: str) -> str:
    marker = "/repos/"
    if marker not in url:
        return url.rsplit("/", 1)[-1]
    return url.split(marker, 1)[1]


def compact_repo_display(full_name: str) -> str:
    owner, _, name = full_name.partition("/")
    special = {
        "agentscope": "AgentScope",
        "astrbot": "AstrBot",
        "lightrag": "LightRAG",
        "openclaw": "Openclaw",
        "pytorch": "PyTorch",
        "vllm": "vLLM",
        "transformers": "Hugging Face Transformers",
        "qwen-code": "Qwen Code",
        "github-mcp-server": "GitHub MCP Server",
        "agent-framework": "Microsoft Agent Framework",
        "agents": "LiveKit Agents",
        "microsoft-agent-framework": "Microsoft Agent Framework",
        "litellm": "LiteLLM",
    }
    return special.get(name.lower(), name.replace("-", " ").replace("_", " ").title())


def repo_stars(full_name: str) -> int:
    try:
        repo = gh_json(["api", f"repos/{full_name}"])
        return int(repo.get("stargazers_count", 0))
    except Exception:
        return 0


def merged_pr_key(item: dict[str, Any]) -> tuple[str, int]:
    repo = repo_name_from_api_url(item.get("repository_url", "")).lower()
    return repo, int(item.get("number", 0))


def merge_landed_overrides(owner: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = list(items)
    seen = {merged_pr_key(item) for item in merged}
    for override in LANDED_MERGED_PR_OVERRIDES:
        if str(override.get("author", "")).lower() != owner.lower():
            continue
        item = {key: value for key, value in override.items() if key not in {"author", "repo_stars", "evidence"}}
        key = merged_pr_key(item)
        if key in seen:
            continue
        merged.append(item)
        seen.add(key)
    return merged


def override_repo_stars(item: dict[str, Any]) -> int | None:
    key = merged_pr_key(item)
    for override in LANDED_MERGED_PR_OVERRIDES:
        if key == merged_pr_key(override):
            stars = override.get("repo_stars")
            return int(stars) if stars is not None else None
    return None


def qualified_pr_items(items: list[dict[str, Any]], min_stars: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    stars: dict[str, int] = {}
    qualified = []
    for item in items:
        repo = repo_name_from_api_url(item.get("repository_url", ""))
        if repo not in stars:
            stars[repo] = override_repo_stars(item) or repo_stars(repo)
        if stars[repo] >= min_stars:
            qualified.append(item)
    return qualified, stars


def upstream_repos_from_prs(items: list[dict[str, Any]], stars: dict[str, int]) -> list[dict[str, Any]]:
    counts = Counter()
    urls: dict[str, str] = {}
    for item in items:
        repo = repo_name_from_api_url(item.get("repository_url", ""))
        counts[repo] += 1
        urls[repo] = "https://github.com/" + repo
    ordered = sorted(counts, key=lambda repo: (-stars.get(repo, 0), -counts[repo], repo.lower()))
    return [
        {
            "name": repo,
            "display": compact_repo_display(repo),
            "url": urls[repo],
            "count": counts[repo],
            "stars": stars.get(repo, 0),
        }
        for repo in ordered
    ]


def upstream_pr_rows(items: list[dict[str, Any]], stars: dict[str, int]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        repo = repo_name_from_api_url(item.get("repository_url", ""))
        rows.append(
            {
                "repo": repo,
                "repo_display": compact_repo_display(repo),
                "repo_display_en": compact_repo_display(repo),
                "repo_display_zh": compact_repo_display(repo),
                "area": contribution_area(repo),
                "repo_url": "https://github.com/" + repo,
                "repo_stars": stars.get(repo, 0),
                "number": item.get("number"),
                "title": item.get("title") or "",
                "url": item.get("html_url"),
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            -int(item.get("repo_stars") or 0),
            str(item.get("repo") or "").lower(),
            -int(item.get("number") or 0),
        ),
    )


def contribution_area(full_name: str) -> str:
    name = full_name.rsplit("/", 1)[-1].lower()
    if name in {"pytorch", "vllm", "mooncake", "litellm", "sglang", "transformers", "ktransformers"}:
        return "AI infrastructure / model systems"
    if name in {
        "openclaw",
        "agentscope",
        "qwen-code",
        "astrbot",
        "pydantic-ai",
        "qwenpaw",
        "hivemind",
        "github-mcp-server",
        "agent-framework",
        "agents",
        "microsoft-agent-framework",
    }:
        return "Agent frameworks / protocols / evals"
    if name in {"dify", "ragflow", "lightrag", "langchain"}:
        return "Applied AI / RAG / observability"
    if "recommender" in name or "recbole" in name:
        return "Recommender systems"
    return "Applied AI / RAG / observability"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GitHub profile README facts.")
    parser.add_argument("--owner", default="VectorPeak", help="GitHub username or organization.")
    parser.add_argument("--out", required=True, type=Path, help="Output JSON path.")
    parser.add_argument("--summary-limit", type=int, default=12)
    parser.add_argument("--min-upstream-stars", type=int, default=500)
    parser.add_argument("--exclude-repo", action="append", default=[], help="Repository name to exclude from profile project counts.")
    args = parser.parse_args()

    excluded_names = {args.owner.lower(), *(name.lower() for name in args.exclude_repo)}
    repos = repo_list(args.owner, excluded_names)
    pr_count, pr_items = search_merged_prs(args.owner)
    pr_items = merge_landed_overrides(args.owner, pr_items)
    qualified_prs, upstream_stars = qualified_pr_items(pr_items, args.min_upstream_stars)

    facts = {
        "owner": args.owner,
        "public_project_count": len(repos),
        "public_repos": sorted(repos, key=lambda repo: (-int(repo["stars"]), repo["name"].lower())),
        "merged_pr_count": len(qualified_prs),
        "min_upstream_repo_stars": args.min_upstream_stars,
        "upstream_repos": upstream_repos_from_prs(qualified_prs, upstream_stars),
        "upstream_prs": upstream_pr_rows(qualified_prs, upstream_stars),
    }

    args.out.write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
