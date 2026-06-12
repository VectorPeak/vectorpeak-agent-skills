<h1 align="center">
  Tech Article Rewriter VP | 技术文章深度重写技能
</h1>

<p align="center">
  从 URL、截图、OCR 或现成语料出发，获取可信全文，重建文章逻辑，按 Markdown 模板生成可迭代的技术博客草稿
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/tech--article--rewriter--vp-writing-blue" alt="tech article rewriter vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
URL / 截图 / 语料  ->  全文采集与缓存  ->  要点抽取  ->  逻辑重建  ->  模板化 Markdown 初稿  ->  迭代润色
```

---

## 为什么要做 Tech Article Rewriter?

技术文章改写最容易失败的地方，不是“语言不够顺”，而是素材、逻辑和输出边界混在一起：一边要从知乎、微信或截图里拿到完整原文，一边要抽取事实、代码、工具和坑点，还要把多篇来源揉成一篇逻辑顺畅的博客。

Tech Article Rewriter 解决的是“把可信来源材料转成可发布技术博客”的问题。它不是逐段同义改写，也不是把几篇文章摘要拼起来，而是让 Agent 先拿到完整语料，再理解素材结构，最后重建一条适合读者阅读的技术主线。

核心策略是 **corpus-first, logic-first, template-final**：

- 先把 URL、截图、OCR 或 copied text 变成可信 `source-corpus-clean.md`
- 再抽取多篇来源中的事实、观点、代码、工具、失败模式和独特点
- 然后重建文章逻辑，不照搬单篇来源的顺序
- 最后按用户模板生成 Markdown，并保留参考资料

## 工作原理

1. **输入路由**：识别用户给的是现成语料、URL、截图、OCR、Markdown 模板，还是只是主题和风格要求。

2. **语料采集**：当输入不是 clean corpus 时，按照 `references/source-corpus-workflow.md` 定位原文、调用 TikHub 或平台相关流程获取全文，并把 raw JSON/HTML 写入 staging cache。

3. **缓存约定**：按 `references/cache-and-corpus.md` 保存：

   - `cache/`：原始 provider 响应、HTML、OCR、搜索 trace
   - `out/source-corpus-clean.md`：后续写作使用的干净语料
   - `out/source-corpus-raw.json`：可追溯 metadata 和原始 HTML/content
   - `notes/`：截图匹配、失败候选和人工判断记录

4. **素材理解**：抽取问题背景、关键概念、方案层级、示例代码、工具链、优缺点、失败模式和来源链接。

5. **逻辑重建**：把素材重新排列成读者理解路径，优先采用“问题 -> 失败原因 -> 方案分层 -> 示例 -> 工程 checklist -> 总结”的结构。

6. **模板生成**：读取用户给的 Markdown 模板；没有模板时使用默认 0x 大段式技术博客模板。

7. **迭代润色**：根据反馈调整标题专业度、正文口吻、篇幅、代码密度、树形图、表格、示例和参考资料。

## 快速上手

### 1. 已有 clean corpus

```text
主题：如何让大语言模型输出 JSON 格式？
语料：E:\Github\.codex-work\zhihu-json-output\out\source-corpus-clean.md
模板：使用默认 0x 大段式技术博客模板
目标：生成一篇专业标题、正文轻松、逻辑清晰的 Markdown 技术博客
```

### 2. 只有 URL 或截图

```text
主题：如何让大语言模型输出 JSON 格式？
素材：
- https://www.zhihu.com/question/656512469/answer/...
- 一张知乎回答截图
模板：默认模板
```

Agent 应先进入 source corpus workflow，定位完整原文并生成 `source-corpus-clean.md`，再开始写作。

### 3. 自定义模板

```markdown
# {{title}}

## 0x01. 结构化输出为什么是工程刚需

## 0x02. 一个 JSON 需求是怎么翻车的

## 0x03. Prompt 约束的边界在哪里

## 0x04. 从生成阶段约束格式：JSON Mode、Schema 与受限解码

## 0x05. 从接收阶段兜底：解析、校验、修复与重试

## 参考资料
```

模板里的说明性文字是约束，不应原样保留到最终文章里。

## 输出格式

默认先写入 staging：

```text
<workspace>/.codex-work/tech-article-rewriter/<slug>-<yyyymmdd-hhmmss>/out/
```

常见输出：

```text
article-draft.md
article-notes.md
source-corpus-clean.md
source-corpus-raw.json
```

当用户确认最终版本后，写入：

```text
E:\LLMWiki\LLMWiki\Clippings
```

`.codex-work` 只作为临时加工区，不作为最终文章的长期保存目录。

## 目录结构

```text
tech-article-rewriter-vp/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── cache-and-corpus.md
    ├── rewrite-rules.md
    ├── source-corpus-workflow.md
    └── template-contract.md
```

## 注意事项

- 不做逐段同义改写；默认做逻辑重建和原创表达。
- 第三方来源默认保留参考资料，不删除来源痕迹。
- 不从截图可见文字直接写最终文章；能抓全文时必须先抓全文。
- 不提交 TikHub raw cache、截图、API key、`.codex-work` 或生成的正式文章到公开仓库。
- 不虚构 benchmark、生产事故、API 行为或未在语料中出现的事实。
- 技术代码示例可以补充，但必须保持合理、可解释，并避免声称未经验证的 SDK 细节。
