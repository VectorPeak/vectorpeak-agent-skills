# Comment Patterns

Use this reference when a task needs more than one or two comments, or when the code contains fallback behavior, import-level module objects, streaming, async, state mutation, or business-rule branching.

## Module Docstrings

Default module template:

```python
"""模块职责一句话。

说明这个文件处在哪一层、接收什么输入、调用哪些下游能力、产出什么结果。
如果是 API / service / pipeline / adapter / config 文件，说明它的边界职责。
"""
```

API/router variant:

```python
"""API 层模块职责一句话。

将外部 HTTP/WebSocket 请求转换为应用层调用，并负责参数解析、限流、异常转响应、
事件转发等入口边界职责。业务规则应保留在 service / pipeline 层。

路由结构：
  GET  /path     - 做什么
  POST /path     - 做什么
"""
```

Pipeline/workflow variant:

```python
"""主流程编排模块职责一句话。

按固定阶段串联上下文创建、规则判断、外部依赖调用、结果组装、兜底处理和收尾副作用。
细节逻辑应下沉到 step/helper 函数，主流程只负责阶段顺序和分支收口。
"""
```

## Import-After Module Notes

Add a short note below imports only when module-level objects matter.

```python
# 模块级对象：注册当前 API 路由并加载轻量级共享依赖。
# 这里不保存请求级状态；每次请求的业务上下文由请求解析对象、service 或 pipeline 创建。
router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)
```

For caches or clients:

```python
# 模块级缓存：复用昂贵的只读配置，避免每次请求重复加载。
# 不缓存用户输入或请求级状态，防止跨请求串扰。
_config_cache: dict[str, Config] = {}
```

Avoid:

```python
# 导入 json
import json
```

## Function Docstrings

Default function template:

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

Generator/streaming variant:

```python
def stream_items(...) -> Generator[dict[str, Any], None, None]:
    """按阶段产生事件流，供上游逐个转发给调用方。

    执行流程：
    1. 创建请求级上下文。
    2. 依次执行确定性分支、外部检索和结果生成。
    3. 每个阶段产出 status/token/end/error 等事件。

    Yields:
        dict[str, Any]: 流式事件，包含 type 字段和当前阶段负载。

    兜底策略：
        任一阶段失败时产出 error 事件，不让调用方等待无结果的流。
    """
```

Boundary/validation variant:

```python
def validate_source(...):
    """校验调用方传入的过滤条件是否在当前业务白名单内。

    参数：
        source_filter: 调用方传入的过滤项，影响后续数据访问范围。
        valid_sources: 当前上下文允许访问的过滤项集合。

    异常：
        ValueError: 当 source_filter 不在 valid_sources 中时抛出，调用方应转成可理解的错误响应。
    """
```

## Fine-Grained Comments

Use fine-grained comments only when the next block has non-obvious behavior.

Reason comment:

```python
# 原因：这里先校验权限，避免后续昂贵的检索/模型调用被非法请求触发。
validate_permission(user)
```

Branch comment:

```python
# 说明：此分支是确定性直答，命中后会提前返回，不再进入后续检索链路。
if direct_answer:
    return direct_answer
```

Async/thread comment:

```python
# 原因：同步检索会阻塞事件循环，因此放入线程池执行。
result = await asyncio.to_thread(search, query)
```

State mutation comment:

```python
# 说明：把路由结果写入请求上下文，供后续 end 事件和 trace 复用。
context.route_info.update(route_payload)
```

## Fallback Comments

Document fallback behavior whenever the normal path can fail or produce no usable result.

Fallback comment:

```python
# 兜底：检索上下文为空时直接返回确定性提示，避免把空上下文交给 LLM 造成幻觉。
if not context_docs:
    return build_insufficient_context_answer()
```

Fallback section in docstring:

```python
"""根据远端配置构造运行时参数。

执行流程：
1. 优先读取远端配置。
2. 远端配置缺失时读取本地默认配置。
3. 合并调用方显式覆盖项。

兜底策略：
    远端配置不可用时使用本地默认配置，保证主流程可启动；显式覆盖项仍然优先生效。
"""
```

Fallback comments should answer:

- 什么情况下触发 fallback
- fallback 返回什么
- 为什么这样降级是安全的
- 是否继续主流程，还是提前返回

## Density Guide

Use full docstrings for public APIs, service boundaries, pipeline orchestrators, core decision functions, and functions with non-obvious side effects.

Use short docstrings for helpers and data containers.

Use inline comments sparingly, mainly before surprising branches or operations.

Do not add comments that only repeat the syntax:

```python
# 如果 user 存在
if user:
    ...
```

## KnowForge-Style Examples

These examples come from the KnowForge RAG platform comment style. Use them as concrete style references when the user asks to follow the current project's comments.

### API Router Module

Use this style for API entry files that define routes and translate transport-level requests into service calls.

