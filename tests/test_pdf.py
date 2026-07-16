from backend.pdf_processor import PDFProcessor

processor = PDFProcessor()

pages = processor.extract_text(
    "documents/HomeLoan.pdf"
)

print("Pages:", len(pages))

print()

print(pages[0])

print()

print(processor.pdf_info(
    "documents/HomeLoan.pdf"
))