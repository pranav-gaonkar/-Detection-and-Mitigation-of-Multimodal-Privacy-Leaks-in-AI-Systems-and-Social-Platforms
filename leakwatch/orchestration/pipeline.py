"""Pipeline orchestration for LeakWatch."""

from __future__ import annotations

from pathlib import Path

from ..detection import ImageDetector, TextDetector
from ..explainability.audit import record_audit
from ..explainability.image import render_image_overlay
from ..explainability.text import render_text_spans
from ..mitigation import ImageMitigator, TextMitigator
from ..utils.config import LeakWatchConfig, get_config
from ..utils.logging import ensure_dir, get_logger
from ..utils.types import DetectionResult, Modality

LOGGER = get_logger(__name__)
TEXT_EXTENSIONS = {".txt", ".md", ".json"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


class PipelineManager:
    """Coordinate modality-specific detectors and mitigators."""

    def __init__(self, config: LeakWatchConfig | None = None) -> None:
        self.config = config or get_config()
        self.text_detector = TextDetector(self.config.text)
        self.text_mitigator = TextMitigator(self.config.text)
        self.image_detector = ImageDetector(self.config.image, text_detector=self.text_detector)
        self.image_mitigator = ImageMitigator(self.config.image)

    # --- Text Modality -------------------------------------------------
    def process_text(self, path: Path) -> DetectionResult:
        source_path = Path(path)
        raw_text = source_path.read_text(encoding="utf-8")
        LOGGER.info("Processing text: %s", source_path.name)
        entities = self.text_detector.detect(raw_text)
        sanitized_text, mitigated_entities = self.text_mitigator.mitigate(raw_text, entities)
        output_path = self._output_path(source_path, suffix=".sanitized.txt")
        ensure_dir(output_path)
        output_path.write_text(sanitized_text, encoding="utf-8")
        artifacts = []
        if self.config.explainability.save_text_spans:
            span_path = output_path.with_suffix(".spans.txt")
            artifacts.append(render_text_spans(sanitized_text, mitigated_entities, span_path))

        result = DetectionResult(
            source_path=source_path,
            modality=Modality.TEXT,
            entities=mitigated_entities,
            mitigated_output=output_path,
            artifacts=artifacts,
        )
        self._attach_audit(result)
        return result

    # --- Image Modality -----------------------------------------------
    def process_image(self, path: Path, output_path: Path | None = None) -> DetectionResult:
        source_path = Path(path)
        LOGGER.info("Processing image: %s", source_path.name)
        entities = self.image_detector.detect(source_path)
        final_output = output_path or self._output_path(source_path, suffix=f".sanitized{source_path.suffix}")
        ensure_dir(final_output)
        mitigated_path, mitigated_entities = self.image_mitigator.mitigate(source_path, entities, final_output)
        artifacts = []
        if self.config.explainability.save_image_overlays and mitigated_entities:
            overlay_path = final_output.with_suffix(".overlay.png")
            artifacts.append(render_image_overlay(mitigated_path, mitigated_entities, overlay_path))

        result = DetectionResult(
            source_path=source_path,
            modality=Modality.IMAGE,
            entities=mitigated_entities,
            mitigated_output=mitigated_path,
            artifacts=artifacts,
        )
        self._attach_audit(result)
        return result

    # --- Helpers -------------------------------------------------------
    def _output_path(self, source_path: Path, suffix: str) -> Path:
        base_name = f"{source_path.stem}{suffix}"
        return Path(self.config.app.output_dir) / base_name

    def process_folder(self, folder: Path, recursive: bool = True) -> list[DetectionResult]:
        folder = Path(folder)
        iterator = folder.rglob("*") if recursive else folder.glob("*")
        results: list[DetectionResult] = []
        for path in iterator:
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix in TEXT_EXTENSIONS:
                results.append(self.process_text(path))
            elif suffix in IMAGE_EXTENSIONS:
                try:
                    results.append(self.process_image(path))
                except FileNotFoundError:
                    LOGGER.warning("Skipping unreadable image: %s", path)
        return results

    def _attach_audit(self, result: DetectionResult) -> None:
        if not self.config.explainability.audit_log_path:
            return
        audit_path = record_audit(result, self.config.explainability)
        result.audit_log = audit_path
