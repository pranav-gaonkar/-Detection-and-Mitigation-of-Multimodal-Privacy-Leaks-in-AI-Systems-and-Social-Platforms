# LeakWatch Capstone Implementation Plan

This document translates the Phase 1 report and Phase 2 high-level design (HLD) into an implementable plan for this repository. The goal is to deliver a proof-of-concept middleware that processes multimodal inputs (text + images for Phase 2 scope) and produces sanitized outputs plus audit artifacts, while leaving lightweight stubs for audio/video extensions.

## Guiding References
- `Team 188_Phase 1_Capstone Report_old.pdf`: defines research motivation, datasets, objectives, and Phase 2 plan.
- `Leak Watch 0 High Level Design (phase 2).pdf`: specifies the architecture diagram and module responsibilities.

## MVP Scope (Phase 2)
1. **Modalities**
   - Fully supported: Text, Image.
   - Partially supported (adapters only): Audio (ASR stub feeding text pipeline), Video (frame extractor feeding image pipeline).
2. **Detection Techniques**
   - Text: Hybrid NER (spaCy) + regex-based detectors + keyword/rule graph to score privacy entities.
   - Image: Haar-cascade face detection + EasyOCR text extraction routed through text detector.
3. **Mitigation Strategies**
   - Text: Configurable masking (full/partial) and synthetic replacement via template library.
   - Image: Gaussian blur for faces, OpenCV inpainting for other ROIs (fallback to mosaic pixelation).
4. **Explainability & Audit**
   - JSONL audit log capturing entities, coordinates, mitigation applied, and confidence.
   - Optional heatmap overlays for images; highlighted spans for text output.
5. **Interfaces**
   - Python package `leakwatch` with orchestration pipeline.
   - CLI entry point (`python -m leakwatch`) to process files/folders.
   - Modular configuration file (`config/leakwatch.yaml`).

## Work Packages
1. **Repository Scaffolding**
   - `pyproject.toml` with dependencies (spacy, easyocr, opencv-python, numpy, pydantic, rich, typer).
   - `leakwatch/` package tree with detection, mitigation, orchestration, explainability, adapters, utils.
   - Tests under `tests/` with pytest fixtures + sample inputs.
2. **Text Pipeline**
   - `TextDetector`: wraps spaCy NER + regex detectors, outputs `DetectedEntity` objects.
   - `TextMitigator`: masking/replacement strategies.
   - `TextExplainer`: highlight spans and produce JSON-friendly metadata.
3. **Image Pipeline**
   - `FaceDetector` (haar cascade) + `SceneTextExtractor` (EasyOCR) + `ImageDetector` aggregator.
   - `ImageMitigator`: blur/inpaint sensitive ROIs.
   - `ImageExplainer`: overlay bounding boxes/heatmaps saved alongside sanitized image.
4. **Orchestration Layer**
   - `PipelineManager` that routes modality-specific processors, merges results, and emits unified schema.
   - CLI via Typer allowing commands: `scan-text`, `scan-image`, `scan-folder`, `serve` (future stub).
5. **Explainability & Audit Module**
   - `audit/logger.py` to append JSONL entries with timestamp + mitigation summary.
   - Hooks in orchestrator to persist `.audit.jsonl` per input.
6. **Docs & Samples**
   - `README.md` with setup instructions, architecture diagrams, usage examples.
   - `docs/ARCHITECTURE.md` elaborating on design choices and future work.
   - `samples/` folder containing demo text and image files.
   - Phase-aligned reporting content summarizing implementation vs plan.
7. **Testing & Validation**
   - Unit tests for detectors/mitigators with synthetic inputs.
   - Snapshot tests ensuring audit schema stability.

## Timeline (suggested)
| Milestone | Components |
|-----------|------------|
| Day 1 | Repo scaffold, dependencies, base package, README skeleton |
| Day 2 | Text detection + mitigation + tests |
| Day 3 | Image detection + mitigation + tests |
| Day 4 | Orchestration + CLI + audit logging |
| Day 5 | Docs polish, demo notebook/script, future-work stubs |

## Risks & Mitigations
- **Heavy dependencies (EasyOCR, spaCy models)**: Provide `scripts/download_models.py` and fallback regex-only mode if models unavailable.
- **OCR accuracy variance**: Keep interface pluggable to swap with PaddleOCR/Tesseract later.
- **Image processing performance**: Use batch resizing and allow configurable detection thresholds.
- **Explainability fidelity**: Augment with textual descriptions in audit log to ensure compliance even if visual overlays fail.

This plan will guide the subsequent tasks in the todo list, ensuring alignment with the provided capstone documentation.
