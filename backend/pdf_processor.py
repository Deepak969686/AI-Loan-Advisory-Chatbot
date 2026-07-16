from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF


class PDFProcessor:
    """
    Handles PDF processing:
    - Validate PDF
    - Extract page-wise text
    - Return structured output
    """

    def __init__(self):
        pass

    # ==========================================================
    # Validate PDF
    # ==========================================================

    @staticmethod
    def validate_pdf(pdf_path: str) -> bool:

        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"{pdf_path} does not exist.")

        if pdf_file.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        return True

    # ==========================================================
    # Extract Text
    # ==========================================================

    def extract_text(self, pdf_path: str) -> List[Dict]:

        self.validate_pdf(pdf_path)

        pages = []

        document = fitz.open(pdf_path)

        filename = Path(pdf_path).name

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text")

            if not text:
                continue

            text = self.clean_text(text)

            if len(text.strip()) == 0:
                continue

            pages.append(
                {
                    "source": filename,
                    "page": page_number,
                    "text": text
                }
            )

        document.close()

        return pages

    # ==========================================================
    # Clean Extracted Text
    # ==========================================================

    @staticmethod
    def clean_text(text: str) -> str:

        text = text.replace("\n", " ")

        text = text.replace("\t", " ")

        text = " ".join(text.split())

        return text

    # ==========================================================
    # Number of Pages
    # ==========================================================

    @staticmethod
    def total_pages(pdf_path: str) -> int:

        PDFProcessor.validate_pdf(pdf_path)

        document = fitz.open(pdf_path)

        pages = len(document)

        document.close()

        return pages

    # ==========================================================
    # PDF Information
    # ==========================================================

    @staticmethod
    def pdf_info(pdf_path: str):

        PDFProcessor.validate_pdf(pdf_path)

        document = fitz.open(pdf_path)

        info = {
            "filename": Path(pdf_path).name,
            "pages": len(document),
            "title": document.metadata.get("title"),
            "author": document.metadata.get("author"),
            "subject": document.metadata.get("subject"),
            "creator": document.metadata.get("creator"),
        }

        document.close()

        return info

    # ==========================================================
    # Process Multiple PDFs
    # ==========================================================

    def process_multiple_pdfs(
        self,
        pdf_paths: List[str]
    ) -> List[Dict]:

        all_pages = []

        for pdf in pdf_paths:

            pages = self.extract_text(pdf)

            all_pages.extend(pages)

        return all_pages