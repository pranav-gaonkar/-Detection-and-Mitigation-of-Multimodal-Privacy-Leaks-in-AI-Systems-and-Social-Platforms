"""CLI entry point for LeakWatch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .orchestration import PipelineManager
from .utils.config import get_config
from .utils.types import DetectionResult

app = typer.Typer(add_completion=False, help="LeakWatch privacy middleware")


@app.command()
def scan_text(
    path: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Mitigated text path"),
):
    """Scan a text file and emit sanitized output + audit trail."""

    cfg = get_config()
    manager = PipelineManager(cfg)
    result = manager.process_text(path)
    if output and result.mitigated_output:
        contents = Path(result.mitigated_output).read_text(encoding="utf-8")
        output.write_text(contents, encoding="utf-8")
    typer.echo(_to_json(result))


@app.command()
def scan_image(
    path: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to sanitized image"),
):
    """Scan an image file for privacy leaks."""

    cfg = get_config()
    manager = PipelineManager(cfg)
    result = manager.process_image(path, output_path=output)
    typer.echo(_to_json(result))


@app.command()
def scan_folder(
    path: Path = typer.Argument(..., exists=True, resolve_path=True),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive"),
):
    """Scan all supported files inside a folder."""

    cfg = get_config()
    manager = PipelineManager(cfg)
    results = manager.process_folder(path, recursive=recursive)
    typer.echo(json.dumps([r.model_dump() for r in results], indent=2, default=str))


def _to_json(result: DetectionResult) -> str:
    return json.dumps(result.model_dump(), indent=2, default=str)


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