```python
"""API 层问答、历史、反馈和检索调试路由。将浏览器 HTTP/WebSocket 请求转换成 QAService 调用，
并组装响应。是整个系统的 HTTP 入口层，负责参数校验、限流、异常转 HTTP 错误码、WebSocket 事件转发。

路由结构：
  GET    /api/history/{session_id}       - 获取会话历史
  DELETE /api/history/{session_id}       - 清理会话历史
  WS     /api/stream                     - 流式问答（WebSocket、限流）
  POST   /api/retrieval/debug            - 检索诊断（同步、限流）
"""
```

Why this works:

- It states the layer: API/transport boundary.
- It states responsibility: parse, limit, convert errors, forward events.
- It lists external capabilities so maintainers can scan the file before reading functions.

### Service Boundary Function

Use this style for service-layer validation or delegation methods.

```python
def validate_source(self, source_filter: str | None, scenario: ScenarioDefinition) -> None:
    """校验 source_filter 是否在当前业务场景的合法来源白名单内。

    在 Milvus 检索之前调用，提前拒绝非法分类过滤条件。

    参数：
        source_filter: 前端传入的业务分类过滤项（可空，空时跳过校验）。
        scenario: resolve_scenario() 解析出的当前请求的场景定义，
                  从中读取 valid_sources 白名单。

    异常：
        ValueError: 当 source_filter 不为 None 且不在 scenario.valid_sources 中时抛出。
    """
```

Why this works:

- It explains when the validation happens, not just what it checks.
- It explains the source of each parameter.
- It documents how callers should understand the exception.

### Pipeline Orchestrator

Use this style for workflow functions that coordinate multiple stages and produce streaming events.

```python
def stream_query(...) -> Generator[dict[str, Any], None, None]:
    """一次完整问答请求的编排主入口，协调 Stage 0-7 管线并持续产出 WebSocket 事件流。★★★ 核心

    执行流程：
    Stage 0: 创建运行时上下文（场景/数据域/会话/trace/知识库版本）
    Stage 1: 低成本查询路由（直答/边界、FAQ 精确命中、继续检索）
    Stage 2: 检索准备（历史、意图、source、按需改写、检索计划、查询变体、Prompt Profile）
    Stage 3: FAQ 检索，判断是否直出
    Stage 4: 文档检索
    Stage 5: 上下文构建
    Stage 6: LLM 流式生成
    Stage 7: 写历史记录、写 trace、发送结束事件

    返回：
        Generator yielding WebSocket 事件 dict（包含事件类型和数据）
    """
```

Why this works:

- Stage labels give maintainers a mental map before reading implementation.
- It captures side effects: history writes, trace writes, event sending.
- It marks central orchestration functions with `★★★ 核心`; use this marker sparingly.

Stage comments should mirror the docstring:

```python
# ── Stage 1: Low-cost route decision ──
# 统一处理确定性直答、边界拦截和 FAQ 精确命中；未命中才进入检索准备。
route = decide_route(context)
```

### Business Decision Function

Use this style for functions where order matters and later steps depend on earlier deterministic checks.

```python
def decide_route(context: RAGQueryContext) -> RouteDecision:
    """统一的低成本查询路由：直答/边界、FAQ 精确命中、或继续完整检索准备。★★★ 核心

    这个阶段只做确定性、低成本决策：
    1. source_filter 校验；
    2. 问候、越界、短句转人工、source 边界直接返回；
    3. 短标准问答尝试 FAQ 精确命中，命中则以 FAQ_QUERY 意图直出；
    4. 都不命中时返回 retrieval，由后续 prepare_retrieval() 做检索准备。

    返回：
        RouteDecision: route=direct_answer / faq_exact / retrieval
    """
```

Why this works:

- It explains rule priority, which is often more important than individual statements.
- It tells readers which paths are terminal and which continue.
- It avoids burying the route semantics inside scattered inline comments.

### Fallback And Early Return

Use this style when the code deliberately avoids an expensive or risky downstream step.

```python
# 合并后上下文仍为空（所有候选低于分数阈值），直接返回确定性"信息不足"避免 LLM 幻觉
if context.hit_type == "insufficient_context":
    answer = build_insufficient_context_answer(context)
    yield from _finish_with_single_answer(context, history, query, answer, record_save_stage=True)
    return None
```

Why this works:

- It names the trigger: merged context is still empty / scores are too low.
- It names the fallback: deterministic insufficient-context answer.
- It names the safety reason: avoid LLM hallucination.

### Import-After Module Objects

For module-level objects created after imports, group the explanation around runtime ownership.

```python
# 模块级对象：注册当前 API 路由并加载轻量级共享依赖。
# 这里不保存请求级状态；每次请求的业务上下文由 QueryServiceContext / QAService / pipeline 创建。
router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)
```

This is better than one comment per variable because it explains the ownership rule: module-level objects are shared, request-level state is not.
