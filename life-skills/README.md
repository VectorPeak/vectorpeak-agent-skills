<h1 align="center">
  Life Skills | 生活事务技能
</h1>

<p align="center">
  Reusable agent skills for life admin, planning, decisions, routines, and personal operations
  <br>
  用于生活事务、计划拆解、日常决策、习惯流程与个人事务管理的 Agent / Codex Skills
</p>

<p align="center">
  <a href="../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/category-life--skills-teal" alt="life skills"></a>
  <a href="../dev-skills/"><img src="https://img.shields.io/badge/dev--skills-engineering-brightgreen" alt="dev skills"></a>
  <a href="../knowledge-skills/"><img src="https://img.shields.io/badge/knowledge--skills-learning-purple" alt="knowledge skills"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

<p align="center">
  简体中文 | English later
</p>

```text
life event  ->  clarify constraints  ->  actionable plan  ->  tracked next steps
```

---

## 简介

`life-skills/` 用来存放生活事务相关的 Agent 技能，覆盖日程规划、个人事务、消费决策、旅行准备、健康预约、订阅管理、家庭维护和日常复盘

这里的 skill 不是普通待办清单，而是把生活问题拆成可执行流程：输入是什么、限制条件是什么、下一步做什么、哪些信息需要确认、哪些风险不能漏掉

## 为什么存在

生活事务经常不是难在单个动作，而是难在信息分散、步骤琐碎、时间节点多、责任边界不清。比如体检、证件、维修、旅行、搬家、订阅续费、购物决策和家庭事项，都容易因为没有流程而拖延或遗漏

这个目录的目标是把生活经验沉淀成可复用 skill，让 Agent 帮助整理事项、拆解步骤、识别风险，并输出可以直接执行的行动清单

## 核心结构

```text
life-skills/
└── README.md            # 生活类技能目录说明
```

## 适合沉淀的技能

- 生活事项拆解与计划
- 每周生活复盘
- 旅行准备清单
- 大件购买决策
- 就医预约准备
- 订阅与账单审计
- 家庭维修与保养计划
- 习惯流程和日常例行事项

## 编写原则

每个生活类 skill 都应该把模糊需求转成明确行动。它不只回答“建议怎么做”，还要说明“今天能做什么、需要准备什么、什么时候必须完成、哪些地方需要用户确认”

一个生活类 skill 至少应该回答：

- 这个 skill 处理哪类生活事务
- 用户需要提供哪些背景和限制
- Agent 应该如何拆解步骤和优先级
- 哪些信息需要确认后才能继续
- 哪些时间点、费用、风险或材料不能漏掉
- 最终输出的行动清单应该长什么样
