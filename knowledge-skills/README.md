<h1 align="center">
  Knowledge Skills | 知识沉淀技能
</h1>

<p align="center">
  Reusable agent skills for learning, research, notes, clipping, OCR, and writing workflows
  <br>
  用于学习、研究、笔记整理、剪藏、图片 OCR 与写作流程的 Agent / Codex Skills
</p>

<p align="center">
  简体中文 | English later
</p>

```text
raw input  ->  structured thinking  ->  reusable skill  ->  durable knowledge workflow
```

---

## 简介

`knowledge-skills/` 用来存放知识工作相关的 Agent 技能，覆盖学习、研究、阅读、笔记整理、概念解释、剪藏、图片 OCR 和写作流程。

## 核心结构

```text
knowledge-skills/
├── ai-learning-mentor-vp/   # AI 学习导师
├── daily-notes-vp/          # 原始学习日记
├── gif-showcase-maker-vp/   # GIF 展示图生成
├── github-clippings-vp/     # GitHub 材料剪藏
├── image-to-markdown-vp/    # 图片/截图 OCR 为 Markdown
├── paper-fetcher-vp/        # 论文识别与下载
├── wechat-clippings-vp/     # 微信公众号剪藏
├── zhihu-clippings-vp/      # 知乎剪藏
└── README.md                # 知识类技能目录说明
```

## 已有技能

- [`ai-learning-mentor-vp`](ai-learning-mentor-vp/)：面向计算机、AI、LLM 与 Agent 学习场景，提供概念讲解、费曼反馈、类比 diff、刻意练习、知识图谱和学习压缩流程。
- [`daily-notes-vp`](daily-notes-vp/)：记录个人日常学习原始材料。
- [`gif-showcase-maker-vp`](gif-showcase-maker-vp/)：把多张图片按顺序合成 GIF 展示图。
- [`github-clippings-vp`](github-clippings-vp/)：把 GitHub 仓库、PR、Issue、Discussion、Commit 等链接整理为结构化 Markdown 原始材料。
- [`image-to-markdown-vp`](image-to-markdown-vp/)：把截图或图片 OCR 成指定 Markdown 文件。
- [`paper-fetcher-vp`](paper-fetcher-vp/)：识别论文、下载并验证官方 PDF。
- [`wechat-clippings-vp`](wechat-clippings-vp/)：抓取微信公众号正文并生成 Markdown 剪藏。
- [`zhihu-clippings-vp`](zhihu-clippings-vp/)：抓取知乎文章或回答并生成 Markdown 剪藏。