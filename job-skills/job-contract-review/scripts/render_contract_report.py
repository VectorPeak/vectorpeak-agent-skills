#!/usr/bin/env python3
"""Render validated contract review JSON as Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_contract_review import validate_review


def bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- 未发现"]


def render_issue(issue: dict[str, object], index: int) -> list[str]:
    lines = [
        f"### {index}. {issue['title']}",
        "",
        f"**条款位置:** {issue['clause']}",
    ]
    quote = str(issue.get("quote") or "").strip()
    if quote:
        lines.extend(["", f"> {quote}"])
    lines.extend([
        "",
        f"**风险说明:** {issue['explanation']}",
        "",
        f"**修改建议:** {issue['suggestion']}",
        "",
    ])
    return lines


def render_report(data: dict[str, object]) -> str:
    lines = [
        "# 合同审查报告",
        "",
        "## 总体判断",
        "",
        f"- **合同类型:** {data['contract_type']}",
        f"- **公平评分:** {data['fairness_grade']} ({data['fairness_score']}/100)",
        f"- **是否建议律师复核:** {'是' if data['lawyer_recommended'] else '否'}",
        "",
        str(data["summary"]),
        "",
        "## 关键条款",
        "",
        *bullet_lines(data.get("key_terms", [])),
        "",
        "## 红旗条款",
        "",
    ]

    red_flags = data.get("red_flags", [])
    if red_flags:
        for index, issue in enumerate(red_flags, 1):
            lines.extend(render_issue(issue, index))
    else:
        lines.append("- 未发现")

    lines.extend(["", "## 警告条款", ""])
    warnings = data.get("warnings", [])
    if warnings:
        for index, issue in enumerate(warnings, 1):
            lines.extend(render_issue(issue, index))
    else:
        lines.append("- 未发现")

    lines.extend(["", "## 保护条款", ""])
    protections = data.get("protections", [])
    if protections:
        for item in protections:
            quote = str(item.get("quote") or "").strip()
            line = f"- **{item['title']}** ({item['clause']}): {item['explanation']}"
            lines.append(line)
            if quote:
                lines.append(f"  - 原文引用: {quote}")
    else:
        lines.append("- 未发现")

    lines.extend(["", "## 缺失保护", "", *bullet_lines(data.get("missing_protections", []))])
    lines.extend(["", "## 优先谈判点", "", *bullet_lines(data.get("negotiation_points", []))])
    lines.extend([
        "",
        "## 是否建议律师复核",
        "",
        "建议律师复核。" if data["lawyer_recommended"] else "基于本次 AI 初筛，不强制要求律师复核；但如果合同金额较高、涉及本地法规或你对条款不确定，仍建议咨询专业律师。",
    ])
    lines.extend(["", "## 免责声明", "", str(data["disclaimer"]).strip()])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Validated review JSON path.")
    parser.add_argument("--output", help="Optional Markdown output path. Prints Markdown when omitted.")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    errors = validate_review(data)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    report = render_report(data)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
