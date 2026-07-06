<h1 align="center">
  Job Skills | 工作与职场技能
</h1>

<p align="center">
  Reusable agent skills for job search, contracts, interviews, offers, and workplace decisions
  <br>
  用于求职、合同审查、面试准备、Offer 对比与职场决策的 Agent / Codex Skills
</p>

<p align="center">
  简体中文 | English later
</p>

```text
job document  ->  extract terms  ->  compare risks  ->  action checklist
```

---

## 简介

`job-skills/` 用来存放工作与职场相关的 Agent 技能，覆盖合同审查、Offer 对比、面试复盘、贡献图计划、日报查询、职场沟通和入职离职流程。

## 核心结构

```text
job-skills/
├── contributions-graph-filler-vp/  # GitHub 贡献图补全计划
├── feishu-interview-minutes-vp/    # 飞书面试纪要整理
├── job-contract-review-vp/         # 工作合同审查
├── xiaohei-daily-query-vp/         # 小黑日报助手本地数据查询
└── README.md                       # 工作与职场类技能目录说明
```

## 已有技能

- [`contributions-graph-filler-vp`](contributions-graph-filler-vp/)：生成可审查的 GitHub 贡献图补全计划。
- [`feishu-interview-minutes-vp`](feishu-interview-minutes-vp/)：把飞书妙记、智能纪要和面试文字记录整理成可复盘的问题链条。
- [`job-contract-review-vp`](job-contract-review-vp/)：提取合同、Offer、NDA 等材料中的关键条款，识别风险并输出可谈判问题清单。
- [`xiaohei-daily-query-vp`](xiaohei-daily-query-vp/)：查询本地小黑日报助手服务，生成工作时间线、日报、热力图和应用使用统计。