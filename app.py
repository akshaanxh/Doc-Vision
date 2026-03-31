from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import cv2

from src.document_scanner import DocumentScanner
from src.pdf_utils import images_to_pdf

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_images(input_path: Path) -> List[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() not in VALID_EXTENSIONS:
            raise ValueError(f"Unsupported image type: {input_path.suffix}")
        return [input_path]

    if input_path.is_dir():
        image_paths = sorted(
            p for p in input_path.iterdir() if p.suffix.lower() in VALID_EXTENSIONS
        )
        if not image_paths:
            raise ValueError(f"No supported images found in directory: {input_path}")
        return image_paths

    raise FileNotFoundError(f"Input path does not exist: {input_path}")


def save_debug_images(debug_dir: Path, debug_images: dict) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    for filename, image in debug_images.items():
        cv2.imwrite(str(debug_dir / filename), image)


def process_images(input_paths: Iterable[Path], output_dir: Path, debug: bool) -> List[Path]:
    scanner = DocumentScanner()
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_scans: List[Path] = []

    for image_path in input_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"[SKIP] Could not read image: {image_path}")
            continue

        result = scanner.scan(image)
        stem = image_path.stem
        out_path = output_dir / f"{stem}_scanned.png"

        if result.success:
            cv2.imwrite(str(out_path), result.scanned)
            saved_scans.append(out_path)
            print(f"[OK] {image_path.name} -> {out_path.name}")
        else:
            print(f"[FAIL] {image_path.name}: {result.message}")

        if debug:
            debug_dir = output_dir / f"{stem}_debug"
            save_debug_images(debug_dir, scanner.debug_images(result))

    return saved_scans


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smart document scanner using OpenCV."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a single image or a folder of images.",
    )
    parser.add_argument(
        "--output",
        default="outputs",
        help="Directory where scanned results will be stored.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save intermediate images for analysis and report screenshots.",
    )
    parser.add_argument(
        "--make-pdf",
        action="store_true",
        help="Combine all successfully scanned pages into one PDF.",
    )
    parser.add_argument(
        "--pdf-name",
        default="scanned_document.pdf",
        help="Output name for the combined PDF.",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)

    images = collect_images(input_path)
    saved_scans = process_images(images, output_dir, args.debug)

    if args.make_pdf and saved_scans:
        pdf_path = output_dir / args.pdf_name
        images_to_pdf(saved_scans, pdf_path)
        print(f"[PDF] Combined scanned pages saved to {pdf_path}")

    if not saved_scans:
        raise SystemExit("No scans were produced. Check the input images.")


if __name__ == "__main__":
    main()
