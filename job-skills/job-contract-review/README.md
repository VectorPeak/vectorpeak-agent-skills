<h1 align="center">
  Job Contract Review | 工作合同审查技能
</h1>

<p align="center">
  输入工作合同或 Offer 材料，提取关键条款，识别风险，并输出可谈判的问题清单
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-job--skills-teal" alt="job skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/job--contract--review-contracts-orange" alt="job contract review"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
合同材料  ->  文本提取  ->  条款结构化  ->  风险审查  ->  谈判清单与报告
```

---

## 为什么要做 Job Contract Review?

工作合同和 Offer 材料通常信息密度高，很多关键点藏在薪资结构、试用期、竞业限制、保密义务、违约责任、解除条件、工作地点和签署时间里。只靠快速浏览，很容易漏掉对自己长期影响很大的条款

Job Contract Review 解决的是“签署前审查”这一步。它不是替代律师，而是让 Agent 按固定流程提取条款、标出风险、识别缺失保护，并给出可操作的确认问题和谈判建议

和直接丢给 ChatGPT 有什么不同?

- **结构固定**：先抽取文本，再按 schema 输出 JSON，验证后再生成报告
- **风险分层**：区分 red flags、warnings、protections 和 missing protections
- **可谈判**：输出优先级问题和具体谈判建议，不只给泛泛评价
- **脚本兜底**：文件提取、JSON 校验和 Markdown 渲染由脚本处理
- **边界明确**：始终声明这是 AI 辅助审查，不是法律意见

## Skill 处理流程

```text
1. 输入合同材料       # PDF、DOCX、TXT、MD、RTF 或粘贴文本
2. 提取合同文本       # 保留页面、段落和表格顺序
3. 结构化风险审查     # 关键条款、红旗、警告、保护条款、缺失保护
4. 校验审查 JSON      # 按 schemas/contract_review.schema.json 验证
5. 输出 Markdown 报告 # 总体评价、风险、谈判点、律师审查建议、免责声明
```

Agent 会先识别合同类型和签署方视角，再检查关键条款、严重风险、中等风险、有利条款和缺失保护。生成内容默认使用中文，合同原文引用保持原语言

使用文件时，先运行文本提取脚本：

```bash
python scripts/extract_contract_text.py \
  --input "<contract-file>" \
  --output "<contract.extracted.json>"
```

完成分析后，Agent 先输出符合 schema 的 JSON，并用校验脚本检查：

```bash
python scripts/validate_contract_review.py \
  --input "<review.json>"
```

JSON 校验通过后，再渲染 Markdown 报告：

```bash
python scripts/render_contract_report.py \
  --input "<review.json>" \
  --output "<contract-review.md>"
```

## 支持的文件格式

| 格式 | 扩展名 | 说明 |
|---|---|---|
| PDF | `.pdf` | 文字型 PDF；扫描件或图片型 PDF 需要先 OCR |
| Word | `.docx` | Microsoft Word 文档，保留段落和表格顺序 |
| 纯文本 | `.txt` | 纯文本合同或粘贴文本保存后的文件 |
| Markdown | `.md` | Markdown 格式的合同、Offer 或条款草稿 |
| 富文本 | `.rtf` | RTF 富文本文件 |

## 支持的合同类型

| 合同类型 | 重点检查内容 |
|---|---|
| 劳动合同 | 薪资结构、试用期、工作地点、岗位职责、工时制度、解除条件、违约责任 |
| Offer Letter | 薪资、奖金、期权、入职日期、试用期、背景调查、撤回条件、附加承诺是否落入正式合同 |
| 保密协议 NDA | 保密范围、期限、例外信息、资料归还、违约责任、是否过度限制未来工作 |
| 竞业限制协议 | 限制范围、期限、地域、补偿标准、触发条件、违约金、是否影响后续就业 |
| 承包/顾问协议 | 交付范围、验收标准、付款节点、知识产权归属、终止条款、责任上限 |
| 自由职业协议 | 付款周期、修改次数、交付物定义、逾期付款、版权归属、取消费用 |
| 实习协议 | 实习期限、补贴、工作时间、转正承诺、保险责任、提前终止 |
| 离职/补偿协议 | 补偿金额、支付时间、豁免条款、保密义务、竞业延续、离职证明和社保公积金处理 |

## 快速上手

安装这个 skill 时，把 `job-contract-review/` 整个目录复制到本地 Agent/Codex 的 skills 目录中。目录里至少要保留 `SKILL.md`、`references/`、`schemas/` 和 `scripts/`

```text
job-contract-review/
├── SKILL.md
├── references/
├── schemas/
└── scripts/
```

给 Agent 的输入可以直接写成：

```text
请使用 job-contract-review 审查这份工作合同：
<上传文件或粘贴合同文本>
我的视角：<员工 / 候选人 / 承包方 / 自由职业者>
```

你最终应该得到：

```text
总体评价
合同类型和关键条款
红旗风险
中等风险
有利保护条款
缺失保护
优先谈判点
是否建议律师审查
AI 辅助审查免责声明
```

## 目录结构

```text
job-contract-review/
├── SKILL.md                         # Agent 使用说明
├── README.md                        # Skill 流程说明
├── references/
│   ├── review_prompt.md             # 结构化审查要求
│   └── contract_type_checks.md      # 合同类型检查点
├── schemas/
│   └── contract_review.schema.json  # 审查 JSON schema
└── scripts/
    ├── extract_contract_text.py     # 合同文本提取
    ├── validate_contract_review.py  # JSON 校验
    └── render_contract_report.py    # Markdown 报告渲染
```

## 使用边界

```text
这是 AI 辅助合同审查，不是法律意见
不要臆造合同里没有写的司法辖区规则
涉及司法辖区、强制性法律或重大金额时，应建议本地律师确认
不要把合同内容上传或分享给第三方，除非用户明确同意并理解隐私影响
不要过度确定；区分文本风险和法律可执行性
```
