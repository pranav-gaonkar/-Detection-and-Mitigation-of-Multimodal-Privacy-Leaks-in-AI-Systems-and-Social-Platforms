from pathlib import Path

from leakwatch.orchestration import PipelineManager
from leakwatch.utils.config import (
    AppConfig,
    ExplainabilityConfig,
    ImageConfig,
    LeakWatchConfig,
    RegexEntityConfig,
    TextConfig,
)


def test_text_pipeline_creates_artifacts(tmp_path):
    input_text = "Reach me at 123-456-7890 and email me@sample.com"
    sample = tmp_path / "input.txt"
    sample.write_text(input_text, encoding="utf-8")

    config = LeakWatchConfig(
        app=AppConfig(output_dir=tmp_path / "artifacts"),
        text=TextConfig(
            enable_spacy=False,
            regex_entities=[
                RegexEntityConfig(name="phone", pattern=r"\d{3}-\d{3}-\d{4}", action="mask"),
                RegexEntityConfig(name="email", pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", action="mask"),
            ],
        ),
        image=ImageConfig(enable_ocr=False),
        explainability=ExplainabilityConfig(
            save_text_spans=True,
            save_image_overlays=False,
            audit_log_path=tmp_path / "audit.log",
        ),
    )

    manager = PipelineManager(config)
    result = manager.process_text(sample)

    assert result.mitigated_output is not None
    sanitized_text = Path(result.mitigated_output).read_text(encoding="utf-8")
    assert "[REDACTED" in sanitized_text

    assert result.artifacts, "expected explainability artifact"
    for artifact in result.artifacts:
        assert artifact.exists()

    assert result.audit_log is not None
    assert Path(result.audit_log).exists()