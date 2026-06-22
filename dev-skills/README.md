<h1 align="center">
  Dev Skills | 工程开发技能
</h1>

<p align="center">
  Reusable agent skills for coding, debugging, review, testing, CI/CD, and release work
  <br>
  用于编码、调试、审查、测试、CI/CD 与发布流程的 Agent / Codex Skills
</p>

<p align="center">
  <a href="../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/category-dev--skills-brightgreen" alt="dev skills"></a>
  <a href="../knowledge-skills/"><img src="https://img.shields.io/badge/knowledge--skills-learning-purple" alt="knowledge skills"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

<p align="center">
  简体中文 | English later
</p>

```text
engineering problem  ->  repeatable practice  ->  SKILL.md  ->  reliable agent workflow
```

---

## 简介

`dev-skills/` 用来存放工程开发相关的 Agent 技能，覆盖编码、调试、测试、代码审查、架构分析、构建修复、CI/CD、发布流程和仓库维护

这里的 skill 不是某一次修 bug 的记录，而是从反复出现的工程任务里抽出的稳定流程：触发条件是什么、应该读哪些上下文、如何定位问题、如何验证结果、哪些操作需要避免

## 为什么存在

工程问题经常看起来不同，本质却重复：构建失败、测试红灯、依赖冲突、PR 评论、发布前检查、仓库结构混乱。把这些处理路径沉淀成 skill，可以让 Agent 少走弯路，也让每次处理更容易复盘

这个目录的目标是保存“可执行的工程经验”，让开发流程从临时判断变成可重复、可检查、可维护的工作流

## 核心结构

```text
dev-skills/
├── opensense-pr-attempt-vp/  # OpenSense 开源 PR 尝试工作流
├── pr-case-collector-vp/     # GitHub PR 案例收集工作流
├── profile-readme-github-vp/ # GitHub Profile README 自动更新工作流
├── code-comments-vp/         # 可维护代码注释与 docstring 工作流
└── README.md                 # 工程类技能目录说明
```

## 当前技能

- [`code-comments-vp`](code-comments-vp/)：为代码补充面向维护者的模块职责、执行流程、边界、副作用、fallback 和设计原因说明，默认粗粒度，复杂逻辑再加细粒度块注释。
- [`opensense-pr-attempt-vp`](opensense-pr-attempt-vp/)：使用 OpenSense 从 watchlist 中筛选 issue，生成 PR 前计划、上下文包、sandbox 执行记录、测试证据和本地 PR 草稿。
- [`pr-case-collector-vp`](pr-case-collector-vp/)：把真实 GitHub PR 按项目、改动类型、评级和备注收录为 LLM 可参考的简表案例库。
- [`profile-readme-github-vp`](profile-readme-github-vp/)：生成 VectorPeak GitHub Profile README，支持公开项目 facts 收集、stars 更新、中英双语表格、自动补全新公开仓库，并排除 `VectorPeak/VectorPeak` profile 仓库本身。

## 适合沉淀的技能

- 系统化调试流程
- 构建与测试修复
- 代码审查清单
- 架构调查与模块梳理
- CI/CD 故障排查
- 发布与 PR 工作流
- 仓库维护
- 本地开发自动化

## 编写原则

每个工程类 skill 都应该围绕可验证结果来写。它不只描述“怎么做”，还要说明“如何知道做对了”

一个工程类 skill 至少应该回答：

- 这个 skill 处理哪类工程问题
- 触发前需要收集哪些上下文
- Agent 应该读哪些文件、跑哪些命令
- 哪些改动属于当前范围，哪些应该避免
- 应该如何测试、构建或复现
- 如果验证失败，下一步怎么缩小问题
