#!/usr/bin/env python3
"""Build a stable prompt for Chinese interview question-chain extraction."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE = """你是一名专业的中文面试录音分析师。请从下面的飞书妙记/文字记录中还原面试官的问题链条。

要求：
1. 只输出结构化 Markdown 报告，不输出处理过程。
2. 重点提取面试官提出的问题、追问、质疑、反问、边界确认、场景假设和压力测试式追问。
3. 不要重点总结候选人的回答。
4. 不要把候选人回答或纯评价句伪造成问题。
5. 如果这是面试辅导材料，可以保留明确建议候选人准备的追问方向。
6. 使用中文 Markdown。
7. 一级标题格式：# 日期：公司/岗位/主题
8. 二级标题使用中文序号，例如：## 一、项目真实性与业务背景
9. 每个主问题格式：**主问题：**
10. 每个追问格式：- **追问1：**、- **追问2：**

元信息：
- source: {source}
- title: {title}
- candidate: {candidate}
- date: {date}
- company: {company}
- position: {position}
- related_source_status: {related_source_status}

逐字稿：
```text
{transcript}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--candidate", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--company", default="面试")
    parser.add_argument("--position", default="")
    parser.add_argument("--related-source-status", default="")
    args = parser.parse_args()

    transcript = Path(args.transcript).read_text(encoding="utf-8")
    prompt = TEMPLATE.format(
        source=args.source,
        title=args.title,
        candidate=args.candidate,
        date=args.date,
        company=args.company,
        position=args.position,
        related_source_status=args.related_source_status,
        transcript=transcript.strip(),
    )
    Path(args.output).write_text(prompt, encoding="utf-8", newline="\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
