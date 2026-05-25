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

## 工作原理

1. **解析**：从合同文件或粘贴文本中提取内容。PDF 使用 `pdfplumber` 处理文字型 PDF，DOCX 使用 `python-docx` 读取段落和表格，TXT/MD/RTF 直接读取文本

2. **识别**：Agent 根据合同内容识别合同类型和签署方视角，例如劳动合同、Offer Letter、NDA、竞业限制协议、承包/顾问协议或离职补偿协议

3. **分析**：Agent 逐条审查关键条款，并把发现分为四类：

   - **红旗风险**：可能造成重大经济损失、法律责任、权利丧失或长期限制的问题
   - **中等风险**：值得谈判或要求澄清，但不一定构成立即拒签的问题
   - **有利保护**：对签署方有帮助、通常应保留的条款
   - **缺失保护**：合同中应该有但缺失或写得不完整的保护条款

4. **评分**：生成公平性评分和等级，从 `A+` 到 `F` 表示合同整体公平程度。评分会结合问题数量、严重程度、已有保护条款和缺失保护

5. **报告**：先按 `schemas/contract_review.schema.json` 输出并校验 JSON，再渲染 Markdown 报告，包含总体评价、关键条款、风险、谈判点、是否建议律师审查和免责声明

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

## 常见问题

**这算法律建议吗?**  
不算。`job-contract-review` 是帮助用户读懂合同文本的 AI 辅助审查 skill，不能替代律师意见。涉及重大合同、强司法辖区差异、竞业限制、高额违约金或争议处理时，应咨询本地律师

**我的合同会上传到云端吗?**  
取决于用户使用的 Agent 和模型服务。这个 skill 本身不保存、不记录、也不会主动传输合同内容；但如果用户使用云端 LLM，合同文本会被发送给对应模型服务进行分析。若合同高度敏感，应使用本地模型或在确认隐私边界后再处理

**它适合审查哪些工作材料?**  
适合劳动合同、Offer Letter、NDA、竞业限制协议、承包/顾问协议、自由职业协议、实习协议、离职或补偿协议等工作相关材料。它也可以审查粘贴文本、条款截图转写内容或 Markdown 草稿

**它能自动判断合同是否合法有效吗?**  
不能。它能指出文本层面的风险、缺失保护、明显不公平或需要谈判的条款，但不会臆造司法辖区规则，也不会断言某个条款在当地一定有效或无效

**支持中文合同吗?**  
支持。默认输出中文报告，并保留合同原文引用的语言。中英文混合合同也可以处理

**能处理很长的合同吗?**  
可以处理较长合同，但超长文档可能需要分段分析或先提取重点条款。对于特别长、金额高或风险大的合同，建议结合人工复核和律师意见

**可以自动化到 CI/CD 或脚本流程里吗?**  
可以做部分自动化。文件提取、JSON 校验和 Markdown 渲染都由脚本处理；真正的法律风险判断仍由 Agent/LLM 完成，适合半自动审查流程，而不是完全离线规则引擎
