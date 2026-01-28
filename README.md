# LeakWatch Middleware

LeakWatch is a privacy-preserving middleware designed during the UE23CS320A Capstone project to detect and mitigate multimodal privacy leaks **before** user content reaches downstream AI systems or social platforms. This repository implements the Phase 2 scope described in the project PDFs: full support for text + image modalities, adapters for audio/video, explainability artifacts, and an orchestration API/CLI layer.

## Features (Phase 2 Scope)
- Text privacy detection via spaCy NER, regex heuristics, and rule graphs.
- Text mitigation strategies (masking, redaction, synthetic replacements) with audit trails.
- Image privacy detection using OpenCV Haar cascades (faces) and OCR-assisted text scanning.
- Image mitigation via facial blur plus on-canvas synthetic text rewrites that preserve document styling with explainability overlays.
- Audio/video adapters that route through speech-to-text or frame sampling stubs so we can reuse the hardened text/image pipelines without extra model training.
- Graph context data structures ready for future GraphSAGE experimentation (Phase 2 keeps them as declarative metadata only).
- Unified pipeline manager with Typer-based CLI for scanning files/folders.
- Configurable YAML settings, JSON audit logs, and sample datasets for quick demos.

## Repository Layout
```
leakwatch/
  detection/         # modality detectors (text, image)
  mitigation/        # mitigation strategies per modality
  explainability/    # highlighting + audit artifacts
  orchestration/     # pipeline manager + CLI wiring
  adapters/          # audio/video stubs + integrations
  utils/             # shared helpers (config, logging, schema)
config/
  leakwatch.yaml     # default runtime configuration
samples/
  text/              # demo text inputs
  images/            # demo image inputs
scripts/
  extract_pdf_text.py
  download_models.py # (to be added) fetch spaCy/ocr assets
tests/
  ...                # pytest suite
```

## Getting Started
1. **Install dependencies**
   ```powershell
   D:/Capstone/.venv/Scripts/python.exe -m pip install -U pip
   D:/Capstone/.venv/Scripts/python.exe -m pip install -r requirements.txt
   ```
2. **Download NLP/OCR models** (after `pip install`):
   ```powershell
   D:/Capstone/.venv/Scripts/python.exe -m spacy download en_core_web_sm
   ```
3. **Run the CLI**
   ```powershell
   D:/Capstone/.venv/Scripts/python.exe -m leakwatch scan-text samples/text/demo_email.txt
   ```
  Other useful commands:
  ```powershell
  # Scan an image
  D:/Capstone/.venv/Scripts/python.exe -m leakwatch scan-image path/to/photo.jpg

  # Scan audio (expects a sibling .txt transcript; toggled via config.audio.enabled)
  D:/Capstone/.venv/Scripts/python.exe -m leakwatch scan-audio path/to/recording.wav

  # Scan video (extracts sparse frames and sanitizes them via the image pipeline)
  D:/Capstone/.venv/Scripts/python.exe -m leakwatch scan-video path/to/clip.mp4

  # Recursively scan a folder (text + images)
  D:/Capstone/.venv/Scripts/python.exe -m leakwatch scan-folder data/uploads
  ```

### Sample Media Assets
- Audio: `samples/audio/demo_call.wav` (plus transcript) demonstrates the `scan-audio` flow; regenerate via `python scripts/generate_demo_media.py` if needed.
- Video: `samples/video/demo_clip.mp4` contains synthetic frames with visible text, ideal for `scan-video` walkthroughs.

## Phase-2 Alignment
- **Detectors**: spaCy + regex for text, Haar/YOLO-compatible faces + EasyOCR for images, optional audio/video wrappers that reuse those flows.
- **Mitigation**: Fully deterministic (masking, replacements, blurs). No GAN training; future GAN inpainting may be added as an optional demo only.
- **Graphs / GNN**: Token/region graphs are captured as metadata to support future GraphSAGE research, but no GNN is executed in this release.
- **Explainability**: Text span reports, bounding-box overlays, JSON audit log documenting what/why/how for every mitigation event.
- **Demo readiness**: `scan-text`, `scan-image`, and sample runs in `samples/` provide an end-to-end story without requiring GPUs or large datasets.

## Explainability & Audit Artifacts
- **Sanitized output**: written to `artifacts/<name>.sanitized.<ext>`.
- **Text span report** (`.spans.txt`): lists each detected entity with original vs sanitized snippets.
- **Image overlay** (`.overlay.png`): draws bounding boxes for redacted regions.
- **Audit log** (`artifacts/audit.log`): JSONL log capturing modality, entities, mitigations, and artifact paths.

## Testing
Run the automated tests with pytest:
```powershell
D:/Capstone/.venv/Scripts/python.exe -m pytest -q
```

## Documentation
- `docs/IMPLEMENTATION_PLAN.md`: bridge between Phase 1 report and this implementation.
- Additional docs (`ARCHITECTURE.md`, pipeline diagrams, etc.) will be added as modules are completed.

## Status
Project is under active development. Remaining stretch goals include richer regex coverage, image test automation, audio/video UX polish, and (future) GraphSAGE/GAN experiments once the deterministic baseline is fully signed off.
