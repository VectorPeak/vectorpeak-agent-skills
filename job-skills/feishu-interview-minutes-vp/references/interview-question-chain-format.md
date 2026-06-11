# Interview Question Chain Format

## Goal

Output a Chinese Markdown report that restores the interviewer's question structure. Focus on:

- 主问题
- 追问
- 质疑
- 反问
- 边界确认
- 场景假设
- 压力测试式追问
- 面试辅导中明确建议候选人准备的追问方向

Do not focus on summarizing the candidate's answers.

## Title

Use:

```markdown
# 日期：公司/岗位/主题
```

If the real company is unknown, use `面试`.

## Section Structure

Use Chinese numbered second-level headings:

```markdown
## 一、自我介绍与岗位匹配度
1. **主问题：** ...
   - **追问1：** ...
   - **追问2：** ...

## 二、项目真实性与业务背景
1. **主问题：** ...
   - **追问1：** ...
```

If one theme contains multiple independent main questions, continue numbering:

```markdown
2. **主问题：** ...
   - **追问1：** ...
```

## Extraction Rules

- Preserve the interviewer's tone when it is a challenge or doubt.
- Clean oral filler while keeping meaning.
- Keep consecutive follow-ups under the same main question.
- Do not turn candidate answers into questions unless the interviewer uses them as a follow-up.
- Do not invent live interview questions from pure evaluation comments.
- Coaching directions may be included only when they clearly imply future interview questions, for example "面试官可能会追问指标来源".

## Common Themes

Use themes like:

- 个人背景与转型动机
- 自我介绍与岗位匹配度
- 项目真实性与业务背景
- 项目指标与业务价值
- 技术知识点深挖
- 工程落地与部署边界
- 薪资期望与稳定性
- 反问环节与沟通方式
- 简历真实性与表达一致性

## Completeness Note

If transcript access is partial or source completeness is uncertain, add a short section near the top:

```markdown
> 来源完整性：文字记录 Docx 无权限；本报告基于妙记原生逐字稿生成，录音时长约 23 分钟，逐字稿时间戳覆盖 00:00-22:58。
```
