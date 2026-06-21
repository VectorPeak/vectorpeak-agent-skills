# fill-contributions-graph

显式调用型 Codex Skill，用于为用户自己的 GitHub 仓库生成回顾式维护提交计划，并在用户确认后执行本地提交。

这个 skill 默认只做计划，不会自动 commit 或 push。执行前必须先生成 Excel 审核表，并由用户明确确认。

## 适用场景

- 为个人或组织名下的多个仓库规划回顾式维护提交。
- 按日期范围生成较自然的活跃日与提交数分布。
- 在已有真实提交的日期上做扣减，避免重复堆叠。
- 为测试性本地提交保留 manifest 和 rollback dry-run。

## 强制流程

1. 显式调用 `fill-contributions-graph`。
2. 输入 GitHub account、日期范围和可选 profile。
3. 运行 preflight，确认 `gh`、GitHub 登录和 API 连接正常。
4. 扫描账号仓库，要求 eligible repositories `> 10`。
5. 生成 Excel 审核表。
6. 用户审核 Excel，并明确确认。
7. 才允许进入 `local-commit`。
8. 本地提交完成后生成 manifest 和 rollback dry-run。
9. push 需要第二次明确确认。

任何 TSV、终端预览或聊天摘要都不能替代 Excel 确认。

## Excel 审核表

默认输出每日聚合视图：

```text
日期 | 目标提交数 | 已有作者提交数 | 本次计划新增数 | commit细则
```

其中：

- `目标提交数` 来自 activity profile。
- `已有作者提交数` 通过 GitHub commit search 查询。
- `本次计划新增数 = max(0, 目标提交数 - 已有作者提交数)`。
- `commit细则` 包含时间、仓库、commit message、计划文件路径。

示例：

```powershell
python scripts/generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --profile vibe_coding_builder `
  --excel-out plan.xls
```

如果下游执行器需要逐条 commit 明细：

```powershell
python scripts/generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --granularity commit `
  --excel-out commit-detail.xls `
  --out commit-detail.tsv
```

## Activity Profiles

当前只保留两个 profile：

- `vibe_coding_builder`：默认，更贴近 AI 辅助高频迭代。
- `active_personal_builder`：更保守的个人项目维护节奏。

详细分布见 `references/activity-profiles.md`。

## 工作区策略

执行 `local-commit` 前必须选择本地 worktree：

- 优先使用 remote URL 匹配且 `git status --porcelain` 干净的现有仓库。
- 如果本地仓库是 dirty，必须停止并让用户选择处理方式。
- 如果同一仓库存在多个 clone，必须展示候选路径后再选择。
- 测试执行或需要强 rollback 时，推荐使用隔离 clone。

这条规则来自实际执行经验：直接在已有工作区提交虽然更快，但容易把用户原本未提交的改动混进本次批处理。隔离 clone 更慢，但 manifest、rollback 和审计都更干净。

## Rollback

`local-commit` 测试完成后，默认准备 rollback：

- manifest 记录每个仓库的 pre-session HEAD、commit SHA、路径、分支、作者日期和 message。
- rollback dry-run 先展示将回到哪个 HEAD。
- 未 push 的测试提交优先用 `git reset --hard <pre-session-head>` 回滚。
- 已 push 的提交默认用 `git revert`，不默认改写远端历史。

rollback 只能作用于 manifest 中记录的 skill-created commits，不能回滚用户其他提交。

## 安全边界

- 不创建空 commit。
- 不写临时占位代码。
- 不生成提交后再删除的假内容。
- 不自动 push。
- 不在脏工作区里混入提交。
- 不在未确认 Excel 的情况下执行 local commit。
