import shutil
from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.config import DOCUMENTS_DIR
from backend.models import (
    ChatRequest,
    ChatResponse,
    UploadResponse,
    EMIRequest,
    EMIResponse,
    HealthResponse,
    ReindexResponse,
)

from backend.pdf_processor import PDFProcessor
from backend.rag import RAGPipeline
from backend.chatbot import LoanChatbot
from backend.loan_utils import LoanUtils


# =====================================================
# FastAPI App
# =====================================================

app = FastAPI(
    title="AI Loan Advisory Agent",
    description="AI-powered Loan Advisory System using Gemini + ChromaDB + RAG",
    version="1.0.0",
)

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# Initialize Services
# =====================================================

pdf_processor = PDFProcessor()

rag_pipeline = RAGPipeline()

chatbot = LoanChatbot(rag_pipeline)

# =====================================================
# Home
# =====================================================

@app.get("/")
def home():

    return {
        "message": "🏦 AI Loan Advisory Agent API Running",
        "version": "1.0.0"
    }


# =====================================================
# Health Check
# =====================================================

@app.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return HealthResponse(
        status="Healthy",
        version="1.0.0"
    )



# =====================================================
# Upload Loan Policy PDFs
# =====================================================

@app.post(
    "/upload",
    response_model=UploadResponse
)
async def upload_documents(
    files: List[UploadFile] = File(...)
):

    uploaded_files = []

    skipped_files = []

    failed_files = []

    indexed_chunks = 0

    for file in files:

        try:

            # -----------------------------
            # Only PDF Allowed
            # -----------------------------

            if not file.filename.lower().endswith(".pdf"):

                failed_files.append(
                    {
                        "filename": file.filename,
                        "reason": "Invalid file type"
                    }
                )

                continue

            save_path = DOCUMENTS_DIR / file.filename

            # -----------------------------
            # Skip Duplicate
            # -----------------------------

            if save_path.exists():

                skipped_files.append(
                    file.filename
                )

                continue

            # -----------------------------
            # Save PDF
            # -----------------------------

            with open(save_path, "wb") as buffer:

                shutil.copyfileobj(
                    file.file,
                    buffer
                )

            # -----------------------------
            # Extract Text
            # -----------------------------

            pages = pdf_processor.extract_text(
                str(save_path)
            )

            # -----------------------------
            # Store in ChromaDB
            # -----------------------------

            chunks = rag_pipeline.add_documents(
                pages
            )

            indexed_chunks += chunks

            uploaded_files.append(
                file.filename
            )

        except Exception as e:

            failed_files.append(
                {
                    "filename": file.filename,
                    "reason": str(e)
                }
            )

    return UploadResponse(
        message="Document processing completed.",
        uploaded_files=uploaded_files,
        skipped_files=skipped_files,
        failed_files=failed_files,
        indexed_chunks=indexed_chunks
    )


# =====================================================
# Rebuild Vector Database
# =====================================================

@app.post(
    "/reindex",
    response_model=ReindexResponse
)
def reindex_documents():

    # Clear old vectors
    rag_pipeline.clear_database()

    pdf_files = list(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    total_chunks = 0

    for pdf_file in pdf_files:

        pages = pdf_processor.extract_text(
            str(pdf_file)
        )

        total_chunks += rag_pipeline.add_documents(
            pages
        )

    return ReindexResponse(
        message="Vector database rebuilt successfully.",
        processed_files=len(pdf_files),
        indexed_chunks=total_chunks
    )


# =====================================================
# List Available Documents
# =====================================================

@app.get("/documents")
def list_documents():

    pdf_files = sorted(
        [pdf.name for pdf in DOCUMENTS_DIR.glob("*.pdf")]
    )

    return {
        "total_documents": len(pdf_files),
        "documents": pdf_files
    }


# =====================================================
# Chat API
# =====================================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    response = chatbot.ask(
        request.question
    )

    return ChatResponse(
        answer=response["answer"],
        sources=response["sources"]
    )


# =====================================================
# EMI Calculator API
# =====================================================

@app.post(
    "/emi",
    response_model=EMIResponse
)
def calculate_emi(request: EMIRequest):

    result = LoanUtils.calculate_emi(
        principal=request.principal,
        annual_interest_rate=request.annual_interest_rate,
        tenure_years=request.tenure_years
    )

    return EMIResponse(
        monthly_emi=result["monthly_emi"],
        total_interest=result["total_interest"],
        total_payment=result["total_payment"]
    )


# =====================================================
# Run Application
# =====================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )