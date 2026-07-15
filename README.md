<h1 align="center">
  VectorPeak Agent Skills | 个人 Agent 技能库
</h1>

<p align="center">
  Reusable agent skills for software development, knowledge work, and job decisions
  <br>
  用于沉淀个人工程开发、知识工作与工作职场场景的 Agent / Codex Skills 仓库
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="dev-skills/"><img src="https://img.shields.io/badge/dev--skills-engineering-brightgreen" alt="dev skills"></a>
  <a href="knowledge-skills/"><img src="https://img.shields.io/badge/knowledge--skills-learning-purple" alt="knowledge skills"></a>
  <a href="job-skills/"><img src="https://img.shields.io/badge/job--skills-career-teal" alt="job skills"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

<p align="center">
  简体中文 | English later
</p>

```text
daily work  ->  repeatable workflow  ->  SKILL.md  ->  reusable agent capability
```

---

## 这是什么

`VectorPeak Agent Skills` 用来把日常工作中反复出现的做法沉淀为可复用的 Agent 工作规程。这里的 Skill 不是一次性 Prompt，而是一个包含触发条件、所需输入、执行步骤、结果验证和安全边界的能力单元。

仓库当前覆盖三类任务：

- **Engineering**：代码注释、开源 PR 和 GitHub 自动化。
- **Knowledge Work**：学习辅导、资料剪藏、OCR、论文归档和内容展示。
- **Career & Work**：面试复盘、合同审查、工作记录和个人 GitHub 维护。

每个 Skill 都可以按需独立安装和调用；本仓库不要求固定的 Skill 组合顺序。

## 30 秒快速开始

### 安装单个 Skill

下面以 `code-comments-vp` 为例：

```bash
npx skills add https://github.com/VectorPeak/vectorpeak-agent-skills --skill code-comments-vp
```

