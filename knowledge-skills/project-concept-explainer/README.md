<h1 align="center">
  Project Concept Explainer | 项目伴读与技术概念讲解技能
</h1>

<p align="center">
  读取项目上下文，解释关键技术名词、模型算法、配置项、数据字段和架构决策，并生成项目知识地图
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/project--concept--explainer-study-blueviolet" alt="project concept explainer"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
项目上下文  ->  概念识别  ->  自顶向下讲解  ->  知识地图/术语表/学习笔记
```

---

## 为什么要做 Project Concept Explainer?

做项目时真正困难的地方往往不是“知道某个词”，而是知道这个词在当前项目里为什么出现、解决什么问题、和哪些概念容易混淆、如果理解错会带来什么风险

Project Concept Explainer 解决的是“边做项目边学习项目”的问题。它不是百科式术语解释，而是让 Agent 先读取仓库上下文，再结合 README、docs、scripts、configs、notebooks 和 reports，把关键概念讲成可理解、可追踪、可沉淀的学习材料

核心策略是 **context-first, top-down, project-grounded**：

- 先看当前项目结构和相关文件，再解释概念
- 先讲整体问题，再进入定义、公式、例子和误区
- 不只解释术语本身，还解释它在项目里的角色和边界
- 重要概念要补充相邻概念、反向概念和常见误区

## 工作原理

1. **上下文读取**：优先读取 `README.md`、`AGENTS.md`、`docs/`、`data/reports/`、`configs/` 和相关 `scripts/`

2. **概念识别**：从用户问题或项目文件中识别业务术语、数据字段、模型算法、训练配置、评估指标、检索/RAG 组件和工程接口

3. **模式选择**：根据问题选择解释模式

   - 单个术语深度讲解
   - 多个概念对比
   - 项目知识地图
   - glossary / learning notes / research notes

4. **自顶向下讲解**：按“直觉 -> 项目角色 -> 严谨定义 -> 对比概念 -> 项目例子 -> 常见误区”的顺序解释

5. **文件定位**：如果概念来自具体文件，给出可点击路径，帮助用户回到代码、配置或报告里验证

6. **沉淀输出**：当用户明确要求时，生成 Markdown 文档，例如 `docs/glossary.md`、`docs/project_knowledge_map.md` 或 `docs/research_notes.md`

## 快速上手

### 1. 解释项目里的技术名词

```text
使用 project-concept-explainer，解释这个项目里的 BM25、FAISS、Hard Negative Mining
```

适合用来理解模型、算法、配置项、数据字段和工程组件

### 2. 比较容易混淆的概念

```text
使用 project-concept-explainer，比较 BM25、MiniLM、SimCSE 和 Hard Negative Mining
```

输出会先解释它们共同属于哪一类问题，再说明差异、适用场景和错误选择的风险

### 3. 生成项目知识地图

```text
使用 project-concept-explainer，扫描当前项目并生成一份项目知识地图
```

知识地图会按层组织概念，例如：

```text
业务概念  ->  数据与标签  ->  清洗处理  ->  模型算法  ->  训练评估  ->  检索/RAG  ->  API/前端
```

### 4. 生成术语表或学习笔记

```text
使用 project-concept-explainer，把这个仓库的核心术语整理成 docs/glossary.md
```

只有当用户明确要求生成持久化文档时，skill 才会写入文件

## 输出格式

单个概念解释通常包含：

```text
一句话直觉
项目里的作用
严谨定义
相关/相反/易混概念
当前项目例子
常见误区
下一步建议
```

项目知识地图通常包含：

```text
项目主线
核心概念分层
必须现在理解的概念
可以后续学习的概念
相关文件路径
术语表或学习笔记入口
```

## 目录结构

```text
project-concept-explainer/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── concept_categories.md
    └── explanation_style.md
```

## 注意事项

- 优先结合项目上下文解释，不输出脱离项目的百科定义
- 如果项目证据不足，需要明确说明哪些是推断
- 不主动生成文件；只有用户要求 glossary、learning notes、research notes 或知识地图文档时才写入
- 生成中文文件时默认使用 UTF-8
- 解释重要概念时要补充常见误区和“不知道自己不知道”的风险
- 引用本地项目文件时尽量给出可点击路径
