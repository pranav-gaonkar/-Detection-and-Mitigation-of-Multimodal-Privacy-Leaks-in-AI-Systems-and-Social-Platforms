"""Utility script to fetch spaCy and EasyOCR assets."""

from __future__ import annotations

import subprocess
import sys

MODELS = [
    ("python", "-m", "spacy", "download", "en_core_web_sm"),
]


def main() -> None:
    for cmd in MODELS:
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    if sys.executable:
        MODELS[0] = (sys.executable, "-m", "spacy", "download", "en_core_web_sm")
    main()
