# COPILOT MEMORY

_Last updated: 2026-01-21_

## Mission Snapshot
- **Project**: LeakWatch middleware for the "Detection and Mitigation of Multimodal Privacy Leaks in AI Systems and Social Platforms" capstone.
- **Goal**: Intercept user content (text + images today, audio/video stubs) before it hits AI/social endpoints, detect sensitive data, mitigate it, and produce explainability/audit artifacts.

## Tech Stack & Runtime
- **Language**: Python 3.13 inside `.venv`.
- **Key libs**: spaCy (NER), EasyOCR + OpenCV (image text + faces), Typer (CLI), Pydantic (schemas), pytest.
- **Config**: `config/leakwatch.yaml` drives detector thresholds, mitigation style, artifact paths.

## Major Features
1. **Text Pipeline**
   - Detector combines spaCy NER (PERSON/GPE/ORG/CARDINAL/MONEY) with YAML-driven regex rules (credit cards, phones, emails, etc.).
   - Mitigator replaces spans according to `text.mask_style` (`mask` default, synthetic placeholders optional) while storing original text in `explanation` for audits.
   - Explainability outputs sanitized text + `.spans.txt` report; entries appended to JSONL audit log.

2. **Image Pipeline**
   - Detector uses Haar cascades for faces plus EasyOCR for scene text.
   - Mitigator now blends each sensitive text region with a softened version of the original pixels and redraws **synthetic** phrases (date/phone/name scrubbing heuristics) using sampled text color—no black boxes.
   - Explainability creates sanitized `.png` + overlay highlighting redacted regions and logs every action.

3. **Orchestration & Interfaces**
   - `leakwatch/orchestration/pipeline.py` routes text/image jobs, writes artifacts, and records audits.
   - Typer CLI (`python -m leakwatch`) exposes `scan-text`, `scan-image`, and `scan-folder` commands.
   - FastAPI service (`service/app.py`) wraps the same pipeline with REST endpoints (`/scan/text|image|audio|video`) and policy decisions, plus a download route for serving sanitized artifacts.
   - Outputs land under `artifacts/` with deterministic naming.
4. **Audio/Video Adapters & Graph Context**
   - Placeholder adapters turn audio into transcripts and videos into sparse frames so the hardened text/image pipelines can sanitize them without new models. Demo assets live in `samples/audio/demo_call.wav` (+ transcript) and `samples/video/demo_clip.mp4`, regenerated via `python scripts/generate_demo_media.py`.
   - Graph node/edge schemas capture relationships for future GraphSAGE research while staying dormant (no GNN execution in Phase 2).

## Testing & Verification
- Run `python -m pytest -q` for the automated suite (`tests/test_text_pipeline.py`).
- Manual smoke tests: `python -m leakwatch scan-text samples/text/demo_email.txt` and `scan-image` on `Gemini_Generated_Image_pg2bgppg2bgppg2b.png` (generates sanitized/overlay artifacts).
- Known warning: Pydantic v1 `@validator` deprecation—migrate to `@field_validator` later.

## Operational Notes
- EasyOCR currently runs on CPU; optional GPU acceleration if available.
- Everything logs through `artifacts/audit.log` (JSONL). Rotate/ship log as needed.
- When updating mitigation behavior, also update README + docs and rerun sample scans to refresh artifacts.

## Future Enhancements (Backlog)
1. Broaden regex/entity coverage (bank routing numbers, passports, etc.).
2. Add automated tests for image mitigation overlays.
3. Upgrade to Pydantic v2 validators and tighten type hints.
4. Flesh out adapters for audio/video inputs per Phase 2 scope.

## Conversation Timeline
- **Month 0 – Requirement Intake**
   - Parsed Phase 1 report + LeakWatch HLD PDFs, extracted key acceptance criteria (multimodal detection, explainability, audit logging).
   - Decided on Python stack, CLI-first workflow, and YAML-driven config system to keep detectors pluggable.
- **Month 1 – Repository Scaffold**
   - Initialized `leakwatch/` package with modular folders (`detection`, `mitigation`, `explainability`, `orchestration`, `utils`).
   - Authored README, implementation plan, config templates, and sample datasets to ground future work.
- **Month 2 – Text Pipeline Build**
   - Implemented spaCy-backed NER + regex detector table sourced from config.
   - Added mitigation engine with mask vs synthetic strategies and span reports; wrote pytest to lock behavior.
   - Verified CLI command `scan-text` including audit log entries.
- **Month 3 – Image Pipeline Build**
   - Integrated EasyOCR for scene text and OpenCV Haar cascades for faces; produced bounding boxes for explainability.
   - First mitigation version blurred faces and blacked out text; overlays plus sanitized assets stored under `artifacts/`.
- **Month 4 – Explainability & Orchestration**
   - Centralized pipeline manager orchestrating detection → mitigation → artifact emission for both modalities.
   - Added Typer CLI commands (`scan-image`, `scan-folder`) and JSON output to support automation.
- **Month 5 – Verification & User Feedback**
   - Ran end-to-end demos on provided Gemini image and sample emails; captured CLI output plus artifacts for the report.
   - Documented known warnings (EasyOCR CPU, Pydantic validator deprecation).
- **Month 6 – Mitigation Refinement**
   - Replaced black boxes with synthetic on-canvas rewriting that matches original font color/placement.
   - Updated README and reran `scan-image` to confirm new artifacts and audit trail entries.
- **Month 7 – Text Pipeline Review**
   - Re-demonstrated `scan-text` behavior, confirmed regex-driven replacements, and noted future improvements (persona-preserving rewrites).
- **Month 8 – Repo Handoff & Memory System**
   - Provided Git commands for pushing entire workspace to GitHub target repo.
   - Created `docs/COPILOT_MEMORY.md` and expanded it with this detailed timeline for long-lived context.
- **Month 9 – Phase-2 Alignment Pass**
   - Added audio/video CLI commands and adapters, codified graph data structures as metadata, shipped sample audio/video assets + generator script, and reiterated deterministic mitigation (no GAN/GNN at runtime).
- **Month 10 – Middleware API & Dockerization**
   - Wrapped `PipelineManager` in FastAPI (`service/app.py`), introduced policy-aware responses, documented curl/Docker workflows, added sanitized artifact download endpoint, and created a slim Dockerfile for deployment.

> Reference this file in chat using `#COPILOT_MEMORY.md` to fast-forward Copilot’s context.   
