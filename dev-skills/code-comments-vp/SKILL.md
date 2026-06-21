---
name: code-comments-vp
description: Add, rewrite, review, or standardize maintainable code comments and docstrings. Use when the user asks to add comments, improve comments, write Chinese code comments, document modules/classes/functions, explain code through comments, follow an existing code comment style, or make code easier for future maintainers to understand. Default to coarse-grained module/function comments, and add fine-grained block comments only for complex control flow, async/concurrency, caching, fallback behavior, state mutation, external calls, safety checks, performance choices, or business rule priority.
---

# Code Comments VP

## Goal

Write maintainable comments that explain responsibility, execution flow, boundaries, side effects, fallback behavior, and design reasons.

Golden rule:

优先解释“为什么这样写”和“这段代码在链路中承担什么责任”，少解释“这行代码语法上做了什么”。

## Mode Selection

Choose one mode before editing:

- **coarse**: Add or improve comments for a file, module, class, or function. This is the default.
- **fine**: Add detailed block comments because the user asks for细粒度/逐段/逐行 comments, or the code contains complex branching, async/concurrency, cache, fallback, state mutation, external calls, security checks, performance-sensitive logic, or business rule priority.
- **review**: Review whether comments are sufficient. Lead with findings and suggestions before changing anything.
- **rewrite**: Existing comments are inaccurate, noisy, inconsistent, or too shallow. Preserve correct meaning and rewrite in this style.
- **style-transfer**: The user points to an example file. First extract the comment style, then apply it to the target code.

## Default Style

Default to coarse-grained comments. Prefer module docstrings, class docstrings, and function docstrings before inline comments.

Use Chinese comments by default when the user uses Chinese or the surrounding project comments are Chinese.

Use these section labels when useful:

- `执行流程：`
- `参数：`
- `返回：`
- `Yields:`
- `异常：`
- `说明：`
- `字段说明：`
- `规则说明：`
- `兜底策略：`

Read `references/comment-patterns.md` when adding or rewriting more than one docstring, when the user asks for a reusable style, or when fallback/import-level comments are involved.

## Coarse-Grained Template

Use this module docstring for most Python files:

```python
"""模块职责一句话。

说明这个文件处在哪一层、接收什么输入、调用哪些下游能力、产出什么结果。
如果是 API / service / pipeline / adapter / config 文件，说明它的边界职责。
"""
```

Use this function docstring for important functions:

```python
def some_function(...):
    """一句话说明这个函数在业务链路中的作用。

    执行流程：
    1. ...
    2. ...
    3. ...

    参数：
        xxx: 来源、含义、影响范围。

    返回：
        xxx: 返回内容和关键字段含义。

    异常：
        xxx: 什么时候抛出，调用方应如何理解。
    """
```

For generators or streaming functions, include `Yields:`. For functions with fallback behavior, include `兜底策略：`.

## Fine-Grained Comments

Only add fine-grained comments for:

- 复杂 if/else 分支
- 提前 return
- 异常处理
- 并发 / 异步 / 线程池
- 缓存
- 数据库写入
- 外部 API 调用
- 安全校验
- 性能优化
- 状态 mutation
- 业务规则优先级
- fallback / degrade / default behavior

Preferred inline patterns:

```python
# 原因：这里先校验权限，避免后续昂贵的检索/模型调用被非法请求触发。
validate_permission(user)
```

```python
# 说明：此分支是确定性直答，命中后会提前返回，不再进入后续检索链路。
if direct_answer:
    return direct_answer
```

```python
# 兜底：外部服务无结果时返回本地默认配置，保证主链路可继续执行。
config = remote_config or default_config
```

## Import-After Notes

After imports, add comments for module-level objects only when they clarify runtime behavior, dependency ownership, or import-time side effects.

Use this especially for routers, app objects, settings/config singletons, loggers, caches, stores/clients, registries, and global constants with business meaning.

Do not comment imports one by one.

## Fallback Rule

Always document fallback behavior when code has one of these patterns:

- default value after failed lookup
- empty retrieval result handling
- try/except that returns a degraded response
- timeout/circuit-breaker fallback
- cache miss fallback
- model/API unavailable fallback
- insufficient context fallback
- validation failure converted into a user-facing message

Fallback comments should answer what triggers the fallback, what is returned, why the degradation is safe, and whether the main flow continues or returns early.

## Boundaries

Do not:

- Explain obvious syntax.
- Add comments to every line by default.
- Add full docstring templates to trivial getters or one-line wrappers.
- Invent business facts not visible from code.
- Use comments to hide unclear naming or broken structure.
- Rewrite business logic unless the user explicitly asks.
- Add comments to generated, vendored, or minified files unless explicitly requested.

## Review Checklist

Before finishing:

- Does the module docstring explain this file's responsibility and boundary?
- Do important functions explain execution flow?
- Are parameters described by source, meaning, and impact?
- Are return values described by structure and key fields?
- Are fallback paths documented?
- Are side effects documented, such as DB writes, trace writes, network calls, cache updates, or event pushes?
- Do inline comments explain reasons instead of repeating code?
- Is comment density appropriate for the code complexity?
