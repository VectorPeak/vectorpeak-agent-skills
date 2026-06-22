<h1 align="center">
  PR Case Collector VP | PR 案例收集技能
</h1>

<p align="center">
  把真实 GitHub PR 简要收录为 LLM 可参考的案例表
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-dev--skills-brightgreen" alt="dev skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/pr--case--collector-vp-green" alt="pr case collector vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
GitHub PR 链接  ->  查看改动规模  ->  判断难度  ->  追加到 PR 案例参考库
```

---

## 为什么要做 PR Case Collector VP?

开源 PR 是训练和校准 LLM coding agent 的好材料，但零散链接很快会丢失上下文。这个 skill 把真实 PR 按“项目、改动类型、评级、备注”收进一个轻量表格，方便以后复用为 prompt 样例、review 样例或难度判断样例。

核心目标是：**短、准、可追加**。每个 PR 默认只写一行，不展开成长篇分析。

## 适用场景

典型触发语：

```text
把这个 PR 收进案例库
记录这个 GitHub PR 给 LLM 参考
这个 PR 评级一下
用 pr-case-collector-vp 处理
```

适合处理：

- GitHub Pull Request 链接
- 小型开源 PR 案例
- 需要给 LLM 留作参考的 PR 样例
- PR 难度粗分类：简单 / 中等 / 困难

不适合处理：

- 需要完整代码审查的 PR
- 需要本地复现和测试的大型变更
- 私有仓库或不能公开记录的 PR
- 没有 URL 且无法定位来源的口头描述

## 工作流程

1. 读取目标 vault 的 `_CLAUDE.md`。
2. 确认案例库文件存在：`E:\LLM_wiki\LLM_wiki\01.raw\10.GitHub\LLM_PR案例参考库.md`。
3. 查看 PR 页面或 diff，提取项目、改动类型、规模和风险。
4. 按简单 / 中等 / 困难给出评级，优先采用用户显式评级。
5. 在 `## PR 案例` 表格中追加一行。
6. 如果 PR 已存在，只在用户要求或明显纠错时更新已有行。

## 目录结构

```text
pr-case-collector-vp/
├── SKILL.md
├── README.md
└── agents/
    └── openai.yaml
```

## 验证方式

使用该 skill 后，至少检查：

- PR URL 是否保留原文链接
- 项目是否使用 `[[wikilink]]`
- 评级是否符合改动规模和风险
- 备注是否足够短，且能说明为什么适合作为 LLM 参考
- 表格格式是否仍然可读
- 是否没有写成长篇 PR dossier

