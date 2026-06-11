#!/usr/bin/env python3
"""Build a stable prompt for Chinese interview question-chain extraction."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE = """你是一名专业的中文面试录音分析师。请从下面的飞书妙记/文字记录中还原面试官的问题链条。

要求：
1. 只输出结构化 Markdown 报告，不输出处理过程。
2. 报告必须从 YAML frontmatter 开始，并包含下方给出的字段。
3. 重点提取面试官提出的问题、追问、质疑、反问、边界确认、场景假设和压力测试式追问。
4. 不要重点总结候选人的回答。
5. 不要把候选人回答或纯评价句伪造成问题。
6. 如果这是面试辅导材料，可以保留明确建议候选人准备的追问方向。
7. 使用中文 Markdown。
8. 一级标题格式：# 日期：公司/岗位/主题
9. 二级标题使用中文序号，例如：## 一、项目真实性与业务背景
10. 每个主问题格式：**主问题：**
11. 每个追问格式：- **追问1：**、- **追问2：**

请使用这个 frontmatter 模板，缺失字段保留为空字符串：

```yaml
---
source: "{source}"
source_type: "{source_type}"
date: "{date}"
event_time: "{event_time}"
company: "{company}"
position: "{position}"
candidate: "{candidate}"
duration: "{duration}"
feishu_title: "{title}"
related_minutes: "{related_minutes}"
related_transcript_doc: "{related_transcript_doc}"
source_priority: "{source_priority}"
related_source_status: "{related_source_status}"
tags:
  - interview
  - feishu
  - question-chain
type: "interview-question-chain"
---
```

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
    parser.add_argument("--source-type", default="feishu-minutes")
    parser.add_argument("--title", default="")
    parser.add_argument("--candidate", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--event-time", default="")
    parser.add_argument("--company", default="面试")
    parser.add_argument("--position", default="")
    parser.add_argument("--duration", default="")
    parser.add_argument("--related-minutes", default="")
    parser.add_argument("--related-transcript-doc", default="")
    parser.add_argument("--source-priority", default="优先读取文字记录 Docx；其次读取妙记原生逐字稿；最后使用智能纪要正文。")
    parser.add_argument("--related-source-status", default="")
    args = parser.parse_args()

    transcript = Path(args.transcript).read_text(encoding="utf-8")
    prompt = TEMPLATE.format(
        source=args.source,
        source_type=args.source_type,
        title=args.title,
        candidate=args.candidate,
        date=args.date,
        event_time=args.event_time,
        company=args.company,
        position=args.position,
        duration=args.duration,
        related_minutes=args.related_minutes,
        related_transcript_doc=args.related_transcript_doc,
        source_priority=args.source_priority,
        related_source_status=args.related_source_status,
        transcript=transcript.strip(),
    )
    Path(args.output).write_text(prompt, encoding="utf-8", newline="\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
