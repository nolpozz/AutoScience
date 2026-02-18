"""
PDF parsing for AutoScience: extract text and tables from PDFs.
Uses PyPDF2 for text; extend with tabula or pdfplumber for tables if needed.
"""

from pathlib import Path
from typing import Any

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None  # type: ignore


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract raw text from a PDF file.
    :param pdf_path: Path to the PDF.
    :return: Concatenated text from all pages.
    :raises ImportError: If PyPDF2 is not installed.
    :raises FileNotFoundError: If the file does not exist.
    """
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is required for PDF text extraction. Install with: pip install PyPDF2")
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    text_parts = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    return "\n\n".join(text_parts)


def extract_tables_from_pdf(pdf_path: Path) -> list[Any]:
    """
    Extract table-like structures from a PDF.
    Default implementation returns an empty list; override or use a library
    such as tabula-py or pdfplumber for real table extraction.
    :param pdf_path: Path to the PDF.
    :return: List of tables (e.g. list of lists or list of DataFrames).
    """
    # Placeholder: PyPDF2 does not provide table extraction. Projects can add
    # tabula-py or pdfplumber and implement here.
    _ = pdf_path
    return []
