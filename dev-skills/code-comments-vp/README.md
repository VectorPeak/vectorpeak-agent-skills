<h1 align="center">
  Code Comments VP | 可维护代码注释技能
</h1>

<p align="center">
  为代码补充面向维护者的模块职责、执行流程、边界、副作用、fallback 和设计原因说明
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-dev--skills-brightgreen" alt="dev skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/code--comments--vp-comments-green" alt="code comments vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
代码片段 / 文件  ->  判断注释粒度  ->  补充职责与执行流  ->  标注原因、边界与兜底  ->  可维护注释
```

---

## 为什么要做 Code Comments VP?

代码注释最容易走向两个极端：要么完全没有，后续维护者只能靠猜；要么逐行解释语法，噪声比帮助还多。

Code Comments VP 解决的是“把代码写成可维护说明书”的问题。它默认不追求密集注释，而是优先补充模块职责、函数执行流程、参数来源、返回结构、异常边界、状态副作用和 fallback 策略，让后来的人能快速理解这段代码在系统链路里的位置。

核心策略是 **coarse-first, reason-focused, fallback-aware**：

- 默认先写粗粒度模块 / 类 / 函数 docstring
- 只有复杂分支、异步、缓存、状态修改、外部调用、安全校验、性能选择和 fallback 才加块级注释
- 优先解释“为什么这样写”和“这段代码承担什么责任”
- 避免逐行解释明显语法
- 遇到 fallback、降级、空结果和提前返回时必须说明触发条件与安全原因

## 适用场景

典型触发语：

```text
帮这个文件加注释
优化一下注释
写中文代码注释
按这个项目的风格补注释
检查这个函数注释够不够
让这段代码更好维护
用 code-comments-vp 处理
```

适合处理：

- API / service / pipeline / adapter / config 文件的模块说明
- 核心函数的执行流程 docstring
- 复杂业务规则的优先级说明
- 异步、线程池、缓存、状态 mutation 的原因说明
- 数据库写入、网络调用、trace 写入、事件推送等副作用
- fallback、degrade、default behavior 和 insufficient context 分支
- 已有注释的统一风格改写

不适合处理：

- import 逐行解释
- 简单 getter / setter 的长模板注释
- 第三方 vendor、生成文件、minified 文件
- 用注释掩盖命名混乱或结构问题
- 未经用户要求就重写业务逻辑

## 工作原理

1. **识别注释意图**：先判断是粗粒度补注释、细粒度块注释、注释审查、注释改写，还是风格迁移。

2. **选择默认粒度**：默认使用粗粒度注释，先补模块 docstring、类 docstring 和核心函数 docstring。

3. **判断细粒度触发点**：只有遇到复杂分支、提前返回、异常处理、异步/线程池、缓存、数据库写入、外部 API 调用、安全校验、性能优化、状态 mutation、业务规则优先级或 fallback 时，才补块级注释。

4. **标注 fallback**：当代码存在空结果、失败查询、异常降级、缓存 miss、模型/API 不可用、验证失败转用户提示等路径时，必须说明触发条件、返回内容、为什么安全，以及主流程是否继续。

5. **审查注释密度**：完成后检查是否解释了职责、流程、边界、副作用和原因，同时删掉只重复语法的注释。

## 快速上手

### 1. 给文件补粗粒度注释

```text
用 code-comments-vp 给 qa_core/api/chat.py 补模块和核心函数注释，保持中文风格。
```

Agent 应优先补充：

- 文件处在哪一层
- 接收什么输入
- 调用哪些下游能力
- 产出什么结果
- 哪些职责属于边界层，哪些不属于

### 2. 给复杂分支补细粒度注释

```text
这段 if/else 和 fallback 有点绕，用 code-comments-vp 加一点细粒度说明。
```

Agent 应只在关键块前添加类似注释：

```python
# 兜底：检索上下文为空时直接返回确定性提示，避免把空上下文交给 LLM 造成幻觉。
if not context_docs:
    return build_insufficient_context_answer()
```

### 3. 按已有项目风格迁移

```text
参考 chat.py / service.py 的注释风格，给这个新模块补注释。
```

Agent 应先抽取样例风格，再应用到目标代码，不照搬无关业务内容。

## 目录结构

```text
code-comments-vp/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    └── comment-patterns.md
```

## 参考材料

`references/comment-patterns.md` 包含：

- 默认模块 docstring 模板
- 函数 docstring 模板
- import 下方模块级对象说明
- 细粒度 `原因 / 说明 / 兜底` 注释模板
- fallback 注释规则
- KnowForge RAG 项目中的真实注释风格样例

## 验证方式

使用该 skill 后，至少检查：

- 模块 docstring 是否解释职责和边界
- 重要函数是否说明执行流程
- 参数是否说明来源、含义和影响范围
- 返回值是否说明结构和关键字段
- fallback 路径是否说明触发条件和安全原因
- 副作用是否明确，例如 DB 写入、trace 写入、网络调用、缓存更新或事件推送
- inline comment 是否解释原因，而不是重复代码
- 注释密度是否与代码复杂度匹配
