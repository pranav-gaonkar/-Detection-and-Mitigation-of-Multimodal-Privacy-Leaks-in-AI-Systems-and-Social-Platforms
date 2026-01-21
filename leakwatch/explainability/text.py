"""Explainability helpers for text modality."""

from __future__ import annotations

from pathlib import Path

from ..utils.logging import ensure_dir
from ..utils.types import DetectedEntity


def render_text_spans(
    sanitized_text: str,
    entities: list[DetectedEntity],
    output_path: Path,
) -> Path:
    """Create a human-readable report summarizing sensitive spans."""

    ensure_dir(output_path)
    if not entities:
        output_path.write_text("No sensitive spans detected.", encoding="utf-8")
        return output_path

    lines: list[str] = ["Detected sensitive spans:", ""]
    sorted_entities = sorted(
        (ent for ent in entities if ent.span),
        key=lambda ent: ent.span.start if ent.span else 0,
    )
    for entity in sorted_entities:
        span = entity.span
        if not span:
            continue
        sanitized_snippet = sanitized_text[span.start : span.end]
        original_snippet = entity.explanation or sanitized_snippet
        lines.append(
            f"- {entity.label} | mitigation={entity.mitigation} | span=({span.start}, {span.end})"
        )
        lines.append(f"  original : {original_snippet}")
        lines.append(f"  sanitized: {sanitized_snippet}")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
