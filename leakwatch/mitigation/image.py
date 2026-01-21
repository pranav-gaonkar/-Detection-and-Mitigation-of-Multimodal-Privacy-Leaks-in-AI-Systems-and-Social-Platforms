"""Image mitigation strategies."""

from __future__ import annotations

import re
from textwrap import wrap
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np

from ..utils.config import ImageConfig
from ..utils.types import DetectedEntity


DATE_RE = re.compile(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})")
PHONE_DIGIT_RE = re.compile(r"\d")


class ImageMitigator:
    """Apply blurring to faces and synthetic replacements to text regions."""

    def __init__(self, config: ImageConfig) -> None:
        self.config = config

    def mitigate(
        self,
        path: Path,
        entities: List[DetectedEntity],
        output_path: Path | None,
    ) -> Tuple[Path, List[DetectedEntity]]:
        image = cv2.imread(str(path))
        if image is None:
            raise FileNotFoundError(f"Unable to load image: {path}")

        if output_path is None:
            output_path = path.with_name(f"{path.stem}.sanitized{path.suffix}")

        updated_entities: list[DetectedEntity] = []
        for entity in entities:
            if not entity.bbox:
                continue
            x, y, w, h = (
                int(entity.bbox.x),
                int(entity.bbox.y),
                int(entity.bbox.width),
                int(entity.bbox.height),
            )
            roi = image[y : y + h, x : x + w]
            if roi.size == 0:
                continue
            if entity.label.lower() == "face":
                image[y : y + h, x : x + w] = self._blur_region(roi)
                action = "blur"
            else:
                synthetic = self._synthetic_text(entity)
                self._rewrite_region(image, x, y, w, h, synthetic, roi.copy())
                action = "replace"
            updated_entities.append(entity.model_copy(update={"mitigation": action}))

        cv2.imwrite(str(output_path), image)
        return output_path, updated_entities

    def _blur_region(self, roi: np.ndarray) -> np.ndarray:
        kernel = (self.config.face_blur_kernel, self.config.face_blur_kernel)
        return cv2.GaussianBlur(roi, kernel, 0)

    def _rewrite_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str,
        original_roi: np.ndarray,
    ) -> None:
        region = image[y : y + h, x : x + w]
        softened = self._soften_background(region)
        region[:, :] = softened

        max_chars = max(8, w // 11)
        lines = wrap(text, width=max_chars)
        font_scale = max(0.4, min(w, h) / 140)
        thickness = 1 if font_scale < 0.9 else 2
        text_color = self._text_color_from_region(original_roi)
        y_cursor = max(18, int(font_scale * 20))
        max_lines = max(1, h // max(16, int(font_scale * 30)))

        for line in lines[:max_lines]:
            (text_width, text_height), _ = cv2.getTextSize(
                line,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                thickness,
            )
            text_x = max(4, (w - text_width) // 2)
            y_cursor = min(h - 6, y_cursor + text_height + 4)
            cv2.putText(
                region,
                line,
                (text_x, y_cursor),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                text_color,
                thickness,
                cv2.LINE_AA,
            )

    def _synthetic_text(self, entity: DetectedEntity) -> str:
        raw = (entity.text or entity.label or "REDACTED").strip()
        upper = raw.upper()
        if not raw:
            return "[REDACTED]"
        if "DATE" in upper or "DOB" in upper or DATE_RE.search(raw):
            return self._mask_date(raw)
        if "TEL" in upper or "PHONE" in upper or self._looks_like_phone(raw):
            return self._mask_phone(raw)
        if "SOCIAL" in upper or "SSN" in upper:
            return "SOCIAL SECURITY NO: XX-XX-XXXX"
        if "CLASSIFIED" in upper or "CONFIDENTIAL" in upper:
            return "CLASSIFIED CONTENT - DO NOT DISTRIBUTE"
        return self._mask_name_like(raw)

    @staticmethod
    def _mask_date(text: str) -> str:
        def repl(match: re.Match[str]) -> str:
            day, month, year = match.groups()
            day_mask = f"{day[:1]}x" if len(day) > 1 else "0x"
            month_mask = f"{month[:1]}a" if len(month) > 1 else "1a"
            year_mask = f"{year[:2]}xx" if len(year) >= 2 else "19xx"
            return f"{day_mask}/{month_mask}/{year_mask}"

        return DATE_RE.sub(repl, text, count=1)

    def _mask_phone(self, text: str) -> str:
        digits = re.sub(r"\D", "", text)
        if len(digits) < 4:
            return "PHONE: XXX-XXXX"
        masked = digits[:2] + "x" * max(0, len(digits) - 4) + digits[-2:]
        iter_digits = iter(masked)

        def replace_char(ch: str) -> str:
            return next(iter_digits, "x") if ch.isdigit() else ch

        rebuilt = "".join(replace_char(ch) for ch in text)
        remaining = "".join(iter_digits)
        return rebuilt + remaining

    @staticmethod
    def _mask_name_like(text: str) -> str:
        tokens = text.split()
        result_tokens = []
        for token in tokens:
            clean = re.sub(r"[^A-Za-z]", "", token)
            if not clean:
                result_tokens.append("X")
                continue
            if len(clean) == 1:
                result_tokens.append(f"{clean.upper()}x")
            else:
                result_tokens.append(f"{clean[0].upper()}xx{clean[-1].upper()} {len(clean)}")
        return " ".join(result_tokens)

    @staticmethod
    def _looks_like_phone(text: str) -> bool:
        digit_count = len(PHONE_DIGIT_RE.findall(text))
        return digit_count >= 7

    @staticmethod
    def _soften_background(region: np.ndarray) -> np.ndarray:
        smallest_dim = max(3, min(region.shape[0], region.shape[1]) // 3)
        kernel = smallest_dim if smallest_dim % 2 == 1 else smallest_dim + 1
        kernel = max(3, min(kernel, 51))
        blurred = cv2.medianBlur(region, kernel)
        return cv2.addWeighted(blurred, 0.9, region, 0.1, 0)

    @staticmethod
    def _text_color_from_region(region: np.ndarray) -> Tuple[int, int, int]:
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text_mask = thresh < 128
        if np.count_nonzero(text_mask) < 20:
            brightness = gray.mean()
            return (40, 40, 40) if brightness > 128 else (230, 230, 230)
        text_pixels = region[text_mask]
        mean_color = np.mean(text_pixels, axis=0)
        if np.isnan(mean_color).any():
            return (40, 40, 40)
        return tuple(int(c) for c in mean_color)
