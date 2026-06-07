<h1 align="center">
  Learning Repo Log VP | 仓库学习复盘记录技能
</h1>

<p align="center">
  把项目开发过程中的技术栈、名词概念、架构决策、工程经验和待复习问题，沉淀到当前仓库的学习复盘 Markdown 文档中
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/learning--repo--log--vp-notes-green" alt="learning repo log vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
临时提醒  ->  项目上下文判断  ->  分类整理  ->  结构化条目  ->  仓库学习复盘文档
```

---

## 为什么要做 Learning Repo Log?

项目开发时，真正容易丢失的不是代码，而是“当时为什么这样理解、为什么这样选型、哪里容易混淆、以后还要复习什么”。

Learning Repo Log 解决的是“把开发过程中的零散学习点沉淀成项目级复盘文档”的问题。当用户说“记一下”“记录到复盘”“这个概念以后要复习”时，Agent 不应该只在对话里解释一遍，而应该把精炼后的内容写入当前仓库的长期学习记录。

核心策略是 **project-scoped, lightweight, reviewable**：

- 按当前仓库维护学习记录，而不是混进全局杂记
- 默认写入 `{{项目名}}_学习复盘_技术栈与概念记录.md`
- 记录技术栈、名词概念、架构决策、工程实践、业务概念和待复习问题
- 保持项目上下文，不写成泛百科
- 不做面试包装、不写简历话术、不生成项目宣传稿

## 适用场景

典型触发语：

```text
记一下 MCP Tool Schema
把 RRF 记录到复盘里
这个概念以后我要复习
把这个技术栈保存一下
记录到当前项目的学习文档
帮我把这次踩坑沉淀下来
```

适合记录：

- 技术栈和框架
- 算法、协议、指标和模型
- RAG、Agent、MCP、数据库、前端、后端、部署和评估概念
- 项目里的业务术语
- 架构决策和选型理由
- 调试经验和工程实践
- 用户纠正过的项目偏好
- 后续需要复习的问题

不适合记录：

- API Key、Token、密码和隐私信息
- 大段源码复制
- 和当前项目无关的泛百科解释
- 面试包装和简历话术
- 没有证据的夸大结论

## 默认文件名

默认在当前仓库根目录写入：

```text
{{项目名}}_学习复盘_技术栈与概念记录.md
```

例如：

```text
MineTrain-Agent_学习复盘_技术栈与概念记录.md
```

项目名优先从用户明确输入获取，其次使用仓库目录名，再参考 `AGENTS.md` 或 `README.md` 的项目标题。

## 工作流程

1. **识别学习点**：从用户请求中提取要记录的技术点、概念、决策或复习问题
2. **判断项目上下文**：必要时轻量读取 `AGENTS.md`、`README.md`、`docs/` 或相关源码
3. **确定记录分类**：技术栈、名词概念、架构决策、工程实践、业务概念、易混淆点或待复习问题
4. **查重与更新**：如果已有同名条目，就追加“补充”；否则创建新日期条目
5. **写入 Markdown**：使用结构化模板追加到学习复盘文档
6. **返回结果**：告诉用户记录了什么，以及写入了哪个文件

## 条目结构

常规条目：

```markdown
## YYYY-MM-DD：概念名称

### 一句话理解

用自己的话解释这个概念是什么。

### 在 {{project_name}} 中怎么用

说明它在当前项目中对应哪个模块、流程、文件、配置或设计决策。

### 为什么值得记录

说明它解决了什么问题，为什么容易混淆，或者为什么后续开发会再次遇到。

### 易混淆点

列出相近概念、常见误解、边界条件或使用陷阱。

### 后续复习问题

- 问题一
- 问题二
```

小条目可以使用紧凑格式：

```markdown
## YYYY-MM-DD：概念名称

- **一句话理解：** ...
- **项目关联：** ...
- **后续复习：** ...
```

## Skill 文件结构

```text
learning-repo-log-vp/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── category-guide.md
    └── entry-template.md
```

其中：

- `SKILL.md`：定义触发场景、默认文件名、工作流和输出规则
- `references/category-guide.md`：记录分类和新建日志时的默认结构
- `references/entry-template.md`：常规条目、紧凑条目和补充条目的模板

## 与其他 Skill 的关系

- 如果用户需要先理解概念，可以先使用 `project-concept-explainer-vp` 解释，再把精炼结论记录下来
- 如果用户在读论文、剪藏文章或生成素材后想保存收获，可以只记录最终学习点，而不是复制完整材料
- 如果用户明确要写面试文档、简历项目或项目包装，不使用本 Skill

