#!/usr/bin/env python
"""Create an ordered cross-fade GIF from multiple images."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageColor, ImageDraw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or verify an ordered image-sequence GIF.")
    parser.add_argument("--images", nargs="+", default=[], help="Input images in playback order.")
    parser.add_argument("--output", default="showcase.gif", help="Output GIF path.")
    parser.add_argument("--fps", type=int, default=12, help="Frames per second.")
    parser.add_argument("--hold-ms", type=int, default=900, help="Still time per image.")
    parser.add_argument("--fade-ms", type=int, default=450, help="Cross-fade time between images.")
    parser.add_argument("--width", type=int, default=None, help="Canvas width. Defaults to first image width.")
    parser.add_argument("--height", type=int, default=None, help="Canvas height. Defaults to first image height.")
    parser.add_argument("--background", default="#ffffff", help="Canvas background color.")
    parser.add_argument("--fit", choices=["contain", "cover"], default="contain", help="Image fit mode.")
    parser.add_argument("--loop", type=int, default=0, help="GIF loop count. 0 means forever.")
    parser.add_argument("--sort", choices=["input", "name"], default="input", help="Input order strategy.")
    parser.add_argument("--verify", default=None, help="Verify an existing GIF and print JSON metrics.")
    parser.add_argument("--make-test-images", default=None, help="Create three placeholder PNGs in the given folder.")
    return parser.parse_args()


def frame_count(milliseconds: int, fps: int, minimum: int = 1) -> int:
    return max(minimum, int(round(milliseconds / 1000 * fps)))


def load_images(paths: Iterable[str]) -> list[Image.Image]:
    images: list[Image.Image] = []
    for path in paths:
        image_path = Path(path)
        if not image_path.exists():
            raise FileNotFoundError(f"Input image not found: {image_path}")
        images.append(Image.open(image_path).convert("RGBA"))
    if not images:
        raise ValueError("At least one input image is required.")
    return images


def fit_image(image: Image.Image, size: tuple[int, int], background: str, mode: str) -> Image.Image:
    canvas_w, canvas_h = size
    bg = Image.new("RGBA", size, ImageColor.getrgb(background) + (255,))
    scale = max(canvas_w / image.width, canvas_h / image.height) if mode == "cover" else min(canvas_w / image.width, canvas_h / image.height)
    resized_w = max(1, int(round(image.width * scale)))
    resized_h = max(1, int(round(image.height * scale)))
    resized = image.resize((resized_w, resized_h), Image.Resampling.LANCZOS)

    if mode == "cover":
        left = max(0, (resized_w - canvas_w) // 2)
        top = max(0, (resized_h - canvas_h) // 2)
        resized = resized.crop((left, top, left + canvas_w, top + canvas_h))
        bg.alpha_composite(resized, (0, 0))
    else:
        left = (canvas_w - resized_w) // 2
        top = (canvas_h - resized_h) // 2
        bg.alpha_composite(resized, (left, top))
    return bg


def build_frames(images: list[Image.Image], fps: int, hold_ms: int, fade_ms: int, background: str, fit: str, width: int | None, height: int | None) -> tuple[list[Image.Image], int]:
    first = images[0]
    canvas = (width or first.width, height or first.height)
    normalized = [fit_image(image, canvas, background, fit) for image in images]
    hold_n = frame_count(hold_ms, fps)
    fade_n = frame_count(fade_ms, fps)
    duration_ms = int(round(1000 / fps))

    frames: list[Image.Image] = []
    for idx, image in enumerate(normalized):
        frames.extend([image.copy() for _ in range(hold_n)])
        if idx < len(normalized) - 1:
            nxt = normalized[idx + 1]
            for step in range(1, fade_n + 1):
                alpha = step / (fade_n + 1)
                frames.append(Image.blend(image, nxt, alpha))
    return frames, duration_ms


def save_gif(frames: list[Image.Image], output: str, duration_ms: int, loop: int) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames_rgb = [frame.convert("P", palette=Image.Palette.ADAPTIVE) for frame in frames]
    frames_rgb[0].save(
        out,
        save_all=True,
        append_images=frames_rgb[1:],
        duration=duration_ms,
        loop=loop,
        optimize=False,
    )
    return out


def verify_gif(path: str) -> dict[str, object]:
    gif = Path(path)
    if not gif.exists():
        raise FileNotFoundError(f"GIF not found: {gif}")
    with Image.open(gif) as image:
        frame_total = getattr(image, "n_frames", 1)
        size = image.size
        duration = 0
        sampled = []
        indices = sorted(set([0, max(0, frame_total // 2), max(0, frame_total - 1)]))
        for i in range(frame_total):
            image.seek(i)
            duration += int(image.info.get("duration", 0))
            if i in indices:
                sampled.append(image.convert("RGB").copy())
        differs = False
        for a, b in zip(sampled, sampled[1:]):
            diff = ImageChops.difference(a, b)
            if diff.getbbox() is not None:
                differs = True
                break
    return {
        "path": str(gif),
        "bytes": gif.stat().st_size,
        "frames": frame_total,
        "width": size[0],
        "height": size[1],
        "duration_ms": duration,
        "sampled_frames_differ": differs,
    }


def make_test_images(folder: str) -> list[str]:
    out_dir = Path(folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("01-role.png", "#f8d7da", "#b42318", "Role"),
        ("02-bag.png", "#d1fae5", "#047857", "Bag"),
        ("03-shop.png", "#dbeafe", "#1d4ed8", "Shop"),
    ]
    paths: list[str] = []
    for name, bg, fg, label in specs:
        image = Image.new("RGB", (640, 360), bg)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((70, 55, 570, 305), radius=24, outline=fg, width=8)
        draw.text((265, 160), label, fill=fg)
        path = out_dir / name
        image.save(path)
        paths.append(str(path))
    return paths


def main() -> None:
    args = parse_args()
    if args.verify:
        print(json.dumps(verify_gif(args.verify), ensure_ascii=False, indent=2))
        return
    if args.make_test_images:
        print(json.dumps({"images": make_test_images(args.make_test_images)}, ensure_ascii=False, indent=2))
        return
    image_paths = sorted(args.images) if args.sort == "name" else args.images
    images = load_images(image_paths)
    frames, duration_ms = build_frames(
        images,
        fps=args.fps,
        hold_ms=args.hold_ms,
        fade_ms=args.fade_ms,
        background=args.background,
        fit=args.fit,
        width=args.width,
        height=args.height,
    )
    output = save_gif(frames, args.output, duration_ms, args.loop)
    result = verify_gif(str(output))
    result["input_images"] = image_paths
    result["fps"] = args.fps
    result["hold_ms"] = args.hold_ms
    result["fade_ms"] = args.fade_ms
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
