# GitHub Card Templates

## Repository Card

```markdown
---
type: github-source
source_type: repository
repo: owner/repo
url: https://github.com/owner/repo
date: YYYY-MM-DD
tags:
  - github
  - source/raw
  - repository
status: raw
ai-first: true
---

## For future Claude

这是一份 GitHub 仓库级原始语料卡片。优先使用它理解项目定位、架构入口、可读模块、可贡献方向，以及它和用户知识库中其他概念的关系。

## 一句话价值


## 项目背景

- 仓库：`owner/repo`
- 技术栈：
- 主要用途：
- 适合学习的问题：

## 结构入口

- README：
- 核心目录：
- 值得继续阅读的模块：

## 可迁移经验

- 对项目学习：
- 对工程实现：
- 对面试表达：
- 对 LLM/code-agent：

## 关联

- 相关概念：[[...]]
- 相关案例：[[...]]

## 原始链接

- Source: https://github.com/owner/repo
```

## Engineering Case Card

```markdown
---
type: github-source
source_type: pull_request | issue | discussion | commit
repo: owner/repo
github_id: PR-1234
url: https://github.com/owner/repo/pull/1234
date: YYYY-MM-DD
tags:
  - github
  - source/raw
  - engineering-case
status: raw
ai-first: true
---

## For future Claude

这是一份 GitHub 工程案例卡片。重点不是复述链接，而是提取“问题 -> 修复/讨论 -> 验证 -> 可迁移经验”。

## 一句话价值


## 问题是什么？


## 解决或讨论路径


## 关键代码 / 设计点


## 测试与验证


## 可迁移经验

- 对 PR 写作：
- 对代码修复：
- 对系统设计：
- 对面试表达：
- 对自己的项目：

## 关联

- 相关项目：[[...]]
- 相关概念：[[...]]
- 相关模式：[[...]]

## 原始链接

- Source: https://github.com/owner/repo/pull/1234
```

## Code Reading Card

```markdown
---
type: github-source
source_type: code-reading
repo: owner/repo
url: https://github.com/owner/repo/blob/main/path/to/file
date: YYYY-MM-DD
tags:
  - github
  - source/raw
  - code-reading
status: raw
ai-first: true
---

## For future Claude

这是一份源码阅读卡片。优先使用它解释模块职责、调用链、关键抽象、边界条件和可迁移实现方式。

## 阅读对象

- 仓库：`owner/repo`
- 路径：`path/to/file`
- 关注点：

## 模块职责


## 关键调用链


## 关键抽象


## 容易忽略的点


## 可迁移经验


## 原始链接

- Source: https://github.com/owner/repo/blob/main/path/to/file
```

## Batch Final Report Shape

```markdown
已处理 5 个 GitHub URL：成功 4 个，重复跳过 1 个，失败 0 个。

| Source | Category | Output | Status |
|---|---|---|---|
| owner/repo | Repository | `.../01.Repositories/owner__repo.md` | created |
| owner/repo#123 | Case | `.../02.Cases/owner__repo__PR-123__topic.md` | updated |
```