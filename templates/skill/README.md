<h1 align="center">
  Skill Name | 中文名称
</h1>

<p align="center">
  一句话说明这个 skill 解决什么问题
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-skill--category-lightgrey" alt="skill category"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
input  ->  workflow  ->  validation  ->  reusable output
```

---

## 为什么要做这个 skill?

说明这个 skill 沉淀了哪类重复任务，以及为什么值得入库。

## 适用场景

典型触发语：

```text
用 xxx skill 处理
把这个流程沉淀成 skill
更新这个 skill
```

适合处理：

- 场景 1
- 场景 2
- 场景 3

不适合处理：

- 边界 1
- 边界 2

## 工作流程

1. 收集输入和上下文。
2. 读取必要文件或外部资料。
3. 执行核心工作流。
4. 生成输出。
5. 验证结果。
6. 如用户要求入库或同步，推送到 `VectorPeak/vectorpeak-agent-skills`。

## 目录结构

```text
skill-name/
├── SKILL.md
├── README.md
└── agents/
    └── openai.yaml
```

## 验证方式

使用该 skill 后，至少检查：

- 触发条件是否清楚
- 输入和输出是否明确
- 工作流是否可执行
- 安全边界是否写明
- 是否已通过多 agent 审查
- 本地更新是否已按需同步到远端仓库

