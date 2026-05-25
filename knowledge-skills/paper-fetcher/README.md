<h1 align="center">
  Paper Fetcher | 论文抓取与入库技能
</h1>

<p align="center">
  输入论文线索，核验官方来源，保存规范命名的 PDF，并返回 Zotero 可用的 identifier
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/paper--fetcher-research-orange" alt="paper fetcher"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
论文线索  ->  官方来源核验  ->  PDF 下载与校验  ->  规范命名入库  ->  Zotero identifier
```

---

## Skill 处理流程

### 1. 输入论文线索

用户给 Agent 提供一个论文线索，并说明 PDF 要保存到哪个目录：

```text
请下载并入库这篇论文：<论文标题、截图文字、URL 或摘要片段>
保存到：<research-folder>
```

论文线索可以是：

```text
论文标题
论文截图里的文字
arXiv / OpenReview / 会议官网 / 出版社 URL
项目主页或 GitHub README 里的论文链接
论文摘要、引言片段或引用片段
```

如果用户已经知道 arXiv ID、DOI、OpenReview ID 或研究领域前缀，也可以一起提供

### 2. Agent 识别并核验论文

Agent 根据输入线索查找论文，并确认最可靠的官方来源：

```text
识别论文标题、作者和来源页面
查找官方 PDF 链接
提取 arXiv ID、DOI 或 OpenReview ID
优先使用 arXiv、OpenReview、ACL、NeurIPS、ICML、ICLR、ACM、IEEE 等官方来源
避免使用非官方镜像
不绕过 paywall 或访问控制
```

### 3. Agent 选择研究领域前缀

Agent 阅读标题、摘要、引言、方法和结论后，从下面选择一个前缀：

```text
RAG
Agent
SFT
RL
DL_Frameworks
Other
```

这个前缀会写入最终文件名，格式是：

```text
{field}_{original paper title}.pdf
```

### 4. Agent 下载 PDF 并调用脚本

Agent 下载官方 PDF 后，调用后处理脚本：

```bash
python scripts/paper_postprocess.py \
  --pdf "<downloaded-pdf>" \
  --target-dir "<research-folder>" \
  --title "Paper Title" \
  --field Agent \
  --arxiv-id "2401.00001" \
  --doi "10.1234/example.paper" \
  --source-url "https://example.org/paper.pdf" \
  --zotero
```

脚本会执行这些确定性处理：

```text
校验 PDF 文件存在、非空，并且文件头是 %PDF-
把 Windows 文件名非法字符替换为 -
移动 PDF 到 --target-dir
重命名为 {field}_{title}.pdf
如果目标文件已存在，自动追加 (2)、(3) 等后缀
选择 Zotero identifier：arXiv ID 优先，其次 DOI，再从 URL 尝试提取 DOI
输出 JSON
```

### 5. 输出入库结果

脚本默认输出 JSON：

```json
{
  "field": "Agent",
  "final_name": "Agent_Example Paper.pdf",
  "saved_path": "<research-folder>/Agent_Example Paper.pdf",
  "pdf_verified": true,
  "dry_run": false,
  "identifier": "2401.00001",
  "zotero_status": {
    "status": "identifier_available",
    "identifier": "2401.00001"
  }
}
```

Agent 最终向用户汇报：

```text
论文标题
arXiv ID，或 arXiv: not found
DOI，或 DOI: not found
Zotero Add Item by Identifier value
其他来源 ID，例如 OpenReview ID
PDF source URL
Saved local path
File size
Zotero status
```

## 示例

### arXiv 论文

用户输入：

```text
请下载并入库 Proximal Policy Optimization Algorithms
保存到 <research-folder>
```

脚本调用：

```bash
python scripts/paper_postprocess.py \
  --pdf "<downloaded-pdf>" \
  --target-dir "<research-folder>" \
  --title "Proximal Policy Optimization Algorithms" \
  --field RL \
  --arxiv-id "1707.06347" \
  --source-url "https://arxiv.org/pdf/1707.06347" \
  --zotero
```

最终结果：

```text
Saved PDF: <research-folder>/RL_Proximal Policy Optimization Algorithms.pdf
Zotero identifier: 1707.06347
```

### OpenReview 论文

用户输入：

```text
请下载并入库 https://openreview.net/pdf?id=eONq7FdiHa
保存到 <research-folder>
```

脚本调用：

```bash
python scripts/paper_postprocess.py \
  --pdf "<downloaded-pdf>" \
  --target-dir "<research-folder>" \
  --title "Agent Harness Engineering: A Survey" \
  --field Agent \
  --source-url "https://openreview.net/pdf?id=eONq7FdiHa" \
  --zotero
```

最终结果：

```text
Saved PDF: <research-folder>/Agent_Agent Harness Engineering- A Survey.pdf
Zotero identifier: not available unless arXiv ID or DOI is found
Other source ID: OpenReview eONq7FdiHa
```

## 目录结构

```text
paper-fetcher/
├── SKILL.md                         # Agent 使用说明
├── README.md                        # Skill 流程说明
└── scripts/
    └── paper_postprocess.py         # PDF 校验、重命名、JSON 输出
```

## 使用边界

```text
优先使用官方 PDF 来源
不绕过 paywall 或访问控制
不写 Zotero 本地数据库
不保存 Zotero API 凭据
不通过 Web API 手工伪造 Zotero metadata
默认不生成 BibTeX，除非显式传入 --bib
```
