<h1 align="center">
  GIF Showcase Maker VP | GIF 展示图生成技能
</h1>

<p align="center">
  把多张截图、界面图或演示图按顺序合成为轻量 GIF，支持停留帧、淡入转场、固定画布和输出验证
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-knowledge--skills-purple" alt="knowledge skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/gif--showcase--maker--vp-media-orange" alt="gif showcase maker vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
输入图片序列  ->  画布尺寸归一  ->  contain/cover 适配  ->  停留帧生成  ->  淡入转场  ->  GIF 验证输出
```

---

## 为什么要做 GIF Showcase Maker?

GitHub README、项目报告、功能介绍和视觉变更记录经常需要一个“几秒钟看懂流程”的展示图。直接贴多张截图会占空间，录屏又可能带来体积、编码、播放器兼容和隐私画面问题

GIF Showcase Maker 解决的是“把一组图片稳定合成可复现 GIF 展示素材”的问题。它不是视频剪辑器，也不依赖复杂的 FFmpeg 流程，而是让 Agent 用一个轻量脚本完成图片排序、画布统一、图片适配、停留帧、淡入淡出和结果校验

核心策略是 **ordered images, simple motion, verifiable output**：

- 默认尊重用户提供图片的顺序，适合产品截图、前后对比、步骤演示和设计稿轮播
- 每张图片先停留，再与下一张图交叉淡入，避免突兀跳帧
- 默认使用 `contain` 保留完整图片内容，固定画布时用背景色补齐空白区域
- 生成后用脚本验证文件大小、帧数、尺寸、总时长和抽样帧差异，减少“看似生成但内容没动”的问题

## 工作原理

1. **输入识别**：接受一组 PNG、JPG、JPEG 或其他 Pillow 支持的图片路径，默认按命令行输入顺序播放

2. **排序策略**：默认使用 `--sort input` 保持用户上传或传参顺序。如果图片文件名已经带有 `01-xxx.png`、`02-xxx.png` 这类序号，也可以用 `--sort name` 按文件名排序

3. **画布选择**：优先使用 `--width` 和 `--height` 指定固定画布。未指定时，使用第一张图片的尺寸作为整段 GIF 的画布尺寸

4. **图片适配**：每张图片都会被转换到统一画布

   - `contain`：完整保留图片，可能在四周出现背景留白
   - `cover`：铺满画布，可能裁切图片边缘
   - `--background`：用于设置留白背景色，默认 `#ffffff`

5. **停留帧生成**：每张图按 `--hold-ms` 停留一段时间，默认 `900ms`

6. **淡入转场**：相邻图片之间按 `--fade-ms` 生成交叉淡入帧，默认 `450ms`

7. **GIF 保存**：按 `--fps` 控制每秒帧数，默认 `12fps`。`--loop 0` 表示无限循环播放

8. **结果验证**：`--verify` 会输出 JSON 指标，包括文件大小、帧数、宽高、总时长和抽样帧是否存在可见差异

## 快速上手

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

运行环境建议使用 Python 3.10 或更新版本。当前脚本唯一运行依赖是 Pillow

### 2. 最小生成命令

```powershell
python .\scripts\make_sequence_gif.py --images image1.png image2.png image3.png --output showcase.gif
```

默认动画节奏是：

```text
image 1 hold  ->  fade to image 2  ->  image 2 hold  ->  fade to image 3  ->  image 3 hold
```

### 3. 调整节奏和画布

```powershell
python .\scripts\make_sequence_gif.py `
  --images role.png bag.png shop.png `
  --output showcase.gif `
  --fps 12 `
  --hold-ms 900 `
  --fade-ms 450 `
  --width 1200 `
  --height 675 `
  --background "#dbeafe"
```

### 4. 生成可复现测试图片

```powershell
python .\scripts\make_sequence_gif.py --make-test-images .tmp_gif_test
```

随后可以用这三张占位图生成测试 GIF：

```powershell
python .\scripts\make_sequence_gif.py `
  --images .tmp_gif_test\01-role.png .tmp_gif_test\02-bag.png .tmp_gif_test\03-shop.png `
  --output .tmp_gif_test\showcase.gif
```

### 5. 验证输出

```powershell
python .\scripts\make_sequence_gif.py --verify .tmp_gif_test\showcase.gif
```

输出示例：

```json
{
  "path": ".tmp_gif_test\\showcase.gif",
  "bytes": 123456,
  "frames": 38,
  "width": 640,
  "height": 360,
  "duration_ms": 3154,
  "sampled_frames_differ": true
}
```

## 默认参数

| 参数 | 默认值 | 含义 |
|---|---:|---|
| `--fps` | `12` | 每秒帧数，影响动画流畅度和 GIF 体积 |
| `--hold-ms` | `900` | 每张图片静止停留时间 |
| `--fade-ms` | `450` | 相邻图片的淡入淡出转场时间 |
| `--fit` | `contain` | 图片适配模式，默认完整保留图片 |
| `--background` | `#ffffff` | 画布背景色 |
| `--loop` | `0` | 循环次数，`0` 表示无限循环 |
| `--sort` | `input` | 图片排序方式，默认按输入顺序 |
| `--output` | `showcase.gif` | 输出文件路径 |

## 输出格式

默认输出是一个本地 GIF 文件。在本仓库中运行时，建议写入 skill 内部的 `output/` 目录，例如：

```text
knowledge-skills/gif-showcase-maker-vp/output/user-showcase.gif
```

生成完成后，Agent 应打开这个 GIF 所在文件夹，方便直接检查输出结果。Agent 在支持 Markdown 预览的环境里，也可以返回图片路径并嵌入：

```markdown
![showcase](showcase.gif)
```

公开仓库中不建议默认提交生成的 GIF。若确实需要 README 示例，应使用小尺寸、可公开、可复现的示例素材，并确认文件体积不会让仓库变重

## 目录结构

```text
gif-showcase-maker-vp/
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/
│   └── openai.yaml
└── scripts/
    └── make_sequence_gif.py
```

## 注意事项

- 生成 GIF 前应确认图片顺序，默认不会自动按文件名重排
- 公开项目不要提交私人截图、客户界面、后台数据或未经授权的产品图
- 生成的 GIF 可能比图片本身更大，提交前应检查体积
- GIF 编码器可能把相同停留帧合并为一个更长 duration 的帧，因此不要只用精确帧数判断是否成功
- 当前技能只依赖 Pillow，不默认引入 FFmpeg、视频编码器或大型媒体处理依赖
- 示例应优先使用 `--make-test-images` 生成的占位图，方便其他人复现实验
- 生成的文件统一使用普通本地路径，不写死个人用户目录或私有项目路径
