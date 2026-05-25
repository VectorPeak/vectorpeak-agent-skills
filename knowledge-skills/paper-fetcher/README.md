<h1 align="center">
  Paper Fetcher | 论文抓取与入库技能
</h1>

<p align="center">
  Turn a paper clue into a verified, renamed PDF and a Zotero-ready identifier
  <br>
  把论文线索转换为已校验、已规范命名的 PDF，并输出可用于 Zotero 的 identifier
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/paper--fetcher-research-orange" alt="paper fetcher"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

<p align="center">
  简体中文 | English later
</p>

```text
your paper clue  ->  agent verification  ->  PDF postprocess  ->  saved PDF + Zotero identifier
```

---

## 最直接的流程

你给 Agent 一个论文线索，可以是：

```text
论文标题
论文截图里的文字
arXiv / OpenReview / 会议官网 / 出版社 URL
项目主页或 GitHub README 里的 paper 链接
论文摘要、引言片段或引用片段
```

Agent 中间做这些事：

```text
1. 识别论文标题、作者、来源页面、PDF 链接和可能的 arXiv ID / DOI
2. 优先核验官方来源，例如 arXiv、OpenReview、ACL、NeurIPS、ICML、ICLR、ACM、IEEE
3. 下载官方 PDF，不绕过 paywall 或访问控制
4. 读取标题、摘要、引言、方法和结论，选择一个研究领域前缀
5. 调用 scripts/paper_postprocess.py 校验 PDF、移动到目标目录、规范重命名并输出 JSON
```

最后你得到：

```text
1. 一个保存到 <research-folder> 的 PDF
2. 一个按 {field}_{original paper title}.pdf 命名的文件名
3. 一个 arXiv ID 或 DOI，用于 Zotero Add Item by Identifier
4. 一个结构化 JSON 输出，方便 Agent 继续汇报或自动化处理
```

## 输入

最少需要告诉 Agent 两件事：

```text
论文线索：标题、URL、截图文字或摘录
保存位置：<research-folder>
```

如果你已经知道这些信息，也可以直接提供：

```text
arXiv ID
DOI
OpenReview ID
研究领域前缀：RAG / Agent / SFT / RL / DL_Frameworks / Other
```

## 处理

Agent 下载 PDF 后，使用后处理脚本：

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

脚本负责确定性处理：

```text
校验 PDF 文件存在、非空，并且文件头是 %PDF-
把 Windows 文件名非法字符替换为 -
移动到 --target-dir
重命名为 {field}_{title}.pdf
重名时追加 (2)、(3) 等后缀
选择 Zotero identifier：arXiv ID 优先，其次 DOI，再从 URL 尝试提取 DOI
输出 JSON
```

## 输出

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

Agent 最终应该向你汇报：

```text
Paper title
arXiv ID 或 arXiv: not found
DOI 或 DOI: not found
Zotero Add Item by Identifier value
其他来源 ID，例如 OpenReview ID
PDF source URL
Saved local path
File size
Zotero status
```

## 两个典型例子

### arXiv 论文

输入给 Agent：

```text
请下载并入库 Proximal Policy Optimization Algorithms
保存到 <research-folder>
```

后处理命令：

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

输出结果：

```text
Saved PDF: <research-folder>/RL_Proximal Policy Optimization Algorithms.pdf
Zotero identifier: 1707.06347
```

### OpenReview 论文

输入给 Agent：

```text
请下载并入库 https://openreview.net/pdf?id=eONq7FdiHa
保存到 <research-folder>
```

后处理命令：

```bash
python scripts/paper_postprocess.py \
  --pdf "<downloaded-pdf>" \
  --target-dir "<research-folder>" \
  --title "Agent Harness Engineering: A Survey" \
  --field Agent \
  --source-url "https://openreview.net/pdf?id=eONq7FdiHa" \
  --zotero
```

输出结果：

```text
Saved PDF: <research-folder>/Agent_Agent Harness Engineering- A Survey.pdf
Zotero identifier: not available unless arXiv ID or DOI is found
Other source ID: OpenReview eONq7FdiHa
```

## 研究领域前缀

```text
RAG
Agent
SFT
RL
DL_Frameworks
Other
```

## 目录结构

```text
paper-fetcher/
├── SKILL.md                         # Agent 使用说明
├── README.md                        # 人类阅读的公开说明
└── scripts/
    └── paper_postprocess.py         # PDF 校验、重命名、JSON 输出
```

## 边界

```text
优先使用官方 PDF 来源
不绕过 paywall 或访问控制
不写 Zotero 本地数据库
不保存 Zotero API 凭据
不通过 Web API 手工伪造 Zotero metadata
默认不生成 BibTeX，除非显式传入 --bib
```

## 维护说明

公开版只保留使用所需的 skill 说明和后处理脚本。脚本测试和扩展示例可以放在本地维护环境中，不需要作为最终使用包的一部分发布
