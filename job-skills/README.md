<h1 align="center">
  Job Skills | 工作与职场技能
</h1>

<p align="center">
  Reusable agent skills for job search, contracts, interviews, offers, and workplace decisions
  <br>
  用于求职、合同审查、面试准备、Offer 对比与职场决策的 Agent / Codex Skills
</p>

<p align="center">
  <a href="../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/category-job--skills-teal" alt="job skills"></a>
  <a href="../dev-skills/"><img src="https://img.shields.io/badge/dev--skills-engineering-brightgreen" alt="dev skills"></a>
  <a href="../knowledge-skills/"><img src="https://img.shields.io/badge/knowledge--skills-learning-purple" alt="knowledge skills"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

<p align="center">
  简体中文 | English later
</p>

```text
job document  ->  extract terms  ->  compare risks  ->  action checklist
```

---

## 简介

`job-skills/` 用来存放工作与职场相关的 Agent 技能，覆盖合同审查、Offer 对比、简历优化、面试准备、薪资谈判、职场沟通和入职离职流程

这里的 skill 不是泛泛给建议，而是把职场材料拆成可核查的条款、风险、问题清单和下一步行动。比如 `job-contract-review-vp` 这种技能，应该帮助用户看清合同里的薪资、试用期、竞业限制、违约责任、保密条款和签署前需要确认的问题；`feishu-interview-minutes-vp` 则应该把飞书妙记、智能纪要和文字记录整理成可复盘的面试问题链条

## 为什么存在

工作相关决策通常信息密度高、后果也更重。合同、Offer、入职材料、绩效沟通和离职流程里，很多关键点藏在条款、时间节点、责任边界和默认假设里，单靠临场阅读很容易漏掉风险

这个目录的目标是把工作场景里的判断路径沉淀成可复用 skill，让 Agent 帮助提取关键信息、对比选项、标出风险，并输出可以直接执行的沟通或确认清单

## 核心结构

```text
job-skills/
├── job-contract-review-vp/ # 工作合同审查与风险提示
├── feishu-interview-minutes-vp/ # 飞书面试妙记与智能纪要问题链条整理
└── README.md            # 工作与职场类技能目录说明
```

## 已有技能

### [`job-contract-review-vp/`](job-contract-review-vp/)

用于工作合同、Offer、NDA、竞业限制、离职补偿等材料的结构化审查：提取关键条款，识别红旗风险、中等风险、有利保护和缺失保护，并输出可谈判的问题清单与 Markdown 报告

### [`feishu-interview-minutes-vp/`](feishu-interview-minutes-vp/)

用于把飞书妙记、智能纪要 Docx、文字记录或粘贴的中文面试转写整理成面试问题链条：优先读取文字记录，其次读取妙记原生逐字稿，最后才使用智能纪要正文，并输出 UTF-8 Markdown 复盘文件

## 适合沉淀的技能

- 合同审查与风险提示
- Offer 对比与决策
- 简历优化和岗位匹配
- 面试准备与复盘
- 薪资谈判准备
- 入职材料检查
- 离职交接清单
- 职场沟通草稿和冲突处理

## 编写原则

每个工作类 skill 都应该把模糊材料转成可检查的结构。它不只回答“这个看起来怎么样”，还要说明“哪些条款重要、风险在哪里、还要问什么、下一步怎么沟通”

一个工作类 skill 至少应该回答：

- 这个 skill 处理哪类工作材料或职场场景
- 用户需要提供哪些文本、截图或背景约束
- Agent 应该提取哪些关键字段和条款
- 哪些风险需要明确标注不确定性
- 哪些问题需要用户向 HR、法务、招聘方或上级确认
- 最终输出的行动清单、问题清单或对比表应该长什么样
