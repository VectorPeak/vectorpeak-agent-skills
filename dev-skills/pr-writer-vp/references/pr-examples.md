# PR 案例参考

这些案例用于参考小型 bug-fix PR 的写法：正文要简洁，证据要具体，影响范围要说清楚。

## 案例

- `langgenius/dify#37799`：`fix(web): prevent ssePost error handler from throwing`
- `AstrBotDevs/AstrBot#8968`：`fix: prevent path traversal vulnerability in plugin upload filenames`

## 共性结构

```markdown
<一句话摘要>

## What Problem This Solves

<说明具体 bug，不要只说“修复问题”。>
<指出出错函数、路径、接口或入口。>
<解释为什么这会影响用户、开发者、安全性或可诊断性。>

## Change

<用 1-3 条说明实际改了什么。>
<强调改动范围很窄：只影响某个 fallback path、文件名解析、边界 case 等。>

## Evidence

<重现此错误的步骤。>
<预期行为。>
<实际行为或失败输出。>
<后端问题尽量提供日志；docker-compose logs 尤其有价值。>
<适用时提供截图或视频。>
<尽量提供 before / after。>
<安全、路径或错误处理类问题要给出 payload 或 exception。>

## Possible call chain / impact

<从用户入口或模块入口追踪到受影响函数。>
<说明哪些路径受影响，哪些路径不受影响。>

## Testing

- `<定向验证命令>`
- `<lint/type/compile 命令>`
- `<unit 或 focused test 命令>`
```

## 共同特征

- 标题直接点出 bug 和受影响区域。
- 标题清晰、有描述性，维护者一眼能看出行为变化。
- 第一部分先解释行为问题，再解释代码改动。
- Evidence 包含复现步骤、预期行为、实际行为和具体失败输出。
- 后端问题尽量包含日志；`docker-compose logs` 尤其有价值。
- 截图或视频只在能帮助说明问题时提供。
- 调用链部分帮助维护者理解 bug 如何被触发。
- 影响范围部分同时说明哪些路径不受影响。
- Testing 使用聚焦命令，避免只写笼统的 “tested locally”。

## 写作原则

小 PR 要让维护者相信三件事：bug 真实、改动很窄、验证可复现。
