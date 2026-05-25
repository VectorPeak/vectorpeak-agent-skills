<h1 align="center">
  Paper Fetcher | 论文抓取与入库技能
</h1>

<p align="center">
  Identify research papers, download verified official PDFs, rename them consistently, and report Zotero identifiers
  <br>
  用于论文识别、官方 PDF 下载、规范命名与 Zotero identifier 辅助的 Agent / Codex Skill
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
paper clue  ->  official source  ->  verified PDF  ->  named archive  ->  Zotero identifier
```

---

## 简介

`paper-fetcher` 是一个研究论文入库 skill。它帮助 Agent 从论文标题、截图文字、URL 或摘录中识别论文，优先核验官方来源，下载并验证 PDF，然后按研究领域前缀重命名，并输出 arXiv ID 或 DOI 供 Zotero 使用

它不是通用爬虫，也不负责绕过付费墙。它的核心价值是把“找论文、验来源、存 PDF、给 Zotero identifier”这条流程做成可复用工作流

## 为什么存在

论文资料管理最容易乱在入口：同一篇论文可能来自 arXiv、OpenReview、会议官网、项目页或 GitHub README；如果不统一核验和命名，后续检索、引用和复盘都会变慢

这个 skill 把论文入库拆成两部分：Agent 负责识别和判断，脚本负责确定性的文件校验、重命名和 JSON 输出

## 核心结构

```text
paper-fetcher/
├── SKILL.md                         # Agent 使用说明
├── README.md                        # 人类阅读的公开说明
└── scripts/
    └── paper_postprocess.py         # PDF 校验、重命名、JSON 输出
```

## 功能边界

- 优先使用官方 PDF 来源
- 不绕过 paywall 或访问控制
- 不写 Zotero 本地数据库
- 不保存 Zotero API 凭据
- 不通过 Web API 手工伪造 Zotero metadata
- 默认不生成 BibTeX，除非显式传入 `--bib`

## 使用方式

Agent 下载 PDF 后，运行后处理脚本：

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

### arXiv 论文

如果论文有 arXiv ID，优先把 arXiv ID 传给 `--arxiv-id`。Zotero 可以直接使用这个 identifier 添加条目：

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

预期命名：

```text
RL_Proximal Policy Optimization Algorithms.pdf
```

Zotero Add Item by Identifier 可使用：

```text
1707.06347
```

### OpenReview 论文

如果论文只有 OpenReview ID，仍然可以下载并规范命名；但如果没有 arXiv ID 或 DOI，Zotero identifier 应报告为 `not available`，OpenReview ID 只作为来源参考：

```bash
python scripts/paper_postprocess.py \
  --pdf "<downloaded-pdf>" \
  --target-dir "<research-folder>" \
  --title "Agent Harness Engineering: A Survey" \
  --field Agent \
  --source-url "https://openreview.net/pdf?id=eONq7FdiHa" \
  --zotero
```

预期命名：

```text
Agent_Agent Harness Engineering- A Survey.pdf
```

Zotero Add Item by Identifier：

```text
not available unless arXiv ID or DOI is found
```

支持的研究领域前缀：

```text
RAG
Agent
SFT
RL
DL_Frameworks
Other
```

使用 `--dry-run` 可以只预览输出路径，不移动或写入文件

## JSON 输出

脚本默认输出 JSON，便于 Agent 或自动化工具继续处理：

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

## 维护说明

公开版只保留使用所需的 skill 说明和后处理脚本。脚本测试和扩展示例可以放在本地维护环境中，不需要作为最终使用包的一部分发布
