"""Shared data models for LeakWatch."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Span(BaseModel):
    start: int
    end: int


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class DetectedEntity(BaseModel):
    modality: Modality
    label: str
    confidence: float
    text: str | None = None
    span: Span | None = None
    bbox: BoundingBox | None = None
    mitigation: Literal["mask", "blur", "replace", "none"] = "none"
    explanation: str | None = None


class DetectionResult(BaseModel):
    source_path: Path
    modality: Modality
    entities: list[DetectedEntity] = Field(default_factory=list)
    mitigated_output: Path | None = None
    audit_log: Path | None = None
    artifacts: list[Path] = Field(default_factory=list)
