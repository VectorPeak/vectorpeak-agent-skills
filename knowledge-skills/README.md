<h1 align="center">
  Knowledge Skills | 知识沉淀技能
</h1>

<p align="center">
  Reusable agent skills for learning, research, notes, and writing workflows
  <br>
  用于学习、研究、笔记整理与写作流程的 Agent / Codex Skills
</p>

<p align="center">
  <a href="../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="project-concept-explainer-vp/"><img src="https://img.shields.io/badge/project--concept--explainer--vp-study-blueviolet" alt="project concept explainer vp"></a>
  <a href="learning-repo-log-vp/"><img src="https://img.shields.io/badge/learning--repo--log--vp-notes-green" alt="learning repo log vp"></a>
  <a href="gif-showcase-maker-vp/"><img src="https://img.shields.io/badge/gif--showcase--maker--vp-media-orange" alt="gif showcase maker vp"></a>
  <a href="paper-fetcher-vp/"><img src="https://img.shields.io/badge/paper--fetcher--vp-research-orange" alt="paper fetcher vp"></a>
  <a href="zhihu-clippings-vp/"><img src="https://img.shields.io/badge/zhihu--clippings--vp-notes-green" alt="zhihu clippings vp"></a>
  <a href="wechat-clippings-vp/"><img src="https://img.shields.io/badge/wechat--clippings--vp-notes-green" alt="wechat clippings vp"></a>
  <a href="tech-article-rewriter-vp/"><img src="https://img.shields.io/badge/tech--article--rewriter--vp-writing-blue" alt="tech article rewriter vp"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

<p align="center">
  简体中文 | English later
</p>

```text
raw input  ->  structured thinking  ->  reusable skill  ->  durable knowledge workflow
```

---

## 简介

`knowledge-skills/` 用来存放知识工作相关的 Agent 技能，覆盖学习、研究、阅读、笔记整理、概念解释、知识地图抽取和写作流程

这里的重点不是保存一段好用的 prompt，而是保存可复用的思考结构：输入是什么、如何判断、如何组织材料、如何校验结果、最后输出成什么形态

## 为什么存在

知识工作最容易丢失的不是资料本身，而是处理资料时形成的判断路径：如何读一篇论文、如何解释一个概念、如何把零散笔记整理成结构、如何把文章变成可复用知识

这个目录的目标是把这些判断路径沉淀成可反复调用的 skill，让 Agent 在面对相似知识任务时有稳定流程，而不是每次重新临场发挥

## 核心结构

```text
knowledge-skills/
├── project-concept-explainer-vp/  # 项目伴读、概念讲解、知识地图与术语表生成
├── learning-repo-log-vp/          # 按仓库沉淀学习复盘、技术栈、概念、架构决策和待复习问题
├── gif-showcase-maker-vp/         # 多张图片按顺序生成轮播 GIF，支持停留帧和淡入转场
├── paper-fetcher-vp/       # 论文识别、官方 PDF 下载、重命名与 Zotero identifier 辅助
├── zhihu-clippings-vp/     # 知乎文章定位、正文补全、公式图片表格保留与 Obsidian Markdown 剪藏
├── wechat-clippings-vp/    # 微信公众号文章定位、TikHub 正文抓取、页面噪声清理与 Markdown 剪藏
├── tech-article-rewriter-vp/ # URL/截图语料采集、技术文章深度重写、模板化 Markdown 草稿生成与迭代
└── README.md            # 知识类技能目录说明
```

## 已有技能

### [`project-concept-explainer-vp/`](project-concept-explainer-vp/)

用于项目伴读和技术概念讲解：读取当前仓库上下文，解释项目里的关键术语、模型、算法、数据字段和架构决策，也可以生成项目知识地图、术语表、学习笔记和研究笔记

### [`learning-repo-log-vp/`](learning-repo-log-vp/)

用于按仓库维护学习复盘记录：当用户说“记一下”“记录到复盘”“把这个概念加入学习文档”时，将技术栈、名词概念、架构决策、工程实践、业务理解和待复习问题追加到 `{{项目名}}_学习复盘_技术栈与概念记录.md`

### [`gif-showcase-maker-vp/`](gif-showcase-maker-vp/)

用于把多张图片按顺序合成一个 GIF 展示图：默认按输入顺序播放，每张图停留一段时间，相邻图片之间使用淡入淡出转场，适合 GitHub README、项目报告、学习笔记和功能介绍素材

### [`paper-fetcher-vp/`](paper-fetcher-vp/)

用于研究论文入库：从标题、截图文字、URL 或摘录识别论文，优先核验官方来源，下载并验证 PDF，按研究领域前缀重命名，并输出 arXiv ID 或 DOI 供 Zotero Add Item by Identifier 使用

### [`zhihu-clippings-vp/`](zhihu-clippings-vp/)

用于知乎文章剪藏：先用知乎开放平台做作者、标题和 article_id 定位，再用 TikHub 补全完整正文，保留公式、图片、表格和代码块，按自定义范围输出 Obsidian 友好的 Markdown 文件

### [`wechat-clippings-vp/`](wechat-clippings-vp/)

用于微信公众号文章剪藏：从公众号名、文章链接、标题或截图 OCR 定位文章，通过 TikHub 获取正文，清理微信页面尾巴、二维码引流、空列表项和格式噪声，输出 Obsidian 友好的 Markdown 文件

### [`tech-article-rewriter-vp/`](tech-article-rewriter-vp/)

用于技术文章深度重写：从 URL、截图、OCR 或现成语料出发，先获取并缓存可信全文，再提取事实、观点、代码和坑点，重建文章逻辑，按 Markdown 模板生成专业标题、轻松正文、逻辑清晰且带参考资料的技术博客草稿

## 适合沉淀的技能

- 自顶向下学习流程
- 概念解释与对比模板
- 研究论文处理
- 文章摘要与重写
- 知识地图抽取
- 笔记清理与结构化
- 学习检查与反问
- 写作与翻译流程

## 编写原则

每个 skill 都应该保留有用的思考结构，而不只是 prompt 风格。遇到依赖判断的任务时，优先提供明确的输入要求、决策规则、输出格式和示例

一个知识类 skill 至少应该回答：

- 这个 skill 解决哪类知识工作问题
- 输入材料可以是什么形式
- Agent 应该如何拆解、判断和组织信息
- 结果应该输出成什么结构
- 哪些结论需要来源、证据或不确定性标注
- 哪些内容不能猜测或过度补全
