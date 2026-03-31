from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from PIL import Image


def images_to_pdf(image_paths: Iterable[Path], output_pdf: Path) -> None:
    paths: List[Path] = [Path(p) for p in image_paths]
    if not paths:
        raise ValueError("No images were provided for PDF export.")

    pil_images = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        pil_images.append(image)

    first, rest = pil_images[0], pil_images[1:]
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    first.save(output_pdf, save_all=True, append_images=rest)
