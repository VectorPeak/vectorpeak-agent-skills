<h1 align="center">
  Daily Notes VP | 原始学习日记记录技能
</h1>

<p align="center">
  把每天学习时产生的短期目标、疑问和概念，轻量追加到 raw 层的 10 天周期 DailyNotes Markdown 文件中
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/daily--notes--vp-notes-green" alt="daily notes vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
零散学习输入  ->  Goal / Question / Concept 分类  ->  10 天一个 Markdown  ->  后续整理到 Wiki
```

---

## 为什么要做 Daily Notes VP?

学习时最容易丢的不是完整文章，而是那些随手冒出来的小目标、疑问和概念碎片。

Daily Notes VP 解决的是“快速记录，不打断学习流”的问题。当用户说“记一下这个问题”“今天的目标是”“这个概念先放到 daily notes”时，Agent 不需要生成一篇完整 Wiki，也不需要追问复杂分类，而是把内容轻量追加到 raw 原始语料层。

核心策略是 **raw-first, lightweight, reviewable**：

- 按 10 天一个文件聚合，避免单日文件太碎
- 每天内部固定按 `Goal-目标 -> Question-疑问 -> Concept-概念` 排列
- 不记录具体时间点，标题直接使用问题、目标或概念名称
- 不使用“原始记录 / 快速整理 / 标签”这类繁琐小标题
- 标签直接放在标题后，后续动作只在需要时写一行
- 只做 raw 记录，不主动生成 Wiki 页面

## 适用场景

典型触发语：

```text
记一下这个问题
添加到 daily notes
今天的 goal 是搞清楚 RAG 分块
这个概念先记一下
把这个疑问放到 01.raw/02.DailyNotes
用 daily-notes-vp 记录
```

适合记录：

- 今日短期学习目标
- 学习中产生的疑问
- 面试题或待复习问题
- 新遇到的概念、术语和机制
- 暂时还没整理成 Wiki 的理解片段
- 之后需要回看的学习线索

不适合记录：

- API Key、Token、密码和账号凭据
- 大段文章全文或大段源码
- 已经需要正式成文的 Wiki 页面
- 没有标注不确定性的最终结论

## 默认写入位置

默认写入当前 vault 的：

```text
01.raw/02.DailyNotes/YYYY-MM-DD_YYYY-MM-DD.md
```

按 10 天分桶：

```text
2026-06-01_2026-06-10.md
2026-06-11_2026-06-20.md
2026-06-21_2026-06-30.md
```

## Markdown 结构

每个文件创建时包含极简说明：

```markdown
---
type: daily-notes
date_range: 2026-06-11_2026-06-20
created: 2026-06-11
updated: 2026-06-17
tags:
  - daily-notes
  - raw
  - learning
ai-first: true
---

## For future Claude

这是原始学习记录，后续可整理到 Wiki。
```

每天固定三块：

```markdown
## 2026-06-17

### Goal-目标

### Question-疑问

### Concept-概念
```

单条记录使用紧凑格式：

```markdown
#### 1. 为什么 chunk size 不能固定成一个经验值？ #rag #chunking

固定经验值容易切得太小丢上下文，或切得太大降低召回精度。更合理的做法是结合语义边界、文档结构、embedding 表达能力和检索场景来定。

后续：整理成 Wiki/questions 页面。
```

## 完整示例

```markdown
## 2026-06-17

### Goal-目标

#### 1. 搞清楚 RAG 分块策略 #rag

今天想把 chunk size、chunk overlap、语义边界这几个点串起来。

### Question-疑问

#### 1. 为什么 chunk size 不能固定成一个经验值？ #rag #chunking

固定经验值容易切得太小丢上下文，或切得太大降低召回精度。更合理的做法是结合语义边界、文档结构、embedding 表达能力和检索场景来定。

后续：整理成 Wiki/questions 页面。

### Concept-概念

#### 1. Semantic Chunking #rag #concept

Semantic chunking 是按语义边界切分文本，而不是机械按 token 数切。它更适合问答和知识库场景，但实现成本更高。
```

## Skill 文件结构

```text
daily-notes-vp/
├── SKILL.md
├── README.md
└── agents/
    └── openai.yaml
```

其中：

- `SKILL.md`：定义触发场景、写入路径、10 天分桶、分类规则和条目格式
- `README.md`：说明 skill 的用途、默认结构和示例
- `agents/openai.yaml`：提供 Codex/Agent UI 中展示用的名称、描述和默认提示

## 与其他 Skill 的关系

- `daily-notes-vp` 记录个人日常学习原始材料，位置是 `01.raw/02.DailyNotes`
- 如果用户明确要求整理成正式知识页，可以在记录之后再使用 Wiki/知识整理类 workflow
