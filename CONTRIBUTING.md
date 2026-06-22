# Skill Intake Rules | Skill 入库规则

本仓库收录可复用的 Agent / Codex skills。新增或更新 skill 时，默认按下面流程执行。

## 必需输入

新增 skill 入库前，至少需要明确：

- skill 名称：使用小写连字符，例如 `review-pr-comments-vp`
- 所属分类：`dev-skills`、`knowledge-skills` 或 `job-skills`
- 触发场景：用户说什么时应该使用这个 skill
- 输入要求：执行 skill 需要哪些链接、文件、路径、账号或上下文
- 输出结果：最终应该生成什么文件、说明、PR、报告或本地变更
- 验证方式：如何确认结果可靠
- 同步目标：默认同步到 `VectorPeak/vectorpeak-agent-skills`

## 入库流程

1. 创建或更新 skill 目录。
2. 编写 `SKILL.md`，并保持 frontmatter 只有 `name` 和 `description`。
3. 参考仓库内已有 skill 的 README 风格，为该 skill 生成 `README.md`。
4. 如有 UI 元数据，添加或更新 `agents/openai.yaml`。
5. 运行 skill 校验脚本，至少确认 `SKILL.md` 可被 Codex 识别。
6. 启动多 agent 审查，要求不同审查视角至少覆盖：
   - 触发条件是否清楚
   - 输入和输出是否明确
   - 工作流是否可执行
   - 安全边界是否足够
   - README 是否能帮助人类快速理解
7. 根据审查意见修改。
8. 本地更新完成后，同步到远端仓库：
   - 从 `main` 创建 `codex/<change-name>` 分支
   - 只 stage 当前 skill 和必要仓库规范文件
   - commit
   - push 到 `VectorPeak/vectorpeak-agent-skills`
   - 打开 draft PR 或更新已有 PR

## 本地更新同步规则

当用户明确要求“更新 skill”“入库”“同步到远端”“上传到 GitHub”或类似表达时，Agent 应自动执行远端同步流程。

默认同步目标：

```text
https://github.com/VectorPeak/vectorpeak-agent-skills
```

同步时不要默认提交无关文件。如果工作区存在不属于本次 skill 更新的改动，必须先说明并只 stage 本次范围内的文件。

## README 要求

每个正式入库的 skill 必须有自己的 `README.md`。README 应参考已有 skill 的风格，至少包含：

- skill 名称和一句话说明
- 适用场景
- 不适用场景或边界
- 工作流程
- 目录结构
- 验证方式

可从 `templates/skill/README.md` 复制起步，然后按具体 skill 改写。

## 多 Agent 审查记录

PR 描述中需要简要记录多 agent 审查结论。推荐格式：

```markdown
## Multi-Agent Review

- Reviewer A - workflow clarity: pass / issues
- Reviewer B - safety and scope: pass / issues
- Reviewer C - README and usability: pass / issues
```

如果当前环境不能启动 sub-agent，PR 中必须显式说明原因，并把多 agent 审查列为合并前待办。

仓库的 GitHub Actions 会检查 PR 描述是否包含 `Multi-Agent Review` 记录。如果缺少 Reviewer A/B/C 的记录，检查会失败，用来提醒 Agent 不要忘记审查记录。
