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

## 简介

`VectorPeak Agent Skills` 是一个个人 Agent 技能库，用来保存日常工程开发、知识沉淀和工作职场场景中反复出现、值得复用的工作方法

这里的 skill 不是一次性 prompt，而是一组可迁移的工作规程：它应该说明何时使用、需要什么输入、按什么步骤执行、如何验证结果，以及应该避免什么

换句话说，agent skill（智能体技能）更像一份“可执行的工作说明书”：它把人的经验压缩成稳定流程，让 Agent 在相似场景下少猜、多验证、按规程完成任务

## 为什么存在

开发、学习和工作里的很多问题并不是第一次遇到：构建失败、代码审查、论文处理、概念解释、笔记整理、合同审查、Offer 对比、面试准备，这些任务背后都有稳定的判断路径

这个仓库的目标是把这些路径沉淀为 Agent 可以直接调用的技能，让经验从“临场发挥”变成“可复用流程”

## 核心结构

```text
.
├── dev-skills/          # 工程开发技能：debug、review、test、CI/CD、release
├── knowledge-skills/    # 知识沉淀技能：学习法、论文处理、知乎剪藏、概念解释、笔记整理
├── job-skills/          # 工作职场技能：合同审查、Offer 对比、简历面试、职场沟通
├── templates/           # 新 skill 的 README / 结构模板
├── CONTRIBUTING.md      # skill 入库规则
├── README.md            # 仓库说明
└── LICENSE              # Apache-2.0 license
```

## Skill 分类

### `dev-skills/`

用于工程开发场景，包括编码、调试、测试、代码审查、架构分析、构建修复、发布流程、CI/CD、仓库维护和本地自动化

- [`code-comments-vp`](dev-skills/code-comments-vp/)：为代码补充面向维护者的模块职责、执行流程、边界、副作用、fallback 和设计原因说明，默认粗粒度，复杂逻辑再加细粒度块注释。
- [`opensense-pr-attempt-vp`](dev-skills/opensense-pr-attempt-vp/)：把 OpenSense 的每日 issue 筛选、本地 PR 尝试、测试证据和 PR 草稿流程沉淀为可复用 Agent Skill。
- [`pr-case-collector-vp`](dev-skills/pr-case-collector-vp/)：把真实 GitHub PR 按项目、改动类型、评级和备注收录为 LLM 可参考的简表案例库。
- [`profile-readme-github-vp`](dev-skills/profile-readme-github-vp/)：把 VectorPeak GitHub Profile README 的 facts 收集、双语渲染、公开项目自动补全和 profile 仓库排除规则沉淀为可复用 Agent Skill。

### `knowledge-skills/`

用于知识工作场景，包括自顶向下学习、概念解释、论文阅读、知乎文章剪藏、文章摘要、知识地图抽取、笔记整理、学习检查和写作流程

- [`daily-notes-vp`](knowledge-skills/daily-notes-vp/)：把个人学习中的短期目标、疑问、代码记录、概念和踩坑经验轻量追加到 `E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes`，10 天一个文件，按 Goal / Question / Code / Concept / Pitfall 组织。
- [`image-to-md-vp`](knowledge-skills/image-to-md-vp/)：把多轮输入的截图或图片 OCR 成指定路径下的 Markdown 文件，保留标题层级、表格、公式、emoji 和原始结构。

### `job-skills/`

用于工作与职场场景，包括合同审查、Offer 对比、简历优化、面试准备、薪资谈判、入职离职流程和职场沟通

## 使用方式

当前仓库暂不假设任何包管理器或自动安装机制。最稳妥的用法是克隆仓库，然后按需把具体 skill 目录复制或引用到本地 Agent/Codex 的技能目录中

```bash
git clone https://github.com/VectorPeak/vectorpeak-agent-skills.git
```

## Skill 编写规范

每个 skill 使用独立目录，最小结构如下：

```text
dev-skills/example-skill/
├── SKILL.md             # 必需：技能入口说明
├── README.md            # 必需：人类可读说明，参考已有 skill README 风格
├── agents/
│   └── openai.yaml      # 推荐：Codex / OpenAI UI 元数据
├── scripts/             # 可选：自动化脚本
├── references/          # 可选：参考材料
└── templates/           # 可选：输出模板
```

命名使用短小、清晰的小写连字符格式：

```text
debug-failing-build
review-pr-comments
explain-paper-top-down
extract-concept-map
```

一个合格的 `SKILL.md` 至少回答这些问题：

- 什么时候应该使用这个 skill
- 这个 skill 需要哪些输入
- Agent 应该按什么步骤执行
- 最终应该输出什么
- 如何验证结果是可靠的
- 哪些行为应该避免

## Skill 入库流程

新增或更新 skill 时，遵循 [`CONTRIBUTING.md`](CONTRIBUTING.md) 中的入库规则。

核心要求：

- 新 skill 必须说明输入要求、输出结果、工作流程和验证方式。
- 新 skill 必须生成自己的 `README.md`，并参考仓库已有 skill 的 README 风格。
- 入库前必须经过多 agent 审查，至少覆盖触发条件、可执行性、安全边界和 README 可读性。
- 当用户要求本地更新、入库、同步或上传时，默认同步到远端仓库 `VectorPeak/vectorpeak-agent-skills`。
- 同步远端时使用独立分支和 draft PR，且只提交本次 skill 相关文件。
- PR 会通过 GitHub Actions 检查 `Multi-Agent Review` 记录，防止 Agent 忘记写审查结论。

新 README 可从 [`templates/skill/README.md`](templates/skill/README.md) 复制起步。

## 许可证

本仓库使用 [Apache License 2.0](LICENSE)，SPDX 标识为 `Apache-2.0`

这个许可证适合同时包含文档、模板和脚本的技能仓库：它允许使用、修改、分发和私有使用，同时提供明确的专利授权与免责声明

如果后续引入第三方模板、脚本片段、论文摘录或外部资料，应在对应目录 README 或 `NOTICE` 中单独标明来源与许可
