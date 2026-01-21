from pathlib import Path
from pypdf import PdfReader

PDF_FILES = [
    Path("Leak Watch – High Level Design (phase 2).pdf"),
    Path("Team 188_Phase 1_Capstone Report_old.pdf"),
]

for pdf_path in PDF_FILES:
    if not pdf_path.exists():
        print(f"Skipping missing file: {pdf_path}")
        continue

    reader = PdfReader(pdf_path)
    text_chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text_chunks.append(text.strip())
        print(f"Read page {page_number} from {pdf_path.name}")

    output_path = pdf_path.with_suffix(".txt")
    output_path.write_text("\n\n".join(text_chunks), encoding="utf-8")
    print(f"Wrote text to {output_path}")
