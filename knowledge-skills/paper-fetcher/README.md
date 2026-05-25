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

## 为什么要做 Paper Fetcher?

研究资料最容易乱在入口：同一篇论文可能出现在 arXiv、OpenReview、会议官网、出版社页面、项目主页或 GitHub README 里。来源不统一、文件名不统一、PDF 没校验、Zotero identifier 没记录，后面检索、引用和复盘都会变慢

Paper Fetcher 解决的是“论文入库”这一步。它不是简单下载器，而是让 Agent 按固定流程完成识别、核验、下载、校验、重命名和 Zotero identifier 汇报，把散乱论文线索变成可归档、可检索、可引用的本地资料

和直接丢给 ChatGPT 有什么不同?

- **流程固定**：不是只回答“这篇论文是什么”，而是走完识别、核验、下载、校验、命名和汇报
- **来源优先级明确**：优先官方来源，避免非官方镜像和错误 PDF
- **文件可落地**：最终保存为规范命名的本地 PDF，而不是只给一段文字解释
- **Zotero 友好**：优先返回 arXiv ID 或 DOI，方便用 Add Item by Identifier 获取规范元数据
- **脚本兜底**：PDF 校验、文件移动、重命名和 JSON 输出由脚本处理，减少 Agent 临场发挥的不确定性

## Skill 处理流程

```text
1. 输入论文线索       # 标题、截图文字、URL、摘要片段、保存目录
2. 核验官方来源       # 识别论文，提取 arXiv ID、DOI 或 OpenReview ID
3. 下载官方 PDF      # 使用官方来源，不绕过 paywall 或访问控制
4. 运行后处理脚本     # 校验 PDF、移动文件、规范命名、输出 JSON
5. 汇报入库结果       # 保存路径、文件大小、Zotero identifier、来源信息
```

用户给 Agent 提供论文线索和保存目录。Agent 会根据线索识别论文标题、作者、来源页面、PDF 链接，以及可能存在的 arXiv ID、DOI 或 OpenReview ID。核验来源时优先使用 arXiv、OpenReview、ACL、NeurIPS、ICML、ICLR、ACM、IEEE 等官方来源，避免非官方镜像，也不绕过 paywall 或访问控制

接着，Agent 阅读标题、摘要、引言、方法和结论，选择一个研究领域前缀：

```text
RAG
Agent
SFT
RL
DL_Frameworks
Other
```

Agent 下载官方 PDF 后，调用后处理脚本。脚本负责校验 PDF、移动文件、规范命名，并输出 JSON：

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

脚本处理规则：

```text
校验 PDF 文件存在、非空，并且文件头是 %PDF-
把 Windows 文件名非法字符替换为 -
移动 PDF 到 --target-dir
重命名为 {field}_{title}.pdf
如果目标文件已存在，自动追加 (2)、(3) 等后缀
选择 Zotero identifier：arXiv ID 优先，其次 DOI，再从 URL 尝试提取 DOI
输出 JSON
```

最后，Agent 向用户汇报论文标题、arXiv ID、DOI、Zotero identifier、其他来源 ID、PDF 来源 URL、保存路径、文件大小和 Zotero 状态。脚本默认输出结构如下：

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

## 快速上手

安装这个 skill 时，把 `paper-fetcher/` 整个目录复制到本地 Agent/Codex 的 skills 目录中。目录里至少要保留 `SKILL.md` 和 `scripts/paper_postprocess.py`

```text
paper-fetcher/
├── SKILL.md
└── scripts/
    └── paper_postprocess.py
```

给 Agent 的输入可以直接写成：

```text
请使用 paper-fetcher 下载并入库这篇论文：<论文标题、URL、截图文字或摘要片段>
以后都默认保存到：<research-folder>
```

你最终应该得到：

```text
保存后的 PDF 路径
规范化文件名
文件大小
PDF 校验状态
arXiv ID 或 DOI
Zotero Add Item by Identifier value
其他来源 ID，例如 OpenReview ID
PDF 来源 URL
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
