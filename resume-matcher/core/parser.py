"""Turn an uploaded resume (PDF / DOCX / TXT) into plain text."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _from_pdf(file_bytes)
    if ext == ".docx":
        return _from_docx(file_bytes)
    if ext in {".txt", ".md"}:
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {ext}. Use PDF, DOCX or TXT.")


def _from_pdf(data: bytes) -> str:
    import pdfplumber

    with pdfplumber.open(BytesIO(data)) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def _from_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)
