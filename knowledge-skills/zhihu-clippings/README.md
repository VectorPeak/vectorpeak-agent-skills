<h1 align="center">
  Zhihu Clippings | 知乎文章剪藏技能
</h1>

<p align="center">
  从知乎作者、文章标题或文章 ID 定位内容，保留正文、公式、图片、表格和代码块，输出 Obsidian 友好的 Markdown 剪藏
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/zhihu--clippings-notes-green" alt="zhihu clippings"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
知乎线索  ->  官方 API 定位/验证  ->  TikHub 正文补全  ->  Markdown 结构清洗  ->  Obsidian 剪藏
```

---

## 为什么要做 Zhihu Clippings?

知乎长文常常包含正文、代码、公式、截图、表格和目录层级。直接复制容易丢公式、丢图片、标题层级混乱，浏览器剪藏又容易受登录、反爬和动态渲染影响

Zhihu Clippings 解决的是“把知乎文章稳定转成可沉淀 Markdown 笔记”的问题。它不是简单网页抓取，而是按固定流程完成官方定位、第三方正文补全、结构转换、格式清理和文件分包

核心策略是 **official-first, TikHub-final**：

- 先用知乎开放平台 API 做作者、标题、article_id 和 source 验证
- 最终正文大概率使用 TikHub API，因为官方 API 通常只返回搜索摘要或不完整正文
- 对长文、公式、图片、表格和代码块，不能停在官方 `ContentText` 摘要层

## 工作原理

1. **输入识别**：接受作者名、知乎 people URL、文章标题、文章 URL、article_id 或截图转写标题列表

2. **官方定位**：调用知乎开放平台 `zhihu_search`，确认作者、标题、文章 URL 和 article_id。官方接口主要用于定位和交叉验证

3. **正文补全**：使用 TikHub 的知乎接口获取完整正文

   - 作者近期文章列表：`fetch_user_articles`
   - 已知单篇长文：`fetch_column_article_detail`

4. **结构转换**：将 HTML 转为 Markdown，保留结构化内容

   - 公式：知乎 equation 图片转 `$...$` 或 `$$...$$`
   - 图片：普通图片转 `![alt](url)`
   - 表格：HTML table 转 Markdown table
   - 代码块：自动推断 `python`、`bash`、`json`
   - 链接：保留 Markdown 链接，压缩 `GitHub：` + 单独链接的空行

5. **标题层级清洗**：按文本模式修正标题层级

   - `## 0x01. 文章名`：每篇文章
   - `### 1. 核心章节`：大章节，中文序号需转为阿拉伯数字
   - `#### 1.1 小节`
   - `##### 方法一：实现方案`

6. **输出分包**：按 `--ranges` 生成一个或多个 Markdown 文件，例如 `1-4,5-8`

## 快速上手

### 1. 环境变量

```powershell
[Environment]::SetEnvironmentVariable("ZHIHU_ACCESS_SECRET", "<zhihu_access_secret>", "User")
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key_without_API_prefix>", "User")
```

`TIKHUB_API_KEY` 如果带有 `API:` 前缀，脚本会自动剥离此前缀

### 2. 按作者近期文章分包

```powershell
python .\scripts\clip_zhihu_official.py "https://www.zhihu.com/people/dan-mo-41-42 何宇峰" --author "何宇峰" --content-provider tikhub --user-url-token dan-mo-41-42 --count 10 --ranges "1-5,6-10"
```

### 3. 已知 article_id 的长文单篇剪藏

```powershell
python .\scripts\clip_zhihu_official.py "LLM & VLM & Agent 面试八股参考 若尘797" --author "若尘797" --article-id 2014503030167451362 --count 1 --ranges "1" --filename-template "知乎_{author}_LLM VLM Agent 面试八股参考_{date}.md"
```

### 4. 多篇已知 article_id 分包

```powershell
python .\scripts\clip_zhihu_official.py "卡卡带我飞 GPU 集群文章合集" --author "卡卡带我飞" --article-id 2028891401836929299 --article-id 2028883905680286035 --article-id 2028142360152817950 --article-id 2024359354514556166 --count 4 --ranges "1-4"
```

## 输出格式

默认输出目录是当前工作目录下的 `.\clippings`。如果需要写入 Obsidian vault，可以通过 `--output-dir` 指定目标目录


默认文件名模板：

```text
知乎_{author}_{summary}_知乎文章搜索剪藏_{date}_{range}.md
```

可通过 `--filename-template` 自定义，例如：

```text
知乎_{author}_GPU集群与私有化部署文章合集_{date}_{range}.md
```

Markdown frontmatter 示例：

```yaml
---
title: "知乎_作者_大模型Agent_知乎文章搜索剪藏_2026-05-26_1-4"
source: "zhihu official api + tikhub"
author:
  - "作者"
created: 2026-05-26
range: "1-4"
tags:
  - "clippings"
  - "zhihu"
  - "作者"
---
```

正文直接从文章标题开始：

```markdown
## 0x01. 文章标题
正文

### 1. 核心章节
正文

#### 1.1 小节
正文
```

## 可选 LLM 标题复核

复杂文章的 HTML 标题层级可能不可靠。可以开启：

```powershell
--llm-heading-review
```

这个模式只把标题列表发送给 OpenAI-compatible LLM，让模型返回 JSON 形式的层级修正表，不发送全文正文，也不允许模型改正文内容

## 目录结构

```text
zhihu-clippings/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── zhihu-notes.md
└── scripts/
    └── clip_zhihu_official.py
```

## 注意事项

- TikHub 请求可能计费，脚本会尽量使用本地缓存减少重复请求
- 官方 API 有频率限制，脚本默认加入查询间隔和重试
- 不使用浏览器抓取、cookie 登录或验证码绕过作为默认方案
- 生成的 Markdown 统一使用 UTF-8
- 默认输出目录是 `.\clippings`，公开仓库不写死个人 Obsidian 路径
- 当终端或 PowerShell 出现中文被替换成 `?` 时，优先使用 UTF-8 文件输入或 article_id，避免命令行编码污染
