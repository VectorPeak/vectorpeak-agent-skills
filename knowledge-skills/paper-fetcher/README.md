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

## 工作原理

1. **识别**：Agent 从论文标题、截图文字、URL、摘要片段或引用片段中识别论文标题、作者、来源页面、PDF 链接，以及可能存在的 arXiv ID、DOI 或 OpenReview ID

2. **核验**：Agent 优先核验官方来源，例如 arXiv、OpenReview、ACL Anthology、NeurIPS、ICML、ICLR、ACM、IEEE、Springer、Elsevier、官方项目页或论文作者提供的链接

3. **分类**：Agent 阅读标题、摘要、引言、方法和结论，选择一个研究领域前缀：

   - **RAG**：检索增强生成、向量检索、重排、知识增强生成、长上下文检索
   - **Agent**：LLM Agent、工具调用、规划、多智能体、浏览器/计算机使用、工作流自动化
   - **SFT**：监督微调、指令微调、对齐数据、领域微调、任务微调
   - **RL**：强化学习、RLHF、RLAIF、PPO、DPO、奖励模型、偏好优化
   - **DL_Frameworks**：训练/推理系统、分布式训练、编译器、CUDA kernel、模型服务基础设施
   - **Other**：不适合归入以上类别的论文

4. **入库**：Agent 下载官方 PDF 后调用 `scripts/paper_postprocess.py`。脚本校验 PDF 文件头、移动到目标目录、替换非法文件名字符、按 `{field}_{title}.pdf` 规范命名，并在重名时追加 `(2)`、`(3)` 等后缀

5. **报告**：脚本输出 JSON，Agent 汇报保存路径、文件大小、PDF 校验状态、arXiv ID、DOI、Zotero identifier、其他来源 ID 和 PDF 来源 URL

## 支持的论文线索

| 线索类型 | 示例 | 说明 |
|---|---|---|
| 论文标题 | `Proximal Policy Optimization Algorithms` | Agent 根据标题查找官方页面和 PDF |
| URL | arXiv、OpenReview、会议官网、出版社页面 | 优先核验官方来源 |
| 截图文字 | 论文截图、网页截图、引用截图 | 需要能看出标题、作者或明显片段 |
| 摘要/引言片段 | abstract、introduction、引用段落 | 用于反查论文 |
| 项目页链接 | GitHub README、官方 project page | 仅使用其中指向论文的官方链接 |

## 支持的研究领域前缀

| 前缀 | 适用内容 |
|---|---|
| `RAG` | 检索增强生成、向量检索、索引、query rewriting、reranking、知识增强生成 |
| `Agent` | LLM agents、工具使用、规划、agent benchmark、多智能体、workflow automation |
| `SFT` | supervised fine-tuning、instruction tuning、alignment dataset、domain/task fine-tuning |
| `RL` | RLHF、RLAIF、PPO、DPO、reward model、policy optimization、preference optimization |
| `DL_Frameworks` | 训练系统、推理系统、分布式训练、编译器、CUDA kernel、serving infrastructure |
| `Other` | 不适合归入以上类别的论文 |

## 快速上手

### 1. 安装

把 `paper-fetcher/` 整个目录复制到本地 Agent/Codex 的 skills 目录中。目录里至少要保留 `SKILL.md` 和 `scripts/paper_postprocess.py`

### 2. 提供论文线索

给 Agent 的输入可以直接写成：

```text
请使用 paper-fetcher 下载并入库这篇论文：<论文标题、URL、截图文字或摘要片段>
以后都默认保存到：<research-folder>
```

### 3. 获取入库结果

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

三步完成：安装 skill，交给 Agent 论文线索，拿到规范命名的 PDF 和 Zotero identifier

## 目录结构

```text
paper-fetcher/
├── SKILL.md                         # Agent 使用说明
├── README.md                        # Skill 流程说明
└── scripts/
    └── paper_postprocess.py         # PDF 校验、重命名、JSON 输出
```

## 常见问题

**它会绕过付费墙下载论文吗?**  
不会。`paper-fetcher` 优先使用官方公开 PDF 来源，不绕过 paywall 或访问控制

**它会自动写入 Zotero 吗?**  
不会。它返回 arXiv ID 或 DOI，用户可以用 Zotero 的 Add Item by Identifier 获取规范元数据。这样比手写 metadata 更稳

**如果只有 OpenReview ID 没有 arXiv ID 或 DOI 怎么办?**  
仍然可以下载和规范命名 PDF，但 Zotero identifier 应报告为 `not available`，OpenReview ID 作为其他来源 ID 保留

**扫描版 PDF 能处理吗?**  
脚本只校验 PDF 文件头，不做 OCR。如果 PDF 是扫描版，Agent 需要先说明需要 OCR，或让用户提供可读文本来源

**为什么要加研究领域前缀?**  
前缀让本地论文库更容易排序和检索。文件名会采用 `{field}_{original paper title}.pdf` 的形式

**可以批量处理论文吗?**  
可以由 Agent 逐篇执行同一流程，但当前公开版没有独立批处理 CLI。批量任务仍建议逐篇核验来源，避免下载错论文
