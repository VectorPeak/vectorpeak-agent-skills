<h1 align="center">
  Feishu Interview Minutes VP | 飞书面试纪要整理技能
</h1>

<p align="center">
  从飞书妙记、智能纪要 Docx、文字记录或中文面试转写中提取面试问题链条，并输出结构化 Markdown
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-job--skills-teal" alt="job skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/feishu--interview--minutes--vp-interview-orange" alt="feishu interview minutes vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
Feishu Docx / Minutes  ->  source routing  ->  transcript extraction  ->  question-chain report
```

---

## 为什么要做 Feishu Interview Minutes?

面试录音、模拟面试、面试辅导和复盘材料经常沉在飞书妙记或智能纪要里。直接看智能纪要容易混在“回答总结、待办、金句、章节摘要”里，后续复盘时很难快速看到面试官真正考察的问题链条。

Feishu Interview Minutes 解决的是“从飞书会议材料中还原面试问题结构”这一步。它不是简单总结会议，而是让 Agent 按固定顺序读取飞书材料，优先找原始文字记录和妙记逐字稿，再从中提取主问题、追问、质疑、边界确认和压力测试问题。

核心策略是 **related links first, transcript before summary, permission-aware fallback**：

- 智能纪要 Docx 末尾如果有“相关链接”，优先解析 `妙记` 和 `文字记录`
- 能读 `文字记录` Docx 时优先用它作为 transcript
- `文字记录` 无权限时，回落到妙记原生 transcript export 或 `vc +notes` 产物
- `missing_scope` 才补授权；`permission_denied` 要找文档或妙记 owner 授权
- 最终 Markdown 聚焦问题链条，不保留原始逐字稿全文

## 工作原理

1. **输入识别**：判断用户给的是 `/docx/` 智能纪要、`/wiki/` 文档、`/minutes/` 妙记、转写文件，还是粘贴文本。

2. **授权检查**：先运行 `lark-cli auth status --verify`。只有 user token 缺失、过期或出现明确 `missing_scope` 时才发起授权。

3. **智能纪要读取**：Docx/Wiki 先用 `docs +fetch --api-version v2` 读取 Markdown 内容。

4. **相关链接解析**：使用 `scripts/extract_feishu_links.py` 从正文末尾提取 `妙记`、`文字记录` 和其他 Feishu 链接。

5. **原始内容读取**：优先级为：

   - `文字记录` Docx
   - 妙记原生逐字稿导出
   - `vc +notes` 写出的 transcript
   - 智能纪要正文
   - 粘贴文本

6. **完整性检查**：比较录音时长、字符数、时间戳跨度、说话轮数和大段空白。如果 20 分钟以上录音只有几百字 transcript，应标记为不完整。

7. **问题链条提取**：按考察主题组织主问题和追问，不把候选人回答或纯评价伪造成问题。

8. **报告校验**：用 `scripts/validate_interview_report.py` 检查 frontmatter、标题结构、主问题格式和乱码风险。

## 快速上手

### 1. 安装与初始化 lark-cli

```powershell
npx @larksuite/cli@latest install
lark-cli config init --new --lang zh
lark-cli doctor
```

推荐创建一个专门用于 CLI/Codex 的企业自建应用，例如：

```text
Codex Feishu Minutes Assistant
```

### 2. 首次授权

按当前任务请求最小权限。例如只处理智能纪要 Docx：

```powershell
lark-cli auth login --scope "docx:document:readonly" --no-wait --json
```

处理妙记逐字稿：

```powershell
lark-cli auth login --scope "minutes:minutes.transcript:export vc:note:read minutes:minutes:readonly minutes:minutes.artifacts:read" --no-wait --json
```

授权会持久化到本机凭据存储。日常使用先检查：

```powershell
lark-cli auth status --verify
```

### 3. 读取智能纪要

```powershell
lark-cli docs +fetch --api-version v2 --doc "<docx_url>" --as user --doc-format markdown --json
```

将返回的 Markdown 保存或传给链接解析脚本：

```powershell
python .\scripts\extract_feishu_links.py --input ".\note.md" --json
```

### 4. 读取妙记逐字稿

```powershell
'{"need_speaker":true,"need_timestamp":true,"file_format":"txt"}' |
  lark-cli api GET /open-apis/minutes/v1/minutes/<minute_token>/transcript --as user --params - --output "minutes\<minute_token>\native_transcript.txt" --json
