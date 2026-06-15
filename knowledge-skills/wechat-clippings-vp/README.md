<h1 align="center">
  WeChat Clippings VP | 微信公众号文章剪藏技能
</h1>

<p align="center">
  从公众号名、文章链接、标题或截图 OCR 定位文章，通过 TikHub 获取正文，输出 Obsidian 友好的 Markdown 剪藏
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/wechat--clippings--vp-notes-green" alt="wechat clippings vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
公众号线索  ->  TikHub 公众号定位  ->  历史文章匹配  ->  HTML 正文抓取  ->  Markdown 清洗剪藏
```

---

## 为什么要做 WeChat Clippings?

微信公众号文章适合做知识沉淀，但直接复制经常会带出页面尾巴、二维码引流、空列表项、错乱粗体、裸 URL、图片间距和标题空行等噪声。截图里只看到文章标题时，手动逐篇找原文也很费时间

WeChat Clippings 解决的是“把指定公众号文章稳定转成可读、可归档 Markdown”的问题。它不是浏览器抓取，也不是微信官方 API，而是让 Agent 按固定流程完成公众号定位、文章列表匹配、详情正文获取、结构清洗和文件输出

核心策略是 **direct URL first, account-list fallback, HTML-final**：

- 用户能提供 `mp.weixin.qq.com` 原文链接时，直接走详情接口，最省 TikHub 调用
- 没有链接时，先定位公众号，优先使用 `jumpInfo.userName` 里的 `gh_...` 作为文章列表 `ghid`
- 截图/OCR 标题批量任务优先走公众号历史文章列表匹配，不优先打长标题搜索
- 正文默认使用 TikHub HTML 详情接口，因为真实测试中 JSON 详情对有效文章 URL 返回 400，而 HTML 返回完整内容

## 工作原理

1. **输入识别**：接受公众号名、作者名、文章标题、`mp.weixin.qq.com` URL、截图 OCR 文本或复制的页面文字

2. **成本控制**：优先使用直接文章链接。调用成本从低到高大致是：

   - 原文链接：每篇通常 1 次 HTML 详情调用
   - 已知 `gh_...` + 标题：文章列表分页 + 详情调用
   - 公众号名 + OCR 标题：公众号搜索 + 文章列表分页 + 详情调用
   - 只有作者/主题大概线索：匹配不确定，调用次数最高

3. **公众号定位**：调用 TikHub `fetch_search_official_account`，从结果中优先读取 `jumpInfo.userName`，例如 `gh_2ab5c3151636`

4. **文章列表匹配**：调用 `fetch_mp_article_list`，用 `data.offset.Offset` 翻页，直到找到目标标题或 `data.offset.IsEnd == 1`

5. **正文获取**：对命中的文章 URL 调用 `fetch_mp_article_detail_html`，必要时再尝试 JSON 详情接口

6. **Markdown 清洗**：提取 `#js_content` 正文并清理格式噪声

   - 去除 `继续滑动看下一个`、`微信扫一扫`、`允许`、`取消`、`知道了`
   - 去除尾部二维码/私域引流块，例如 `欢迎关注`、`加我微信`、`交个朋友`
   - 去除独立署名行，例如 `/ 作者：xxx`
   - 去除空列表项，例如单独的 `-`
   - 合并 `xxx地址: https://...` 为 `[xxx地址](https://...)`
   - 修正 `** 关键词 **` 为 `**关键词**`
   - 压紧内部标题、图片、代码块和公式块周围的多余空行

7. **输出分包**：按 `--ranges` 生成一个或多个 Markdown 文件，例如 `1-4,5-8`

## 快速上手

### 1. 环境变量

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key_without_API_prefix>", "User")
```

`TIKHUB_API_KEY` 如果带有 `API:` 前缀，脚本会自动剥离此前缀

### 2. 已知文章链接剪藏

```powershell
python .\scripts\clip_wechat_tikhub.py "https://mp.weixin.qq.com/s/xxxx" --count 1 --ranges "1"
```

这是最省调用次数的方式。多篇文章可以重复传 `--article-url`，或把多个链接放在输入文本里

### 3. 公众号名 + 截图标题剪藏

先把截图 OCR 或可见标题保存为 UTF-8 文本文件，每行一个标题，再运行：

```powershell
python .\scripts\clip_wechat_tikhub.py "公众号名" --author "公众号名" --title-source "<ocr-title-file>" --count 4 --ranges "1-4"
```

### 4. 已知 `gh_...` 账号 ID

```powershell
python .\scripts\clip_wechat_tikhub.py "公众号名 文章主题" --account-id "gh_xxxxxxxxxxxx" --count 4 --ranges "1-4"
```

## 输出格式

Default final output directory for this local LLM_wiki vault is `E:\LLM_wiki\LLM_wiki\01.raw\01.Inbox`. Generated WeChat clipping Markdown belongs in `01.raw/01.Inbox` as unprocessed source material; classify/compile it into 02.wiki later. Use `--output-dir` to override the destination for a specific run.


默认文件名模板：

```text
微信_{author}_{summary}_公众号文章剪藏_{date}_{range}.md
```

可通过 `--filename-template` 自定义，例如：

```text
微信_{author}_{summary}_{date}_{range}.md
```

Markdown frontmatter 示例：

```yaml
---
title: "微信_AI编程实验室_大模型架构与注意力机制_公众号文章剪藏_2026-05-26_1-4"
source: "https://api.tikhub.io/api/v1/wechat_mp/web/fetch_mp_article_detail_html"
author:
  - "AI编程实验室"
published: "2026-01-13 - 2026-04-28"
created: 2026-05-26
description: "TikHub 命中的微信公众号文章候选，共 4 条，本文档收录 4 条"
tags:
  - "clippings"
  - "wechat"
  - "AI编程实验室"
---
```

正文从每篇文章标题开始：

```markdown
## 0x01. 文章标题

> 发布日期：2026-05-26
> 原文链接：[文章标题](https://mp.weixin.qq.com/...)

正文

### 1. 小节标题
正文
```

## 目录结构

```text
wechat-clippings-vp/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── wechat-tikhub-notes.md
└── scripts/
    └── clip_wechat_tikhub.py
```

## 注意事项

- TikHub 请求可能计费，能提供原文链接时优先提供链接
- 不使用浏览器抓取、cookie 登录、验证码绕过或微信登录态作为默认方案
- 不绕过付费墙、登录墙、删除状态或访问控制
- 生成的 Markdown 统一使用 UTF-8
- Default final output directory is `E:\LLM_wiki\LLM_wiki\01.raw\01.Inbox`; use `--output-dir` for custom destinations.
- 缓存会保存原始 TikHub 响应，公开同步或提交前应确认缓存目录不会被包含
- 当终端或 PowerShell 出现中文被替换成 `?` 时，优先使用 UTF-8 文件输入，避免命令行编码污染