将最后的 Skill 名称替换为 [Skill Catalog](#skill-catalog) 中的目标名称即可。

### 浏览并选择多个 Skill

```bash
npx skills add https://github.com/VectorPeak/vectorpeak-agent-skills
```

根据安装器提示选择需要的 Skill 和目标 Agent。若只想阅读或自行维护这些文件，也可以克隆整个仓库：

```bash
git clone https://github.com/VectorPeak/vectorpeak-agent-skills.git
```

> [!NOTE]
> 部分 Skill 依赖个人目录、第三方 API、本地服务或特定 GitHub 仓库。安装完成不代表相关外部依赖已经配置，请先查看对应的 `SKILL.md` 和 README。

## 按任务选择 Skill

| 想完成的任务 | 推荐 Skill |
| --- | --- |
| 改写、补充或审查代码注释与 docstring | [`code-comments-vp`](dev-skills/code-comments-vp/) |
| 从项目选择到提交 PR，管理完整的外部开源贡献流程 | [`pr-workflow-vp`](dev-skills/pr-workflow-vp/) |
| 触发并验证个人 GitHub Profile README 自动更新 | [`profile-readme-vp`](dev-skills/profile-readme-vp/) |
| 学习 AI、LLM、Agent 或计算机科学概念 | [`ai-learning-mentor-vp`](knowledge-skills/ai-learning-mentor-vp/) |
| 把当天的目标、疑问、代码和踩坑写入 DailyNotes | [`daily-notes-vp`](knowledge-skills/daily-notes-vp/) |
| 把多张图片制作成有序 GIF 展示 | [`gif-showcase-maker-vp`](knowledge-skills/gif-showcase-maker-vp/) |
| 将 GitHub 仓库、PR、Issue 等资料保存为结构化 Markdown | [`github-clippings-vp`](knowledge-skills/github-clippings-vp/) |
| 将截图或图片 OCR 为 Markdown | [`image-to-markdown-vp`](knowledge-skills/image-to-markdown-vp/) |
| 识别论文、下载官方 PDF 并记录 DOI 或 arXiv ID | [`paper-fetcher-vp`](knowledge-skills/paper-fetcher-vp/) |
| 剪藏微信公众号文章 | [`wechat-clippings-vp`](knowledge-skills/wechat-clippings-vp/) |
| 剪藏知乎作者、文章、问题或回答 | [`zhihu-clippings-vp`](knowledge-skills/zhihu-clippings-vp/) |
| 规划个人 GitHub 仓库的回溯性维护提交 | [`contributions-graph-filler-vp`](job-skills/contributions-graph-filler-vp/) |
| 从飞书妙记生成面试复盘或准备材料 | [`feishu-interview-minutes-vp`](job-skills/feishu-interview-minutes-vp/) |
| 审查 Offer、劳动合同、NDA 或外包协议 | [`job-contract-review-vp`](job-skills/job-contract-review-vp/) |
| 查询小黑日报助手中的时间线、报告和应用使用情况 | [`xiaohei-daily-query-vp`](job-skills/xiaohei-daily-query-vp/) |

## Skill Catalog

### Engineering

| Skill | 适用场景 | 主要结果 |
| --- | --- | --- |
| [`code-comments-vp`](dev-skills/code-comments-vp/) | 增加、重写、审查或统一代码注释和 docstring | 与代码行为一致、面向维护者的注释 |
| [`pr-workflow-vp`](dev-skills/pr-workflow-vp/) | Fork、选题、Bug 验证、PR 编写和 Reviewer 反馈处理 | 可审查的外部开源 PR 工作流 |
| [`profile-readme-vp`](dev-skills/profile-readme-vp/) | 手动运行或验证 `VectorPeak/VectorPeak` Profile README Workflow | Workflow 运行与 README 更新验证结果 |

> [!IMPORTANT]
> `dev-skills/pr-writer-vp/` 当前与 `pr-workflow-vp` 的能力描述重复。根目录导航暂以 `pr-workflow-vp` 为推荐入口，待后续确认兼容、合并或废弃策略。

### Knowledge Work

| Skill | 适用场景 | 主要结果 |
| --- | --- | --- |
| [`ai-learning-mentor-vp`](knowledge-skills/ai-learning-mentor-vp/) | 概念讲解、费曼反馈、类比辨析、刻意练习、知识图谱和知识压缩 | 结构化教学、练习、复习与掌握度反馈 |
| [`daily-notes-vp`](knowledge-skills/daily-notes-vp/) | 快速记录学习目标、疑问、代码、概念与踩坑 | 个人 10 天桶 DailyNotes 更新 |
| [`gif-showcase-maker-vp`](knowledge-skills/gif-showcase-maker-vp/) | 将多张输入图片制作成演示动画 | 自动适配画布并带过渡效果的 GIF |
| [`github-clippings-vp`](knowledge-skills/github-clippings-vp/) | 保存 GitHub 仓库、PR、Issue、Discussion、Commit 或代码链接 | 带来源信息的结构化 GitHub Markdown 资料卡 |
| [`image-to-markdown-vp`](knowledge-skills/image-to-markdown-vp/) | OCR 截图中的标题、表格、公式、图表和连续内容 | 尽量保持原始结构的 Markdown 文档 |
| [`paper-fetcher-vp`](knowledge-skills/paper-fetcher-vp/) | 从截图、标题、URL 或摘录识别研究论文 | 经来源核验的 PDF、分类信息和文献标识符 |
| [`wechat-clippings-vp`](knowledge-skills/wechat-clippings-vp/) | 从公众号名称、文章 URL、标题或 OCR 线索获取文章 | Obsidian Web Clipper 风格的微信 Markdown 剪藏 |
| [`zhihu-clippings-vp`](knowledge-skills/zhihu-clippings-vp/) | 获取知乎作者、专栏文章、问题和回答 | 带身份与来源核验的知乎 Markdown 剪藏 |

### Career & Work

| Skill | 适用场景 | 主要结果 |
| --- | --- | --- |
| [`contributions-graph-filler-vp`](job-skills/contributions-graph-filler-vp/) | 显式规划或执行个人仓库的回溯性维护提交 | 可审查的提交计划；应用修改前要求明确授权 |
| [`feishu-interview-minutes-vp`](job-skills/feishu-interview-minutes-vp/) | 处理飞书妙记、智能纪要或面试 Transcript | 中文面试复盘、追问链和准备报告 |
| [`job-contract-review-vp`](job-skills/job-contract-review-vp/) | 审查劳动合同、Offer、NDA、竞业、离职或外包条款 | 风险等级、缺失保护、谈判建议与结构化报告 |
| [`xiaohei-daily-query-vp`](job-skills/xiaohei-daily-query-vp/) | 查询本地小黑日报助手服务 | 工作时间线、Markdown 报告、热力图和应用时长统计 |

## Agent 兼容性

本仓库遵循以 `SKILL.md` 为核心的 Agent Skills 目录形式，并以 Codex / OpenAI Agent 元数据作为主要适配方向。

| 环境 | 当前支持情况 | 说明 |
| --- | --- | --- |
| Codex | 主要验证目标 | 多数 Skill 带有 `agents/openai.yaml`；可安装到个人或项目 Skills 目录 |
| Agent Skills CLI | 支持 | 可使用 `npx skills add` 选择并安装 Skill |
| Claude Code 及其他 Agent | 取决于客户端 | `SKILL.md` 可移植，但工具名称、权限模型和目录约定可能需要适配 |

兼容并不等于零配置。遇到以下内容时，应先根据本机环境调整对应 Skill：

- 写死的个人知识库或输出目录；
- TikHub、GitHub、Zotero 等外部服务或凭证；
- 飞书文档、GitHub Actions 或个人仓库权限；
- `xiaohei-daily-query-vp` 使用的局域网 HTTP 服务；
- Python 脚本、第三方包和 OCR/PDF 工具链。

## 一个 Skill 如何工作

每个 Skill 以 `SKILL.md` 为入口，按能力复杂度选择性携带辅助文件：

```text
<skill-name>/
├── SKILL.md            # 触发条件和执行规程，必需
├── agents/             # Agent 展示与调用元数据，可选
├── references/         # 模板、规范和领域资料，可选
├── scripts/            # 可重复执行的辅助脚本，可选
├── examples/           # 输入输出示例，可选
├── tests/              # 脚本或数据处理测试，可选
└── README.md           # 面向使用者的详细说明，可选
```

一个可复用 Skill 应尽量回答六个问题：

1. **何时使用**：明确触发词和适用边界。
2. **需要什么**：列出用户输入、文件、工具和外部依赖。
3. **如何执行**：提供稳定、可检查的步骤，而不是只给一句 Prompt。
4. **输出什么**：说明返回内容、生成文件和目标目录。
5. **如何验证**：检查来源、格式、测试或外部操作结果。
6. **何时停止**：遇到缺失信息、高风险操作或权限不足时及时请求确认。

## 质量与安全约定

- **来源可追溯**：下载、剪藏和研究类结果应保留原始 URL、文献标识符或来源信息。
- **副作用透明**：写文件、修改仓库、创建提交、触发 Workflow 或调用外部服务前，应说明将发生什么。
- **授权优先**：发布、提交、覆盖、批量修改及其他难以撤销的操作，需要用户明确授权。
- **事实与判断分离**：能从文件、代码和工具中核实的事实优先核实；不能确认的内容标记为假设。
- **个人配置不冒充通用默认值**：个人路径、局域网地址和服务凭证应在使用前检查并按环境配置。
- **输出可验证**：存在脚本、Schema 或测试时优先使用；否则至少检查结构、链接和关键字段。

## 仓库结构

```text
.
├── dev-skills/          # 工程开发技能
├── knowledge-skills/    # 知识工作技能
├── job-skills/          # 工作职场技能
├── README.md            # 仓库入口与 Skill Catalog
└── LICENSE              # Apache-2.0 license
```

新增 Skill 时，应优先保持单一职责，使用 `kebab-case` 命名，并至少提供包含有效 `name` 和 `description` frontmatter 的 `SKILL.md`。只有在步骤需要稳定复现时才增加脚本，在内容需要按需加载时才增加 `references/`，避免把一次性上下文直接固化为通用规则。

## 许可证

本仓库使用 [Apache License 2.0](LICENSE)，SPDX 标识为 `Apache-2.0`。
