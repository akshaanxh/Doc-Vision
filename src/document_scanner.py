from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import cv2
import numpy as np


@dataclass
class ScanResult:
    original: np.ndarray
    resized: np.ndarray
    edged: np.ndarray
    contour_image: np.ndarray
    warped_color: np.ndarray
    scanned: np.ndarray
    contour: Optional[np.ndarray]
    success: bool
    message: str


class DocumentScanner:
    """Detects a document-like quadrilateral in an image and scans it."""

    def __init__(
        self,
        resize_height: int = 800,
        canny_threshold_1: int = 75,
        canny_threshold_2: int = 200,
        blur_kernel: Tuple[int, int] = (5, 5),
    ) -> None:
        self.resize_height = resize_height
        self.canny_threshold_1 = canny_threshold_1
        self.canny_threshold_2 = canny_threshold_2
        self.blur_kernel = blur_kernel

    @staticmethod
    def _order_points(pts: np.ndarray) -> np.ndarray:
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # top-left
        rect[2] = pts[np.argmax(s)]  # bottom-right

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left
        return rect

    @staticmethod
    def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        rect = DocumentScanner._order_points(pts)
        (tl, tr, br, bl) = rect

        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        max_width = int(max(width_a, width_b))

        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        max_height = int(max(height_a, height_b))

        dst = np.array(
            [
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1],
            ],
            dtype="float32",
        )

        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
        return warped

    @staticmethod
    def _enhance_scan(warped_color: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(warped_color, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Improve local contrast for uneven lighting.
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Adaptive threshold creates a strong scanned-paper look.
        scanned = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            21,
            15,
        )

        # Mild denoising and closing to reduce small holes in strokes.
        kernel = np.ones((2, 2), np.uint8)
        scanned = cv2.morphologyEx(scanned, cv2.MORPH_CLOSE, kernel)

        # Remove tiny border artifacts introduced during warping.
        if scanned.shape[0] > 20 and scanned.shape[1] > 20:
            scanned = scanned[5:-5, 5:-5]
        return scanned

    def _resize(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        ratio = image.shape[0] / float(self.resize_height)
        resized = cv2.resize(
            image,
            (int(image.shape[1] / ratio), self.resize_height),
            interpolation=cv2.INTER_AREA,
        )
        return resized, ratio

    def _preprocess(self, resized: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)

        edged = cv2.Canny(blurred, self.canny_threshold_1, self.canny_threshold_2)
        edged = cv2.dilate(edged, np.ones((3, 3), np.uint8), iterations=1)
        edged = cv2.erode(edged, np.ones((3, 3), np.uint8), iterations=1)

        # Bright-page mask helps when the paper is much lighter than the background.
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
        return edged, thresh

    def _score_quad(self, approx: np.ndarray, image_shape: Tuple[int, int]) -> float:
        area = cv2.contourArea(approx)
        image_area = image_shape[0] * image_shape[1]
        if area < 0.15 * image_area:
            return -1
        return area

    def _find_document_contour(self, masks: Tuple[np.ndarray, np.ndarray]) -> Optional[np.ndarray]:
        candidates = []
        for idx, mask in enumerate(masks):
            retrieval_mode = cv2.RETR_EXTERNAL if idx == 1 else cv2.RETR_LIST
            contours, _ = cv2.findContours(mask.copy(), retrieval_mode, cv2.CHAIN_APPROX_SIMPLE)
            candidates.extend(contours)

        candidates = sorted(candidates, key=cv2.contourArea, reverse=True)[:25]
        best_quad = None
        best_score = -1.0

        for contour in candidates:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) != 4:
                continue

            score = self._score_quad(approx, masks[0].shape)
            if score > best_score:
                best_quad = approx
                best_score = score

        return best_quad

    def scan(self, image: np.ndarray) -> ScanResult:
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or invalid.")

        original = image.copy()
        resized, ratio = self._resize(image)
        edged, thresh = self._preprocess(resized)
        contour = self._find_document_contour((edged, thresh))
        contour_image = resized.copy()

        if contour is None:
            return ScanResult(
                original=original,
                resized=resized,
                edged=edged,
                contour_image=contour_image,
                warped_color=resized.copy(),
                scanned=cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY),
                contour=None,
                success=False,
                message="Document boundary not detected. Try a clearer image with visible page edges.",
            )

        cv2.drawContours(contour_image, [contour], -1, (0, 255, 0), 3)
        warped_color = self._four_point_transform(original, contour.reshape(4, 2) * ratio)
        scanned = self._enhance_scan(warped_color)

        return ScanResult(
            original=original,
            resized=resized,
            edged=edged,
            contour_image=contour_image,
            warped_color=warped_color,
            scanned=scanned,
            contour=contour,
            success=True,
            message="Document scanned successfully.",
        )

    def debug_images(self, result: ScanResult) -> Dict[str, np.ndarray]:
        return {
            "01_resized_input.jpg": result.resized,
            "02_edges.jpg": result.edged,
            "03_detected_contour.jpg": result.contour_image,
            "04_warped_color.jpg": result.warped_color,
            "05_scanned_binary.jpg": result.scanned,
        }
