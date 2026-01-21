"""Explainability helpers for image modality."""

from __future__ import annotations

from pathlib import Path

import cv2

from ..utils.logging import ensure_dir
from ..utils.types import DetectedEntity


def render_image_overlay(image_path: Path, entities: list[DetectedEntity], output_path: Path) -> Path:
    """Draw bounding boxes for sensitive image regions."""

    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Unable to load image for overlay: {image_path}")

    for entity in entities:
        if not entity.bbox:
            continue
        x, y, w, h = (
            int(entity.bbox.x),
            int(entity.bbox.y),
            int(entity.bbox.width),
            int(entity.bbox.height),
        )
        color = (0, 255, 0) if entity.mitigation == "blur" else (255, 0, 0)
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        label = f"{entity.label} ({entity.mitigation})"
        cv2.putText(image, label, (x, max(0, y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    ensure_dir(output_path)
    cv2.imwrite(str(output_path), image)
    return output_path
