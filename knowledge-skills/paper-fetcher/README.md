<h1 align="center">
  Paper Fetcher | 研究论文获取与入库技能
</h1>

<p align="center">
  从论文截图、标题、URL 或摘录识别论文，优先下载官方 PDF，重命名归档，并返回 Zotero 可用的 arXiv ID 或 DOI
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/paper--fetcher-research-orange" alt="paper fetcher"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
论文线索  ->  官方来源核验  ->  PDF 下载验证  ->  领域前缀重命名  ->  Zotero identifier 返回
```

---

## 为什么要做 Paper Fetcher?

研究论文入库看起来只是“下载 PDF”，但实际经常会遇到标题不完整、截图里只有局部信息、arXiv 和 OpenReview 版本不同、非官方镜像混入、PDF 文件名混乱、Zotero 导入缺少 identifier 等问题

Paper Fetcher 解决的是“把论文从线索稳定转成可归档、可引用、可导入 Zotero 的研究材料”的问题。它不是普通网页下载器，而是让 Agent 按固定流程完成论文识别、官方来源验证、PDF 校验、领域归类、文件重命名和 Zotero identifier 回传

核心策略是 **official-first, verified-PDF, Zotero-friendly**：

- 优先使用 arXiv、OpenReview、ACL Anthology、NeurIPS、ICML、ICLR、ACM、IEEE 等官方来源
- 不绕过付费墙、登录墙或访问控制
- 下载后校验 PDF 文件头，避免把 HTML 错误页当成论文
- 文件名使用研究领域前缀，方便本地资料库归档
- 最终返回 arXiv ID 或 DOI，交给 Zotero 的 Add Item by Identifier 生成规范元数据

## 工作原理

1. **输入识别**：接受论文截图文字、标题、arXiv/OpenReview/publisher URL、项目页 URL 或论文摘录

2. **官方来源核验**：优先搜索和验证官方论文页面，不把非官方镜像作为首选来源

3. **Identifier 提取**：优先提取 arXiv ID，其次 DOI；如果都没有，则报告不可用并保留 OpenReview ID 等辅助来源 ID

4. **PDF 下载与校验**：下载官方 PDF 后检查 `%PDF-` 文件头，避免保存无效文件

5. **领域前缀判断**：阅读标题、摘要、引言、方法和结论，将论文归到一个文件名前缀

   - `RAG`
   - `Agent`
   - `SFT`
   - `RL`
   - `DL_Frameworks`
   - `Other`

6. **后处理归档**：运行 `scripts/paper_postprocess.py`，清理文件名、移动到目标文件夹，并输出 JSON 结果

7. **Zotero 辅助**：返回可复制到 Zotero Add Item by Identifier 的 arXiv ID 或 DOI

## 快速上手

### 1. 准备目标文件夹

Paper Fetcher 不写死个人文献库路径。使用前需要提供或确认论文保存目录，并通过 `--target-dir` 显式传入

### 2. PDF 后处理

Agent 下载 PDF 后，运行：

```powershell
python .\scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --target-dir "<research-folder>" `
  --title "Agent Harness Engineering: A Survey" `
  --field Agent `
  --authors "Junjie Li and Xi Xiao and Yunbei Zhang" `
  --source-url "https://openreview.net/pdf?id=eONq7FdiHa" `
  --zotero
```

### 3. 预览输出路径

```powershell
python .\scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --target-dir "<research-folder>" `
  --title "Proximal Policy Optimization Algorithms" `
  --field RL `
  --arxiv-id "1707.06347" `
  --dry-run
```

### 4. 可选 BibTeX sidecar

默认不生成 `.bib`。只有用户明确要求时才使用：

```powershell
python .\scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --target-dir "<research-folder>" `
  --title "Proximal Policy Optimization Algorithms" `
  --field RL `
  --authors "John Schulman and Filip Wolski and Prafulla Dhariwal and Alec Radford and Oleg Klimov" `
  --year 2017 `
  --arxiv-id "1707.06347" `
  --source-url "https://arxiv.org/pdf/1707.06347" `
  --zotero `
  --bib
```

## 输出格式

脚本默认输出 JSON，例如：

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

最终回复通常包含：

```text
论文标题
arXiv ID 或 arXiv: not found
DOI 或 DOI: not found
Zotero Add Item by Identifier value
PDF 官方来源 URL
保存路径
文件大小
Zotero 状态
```

## 目录结构

```text
paper-fetcher/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── examples/
│   ├── arxiv-paper.example.json
│   └── openreview-paper.example.json
├── scripts/
│   └── paper_postprocess.py
└── tests/
    └── test_paper_postprocess.py
```

## 测试

```powershell
python -m pytest .\tests
```

测试是离线的，覆盖文件名清理、领域校验、重复命名、PDF 文件头检查、dry-run 行为和 identifier 优先级

## 注意事项

- 优先官方 PDF，不优先非官方镜像
- 不绕过 paywall、登录墙或访问控制
- 不直接写 Zotero 本地数据库
- 不存储 Zotero API credentials
- 不通过 Web API 手写 Zotero 元数据条目，优先返回 arXiv ID 或 DOI 让 Zotero 自己解析
- 公开仓库示例不写死个人论文库路径
