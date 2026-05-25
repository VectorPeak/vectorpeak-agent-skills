<h1 align="center">
  VectorPeak Agent Skills | 个人 Agent 技能库
</h1>

<p align="center">
  Reusable agent skills for software development, knowledge work, and life admin
  <br>
  用于沉淀个人工程开发、知识工作与生活事务的 Agent / Codex Skills 仓库
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="dev-skills/"><img src="https://img.shields.io/badge/dev--skills-engineering-brightgreen" alt="dev skills"></a>
  <a href="knowledge-skills/"><img src="https://img.shields.io/badge/knowledge--skills-learning-purple" alt="knowledge skills"></a>
  <a href="life-skills/"><img src="https://img.shields.io/badge/life--skills-admin-teal" alt="life skills"></a>
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

`VectorPeak Agent Skills` 是一个个人 Agent 技能库，用来保存日常工程开发、知识沉淀和生活事务中反复出现、值得复用的工作方法

这里的 skill 不是一次性 prompt，而是一组可迁移的工作规程：它应该说明何时使用、需要什么输入、按什么步骤执行、如何验证结果，以及应该避免什么

换句话说，agent skill（智能体技能）更像一份“可执行的工作说明书”：它把人的经验压缩成稳定流程，让 Agent 在相似场景下少猜、多验证、按规程完成任务

## 为什么存在

开发、学习和生活里的很多问题并不是第一次遇到：构建失败、代码审查、论文处理、概念解释、笔记整理、旅行准备、订阅审计、生活事项拆解，这些任务背后都有稳定的判断路径

这个仓库的目标是把这些路径沉淀为 Agent 可以直接调用的技能，让经验从“临场发挥”变成“可复用流程”

## 核心结构

```text
.
├── dev-skills/          # 工程开发技能：debug、review、test、CI/CD、release
├── knowledge-skills/    # 知识沉淀技能：学习法、论文处理、概念解释、笔记整理
├── life-skills/         # 生活事务技能：计划拆解、旅行准备、消费决策、日常复盘
├── README.md            # 仓库说明
└── LICENSE              # Apache-2.0 license
```

## Skill 分类

### `dev-skills/`

用于工程开发场景，包括编码、调试、测试、代码审查、架构分析、构建修复、发布流程、CI/CD、仓库维护和本地自动化

### `knowledge-skills/`

用于知识工作场景，包括自顶向下学习、概念解释、论文阅读、文章摘要、知识地图抽取、笔记整理、学习检查和写作流程

### `life-skills/`

用于生活事务场景，包括生活事项拆解、旅行准备、消费决策、就医预约、订阅审计、家庭维护、习惯流程和每周复盘

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

## 许可证

本仓库使用 [Apache License 2.0](LICENSE)，SPDX 标识为 `Apache-2.0`

这个许可证适合同时包含文档、模板和脚本的技能仓库：它允许使用、修改、分发和私有使用，同时提供明确的专利授权与免责声明

如果后续引入第三方模板、脚本片段、论文摘录或外部资料，应在对应目录 README 或 `NOTICE` 中单独标明来源与许可
