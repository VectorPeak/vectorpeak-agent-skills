<h1 align="center">
  PR Writer VP | 开源 PR 工作流技能
</h1>

<p align="center">
  自动 fork 项目、寻找小型 bug-fix PR 候选、撰写证据驱动的 PR 草稿，并且只在明确确认后提交。
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-dev--skills-brightgreen" alt="dev skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/pr--writer--vp-github-black" alt="pr writer vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
项目名称 -> fork 并 clone -> 寻找小 bug -> 收集证据 -> 拟 PR 草稿 -> 确认后提交 draft PR
```

---

## 为什么需要 PR Writer?

小型开源 PR 最容易被维护者 review 的前提是：改动范围窄、问题可复现、正文符合目标项目的提交习惯。真正困难的地方不只是改代码，而是证明 bug 真实存在，准确说明影响范围，并且不夸大证据。

PR Writer VP 把这套流程沉淀成可复用的 agent 工作流。它会帮助 agent fork 和 clone 仓库，保持 fork 的 `main` 与 upstream 同步，创建修复分支，寻找小型 bug-fix 机会，收集复现证据，并拟出维护者容易判断的 PR 正文。

默认策略是保守的：先拟草稿，只有在用户明确确认后才提交。

## 工作流程

1. **拉取项目并配置环境**
   - 解析 upstream GitHub 仓库。
   - fork 到用户自己的 GitHub 账号。
   - clone 到 `E:\Github\<repo-name>`。
   - 添加 `upstream` remote。
   - 保持 fork 的 `main` 与 upstream `main` 同步。
   - 创建 `fix` 分支，或在命名冲突时创建不冲突的修复分支。

2. **寻找 PR 候选**
   - 可用时启动多 agent 审查。
   - 默认方向是寻找代码改动不超过 20 行的潜在 bug。
   - 优先寻找确定性边界问题，例如路径大小写、URL 编码、校验错误、空值处理、转义问题和小型边界条件错误。
   - 除非用户明确授权 agent 自行选择，否则先列出候选，再等用户选择。

3. **默认拟 PR 草稿**
   - 可用时必须使用多个 agent：
     - 一个 agent 阅读目标项目的贡献规范和 PR 提交规则；
     - 另一个 agent 核对实际 diff、证据和验证声明是否属实。
   - 先拟标题和正文，再提交。
   - 只有用户明确要求时才创建 draft PR。
   - 只有用户明确要求时才转为正式 ready for review。

## PR 正文模板

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

## 参考资料

技能内置 `references/pr-examples.md`，总结了两个小型 bug-fix PR 的共性结构：

- `langgenius/dify#37799`
- `AstrBotDevs/AstrBot#8968`

核心原则很简单：小 PR 要让维护者相信三件事，bug 真实、改动很窄、验证可复现。

## 目录结构

```text
pr-writer-vp/
|-- SKILL.md
|-- README.md
|-- agents/
|   `-- openai.yaml
`-- references/
    `-- pr-examples.md
```

## 注意事项

- dry-run 模式下不要打开或更新 PR。
- 只有 CLI、单元函数或已安装运行时代码复现时，不要声称完成了 UI 复现。
- 测试、截图或其他证据被删除后，PR 正文里也要同步删除对应声明。
- 保持改动聚焦，避免无关重构和生成文件噪音。
- 遵守目标仓库贡献规范，但不要默认添加单独的 checklist 章节，除非项目模板强制要求。
