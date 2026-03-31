from __future__ import annotations

from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "sample_inputs"


def get_font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def make_page(text_lines, size=(900, 1200)):
    page = Image.new("RGBA", size, (245, 241, 233, 255))
    draw = ImageDraw.Draw(page)
    font = get_font(32)
    title_font = get_font(42)
    y = 80
    draw.text((90, y), text_lines[0], fill=(30, 30, 30, 255), font=title_font)
    y += 90
    for line in text_lines[1:]:
        draw.text((90, y), line, fill=(40, 40, 40, 255), font=font)
        y += 55
    return page


def paste_page_on_background(page: Image.Image, output_path: Path, angle: int, offset=(230, 110)):
    bg = Image.new("RGBA", (1800, 1400), (110, 92, 75, 255))

    rotated = page.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    page_alpha = rotated.getchannel("A")

    shadow = Image.new("RGBA", rotated.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    bbox = page_alpha.getbbox()
    if bbox is None:
        bbox = (0, 0, rotated.size[0], rotated.size[1])
    shadow_draw.rounded_rectangle(bbox, radius=18, fill=(0, 0, 0, 85))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))

    bg.alpha_composite(shadow, (offset[0] + 20, offset[1] + 20))
    bg.alpha_composite(rotated, offset)

    final = bg.convert("RGB").filter(ImageFilter.GaussianBlur(radius=0.3))
    final.save(output_path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    samples = [
        [
            "Computer Vision Lab Notes",
            "1. Edge detection finds page boundaries.",
            "2. Contours trace continuous outlines.",
            "3. Perspective warping fixes viewpoint.",
            "4. Adaptive threshold boosts readability.",
            "5. Morphology removes tiny artifacts.",
        ],
        [
            "Assignment Submission",
            "Course: Computer Vision",
            "Problem: A practical CV mini-project",
            "Method: OpenCV document scanner",
            "Output: Clean page image and PDF",
            "Result: Faster digital archive",
        ],
        [
            "Weekly Study Plan",
            "Monday - Image filtering and kernels",
            "Tuesday - Canny edge detection",
            "Wednesday - Contours and shapes",
            "Thursday - Homography and warping",
            "Friday - Thresholding and cleanup",
        ],
    ]

    configs = [(-11, (240, 100)), (9, (330, 120)), (-7, (290, 110))]

    for idx, lines in enumerate(samples, start=1):
        page = make_page(lines)
        angle, offset = configs[idx - 1]
        paste_page_on_background(page, OUT_DIR / f"sample_{idx}.jpg", angle, offset)

    print(f"Generated {len(samples)} sample images in {OUT_DIR}")


if __name__ == "__main__":
    main()
