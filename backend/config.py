from pathlib import Path
from dotenv import load_dotenv
import os

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

# ==========================================
# Project Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

DOCUMENTS_DIR.mkdir(exist_ok=True)
CHROMA_DB_DIR.mkdir(exist_ok=True)

# ==========================================
# Gemini Configuration
# ==========================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please check your .env file."
    )

LLM_MODEL = "models/gemini-3.1-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"

# ==========================================
# ChromaDB
# ==========================================

COLLECTION_NAME = "loan_documents"

# ==========================================
# Text Splitter
# ==========================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ==========================================
# Retrieval
# ==========================================

TOP_K_RESULTS = 5

SEARCH_TYPE = "similarity"