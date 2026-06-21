---
name: gif-showcase-maker-vp
description: Create animated GIF showcases from multiple input images. Use when the user provides images and wants an ordered GIF demo, image sequence animation, feature showcase, product preview, screenshot carousel, or before/after presentation. Defaults to upload/input order, hold frames per image, fade transitions, automatic canvas sizing, and a local GIF output path.
---

# GIF Showcase Maker

## Purpose

Generate a lightweight GIF from multiple images. The default mode is a simple ordered carousel:

```text
image 1 hold -> fade to image 2 -> image 2 hold -> fade to image 3 -> image 3 hold
```

Use this skill for README demos, product screenshots, feature introductions, visual changelogs, and quick image-sequence previews.

## Dependency

The script requires Pillow:

```bash
pip install pillow
```

Use Python 3.10 or newer.

Do not add heavy video dependencies unless the user asks for MP4/WebP or advanced effects.

## Default Behavior

When the user provides image attachments or local image paths, those user-provided images are the required input.
Do not replace them with generated placeholder images.
Use generated test images only when the user explicitly asks for a reproducible self-test or when no user images are available and the response clearly says it is only a test.

If the user does not specify parameters, use:

```text
order: input/upload order
fps: 12
hold-ms: 900
fade-ms: 450
fit: contain
background: #ffffff
loop: 0
output: showcase.gif
```

The default output should be written under the current project or a temporary output folder, not into a hardcoded personal path.
For this repository layout, prefer writing generated GIFs under the skill folder's `output/` directory, for example `knowledge-skills/gif-showcase-maker-vp/output/user-showcase.gif`.

## Workflow

1. Identify the input image files and preserve the user's order unless they provide an explicit order.
2. Choose a canvas size:
   - Use `--width` / `--height` if provided
   - Otherwise use the first image size
3. Resize every image into the canvas with `fit=contain` by default.
4. Add hold frames for each image.
5. Add cross-fade transition frames between adjacent images.
6. Save a looping GIF.
7. Verify that the output file exists, has multiple frames, expected dimensions, and visible frame changes.
8. Open the folder that contains the generated GIF in Windows File Explorer so the user can immediately inspect the output file. Prefer opening the skill-internal `output/` folder when using this skill in a repository.
9. Return the GIF path and, when supported, embed the generated GIF with Markdown image syntax in the final answer.

## Typical Commands

Minimal:

```bash
python scripts/make_sequence_gif.py --images image1.png image2.png image3.png --output showcase.gif
```

With timing and canvas:

```bash
python scripts/make_sequence_gif.py \
  --images role.png bag.png shop.png \
  --output showcase.gif \
  --fps 12 \
  --hold-ms 900 \
  --fade-ms 450 \
  --width 1200 \
  --background "#dbeafe"
```

## Verification

After generating the GIF, run a quick check:

```bash
python scripts/make_sequence_gif.py --verify showcase.gif
```

The check should report:

- file size
- frame count
- dimensions
- duration
- whether sampled frames differ

GIF encoders can merge identical hold frames into a single frame with a longer duration. Prefer duration, dimensions, nonzero size, and visible frame differences over exact repeated-hold frame counts.

## Public Repository Rules

- Do not commit generated GIFs unless they are small intentional examples.
- Do not commit private screenshots unless the user explicitly asks.
- Do not hardcode local user paths.
- Keep dependencies in `requirements.txt`.
- Keep examples reproducible with generated placeholder images or documented input images.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