```

如果原生导出不可用，可回落到：

```powershell
lark-cli vc +notes --minute-tokens <minute_token> --as user --overwrite --json
```

### 5. 生成分析 Prompt

```powershell
python .\scripts\build_interview_prompt.py `
  --transcript ".\minutes\<minute_token>\native_transcript.txt" `
  --source "<original_feishu_url>" `
  --title "<feishu_title>" `
  --candidate "<candidate>" `
  --date "YYYY-MM-DD" `
  --company "面试" `
  --position "<position>" `
  --output ".\prompt.md"
```

然后让 Agent 根据 `prompt.md` 输出最终问题链条 Markdown。

## 输出格式

默认文件名：

```text
姓名_日期_公司_岗位.md
```

Frontmatter 示例：

```yaml
---
source: "https://example.feishu.cn/docx/..."
source_type: "feishu-docx-ai-minutes"
date: "2026-06-06"
event_time: "2026-06-06 14:11-14:34 GMT+08"
company: "面试"
position: "互联网开发岗位"
candidate: "候选人"
duration: "00:23:00"
feishu_title: "智能纪要：互联网开发岗位面试指导—候选人 2026年6月6日"
related_minutes: "https://example.feishu.cn/minutes/..."
related_transcript_doc: "https://example.feishu.cn/docx/..."
source_priority: "优先读取文字记录 Docx；其次读取妙记原生逐字稿；最后使用智能纪要正文。"
related_source_status: "文字记录无权限；已使用妙记原生逐字稿。"
tags:
  - interview
  - feishu
  - question-chain
type: "interview-question-chain"
---
```

正文示例：

```markdown
# 2026-06-06：面试/互联网开发岗位/面试指导问题链条

## 一、自我介绍与岗位匹配度
1. **主问题：** 你先做一下自我介绍，重点讲一下和当前岗位相关的经历？
   - **追问1：** 你最近的大模型/AI 相关工作做了多久，具体负责哪些内容？
   - **追问2：** 早期前端开发经历和现在应聘的岗位有什么关系？
```

## 目录结构

Agent 入口优先读取 `SKILL.md`；遇到权限、命令细节或输出格式细节时，再按需读取 `references/`。`scripts/` 是可执行工具，用于链接提取、prompt 构建和结果校验。

```text
feishu-interview-minutes-vp/
├── SKILL.md                         # Agent 执行入口：触发条件、来源路由、授权规则、输出约束
├── README.md                        # GitHub 展示文档：能力说明、快速上手、输出格式和目录说明
├── agents/
│   └── openai.yaml                  # Agent UI 元信息：展示名称、短描述和默认提示词
├── references/
│   ├── lark-cli-minutes-notes.md    # lark-cli 读取 Docx/妙记/逐字稿的命令、权限和失败处理
│   └── interview-question-chain-format.md # 面试问题链条 Markdown 的标题、主题、主问题和追问规范
└── scripts/
    ├── extract_feishu_links.py      # 从智能纪要 Markdown 的“相关链接”中提取妙记和文字记录链接
    ├── build_interview_prompt.py    # 将逐字稿和元信息组装成稳定的问题链条分析 prompt
    └── validate_interview_report.py # 校验最终 Markdown 的 frontmatter、标题、主问题/追问和乱码风险
```

## 注意事项

- 授权链接有时效；发出一次链接后，应等待用户完成授权，不要反复生成新链接。
- `missing_scope` 才是补授权信号；`permission_denied` 通常是文档/妙记 owner 没给当前用户访问权限。
- 智能纪要末尾的“相关链接”经常包含真正的 `妙记` 和 `文字记录`，必须优先解析。
- `lark-cli api ... --output` 要求输出路径是当前目录下的相对路径。
- PowerShell 可能把 UTF-8 中文显示成乱码；判断文件内容时使用显式 UTF-8 方式读取或显示。
- 不要把真实 Feishu token、内部链接、本地绝对路径或原始逐字稿提交到公开仓库。
- 不要把纯评价句改写成真实面试问题；只能提取有依据的问题、追问或复盘中明确建议的追问方向。
