"""Audit logging helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..utils.config import ExplainabilityConfig
from ..utils.logging import ensure_dir
from ..utils.types import DetectionResult


def record_audit(result: DetectionResult, config: ExplainabilityConfig) -> Path:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modality": result.modality.value,
        "source": str(result.source_path),
        "output": str(result.mitigated_output) if result.mitigated_output else None,
        "artifacts": [str(path) for path in result.artifacts],
        "entity_count": len(result.entities),
        "entities": [
            {
                "label": ent.label,
                "confidence": ent.confidence,
                "text": ent.text,
                "span": ent.span.model_dump() if ent.span else None,
                "bbox": ent.bbox.model_dump() if ent.bbox else None,
                "mitigation": ent.mitigation,
            }
            for ent in result.entities
        ],
    }
    audit_path = Path(config.audit_log_path)
    ensure_dir(audit_path)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
    return audit_path
