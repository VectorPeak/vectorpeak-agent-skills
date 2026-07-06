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

`VectorPeak Agent Skills` 是一个个人 Agent 技能库，用来保存日常工程开发、知识沉淀和工作职场场景中反复出现、值得复用的工作方法。

这里的 skill 不是一次性 prompt，而是一组可迁移的工作规程：它应该说明何时使用、需要什么输入、按什么步骤执行、如何验证结果，以及应该避免什么。

## 核心结构

```text
.
├── dev-skills/          # 工程开发技能
├── knowledge-skills/    # 知识沉淀技能
├── job-skills/          # 工作职场技能
├── README.md            # 仓库说明
└── LICENSE              # Apache-2.0 license
```

## Skill 分类

### `dev-skills/`

- [`code-comments-vp`](dev-skills/code-comments-vp/)：代码注释与 docstring 工作流。
- [`pr-workflow-vp`](dev-skills/pr-workflow-vp/)：开源 PR 工作流。
- [`profile-readme-vp`](dev-skills/profile-readme-vp/)：GitHub Profile README 自动更新工作流。

### `knowledge-skills/`

- [`ai-learning-mentor-vp`](knowledge-skills/ai-learning-mentor-vp/)：AI 学习导师。
- [`daily-notes-vp`](knowledge-skills/daily-notes-vp/)：原始学习日记。
- [`gif-showcase-maker-vp`](knowledge-skills/gif-showcase-maker-vp/)：GIF 展示图生成。
- [`github-clippings-vp`](knowledge-skills/github-clippings-vp/)：GitHub 材料剪藏。
- [`image-to-markdown-vp`](knowledge-skills/image-to-markdown-vp/)：图片 OCR 到 Markdown。
- [`paper-fetcher-vp`](knowledge-skills/paper-fetcher-vp/)：论文识别与下载。
- [`wechat-clippings-vp`](knowledge-skills/wechat-clippings-vp/)：微信公众号剪藏。
- [`zhihu-clippings-vp`](knowledge-skills/zhihu-clippings-vp/)：知乎剪藏。

### `job-skills/`

- [`contributions-graph-filler-vp`](job-skills/contributions-graph-filler-vp/)：GitHub 贡献图补全计划。
- [`feishu-interview-minutes-vp`](job-skills/feishu-interview-minutes-vp/)：飞书面试纪要整理。
- [`job-contract-review-vp`](job-skills/job-contract-review-vp/)：合同审查。
- [`xiaohei-daily-query-vp`](job-skills/xiaohei-daily-query-vp/)：小黑日报查询。

## 使用方式

```bash
git clone https://github.com/VectorPeak/vectorpeak-agent-skills.git
```

## 许可证

本仓库使用 [Apache License 2.0](LICENSE)，SPDX 标识为 `Apache-2.0`。