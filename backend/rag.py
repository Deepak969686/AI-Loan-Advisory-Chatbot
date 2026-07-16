from typing import List, Dict, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from backend.config import (
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    SEARCH_TYPE,
)


class RAGPipeline:
    """
    Loan Advisory RAG Pipeline

    Responsibilities
    ----------------
    • Convert PDF pages into chunks
    • Generate Gemini Embeddings
    • Store vectors in ChromaDB
    • Retrieve relevant chunks
    • Build context for Gemini
    """

    def __init__(self):

        # ---------------------------------------
        # Gemini Embedding Model
        # ---------------------------------------

        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )

        # ---------------------------------------
        # Text Splitter
        # ---------------------------------------

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "? ",
                "! ",
                "; ",
                ", ",
                " ",
                ""
            ]
        )

        # ---------------------------------------
        # ChromaDB
        # ---------------------------------------

        self.vector_db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding_model,
            persist_directory=str(CHROMA_DB_DIR)
        )

        # ---------------------------------------
        # Retriever
        # ---------------------------------------

        self.retriever = self.vector_db.as_retriever(
            search_type=SEARCH_TYPE,
            search_kwargs={
                "k": TOP_K_RESULTS
            }
        )


    # =====================================================
    # Convert Extracted Pages into LangChain Documents
    # =====================================================

    def create_documents(
        self,
        pages: List[Dict]
    ) -> Tuple[List[Document], List[str]]:
        """
        Convert extracted PDF pages into LangChain Documents.

        Returns
        -------
        documents : List[Document]
        ids : List[str]
        """

        documents = []
        ids = []

        for page in pages:

            chunks = self.text_splitter.split_text(
                page["text"]
            )

            for chunk_index, chunk in enumerate(chunks):

                document_id = (
                    f"{page['source']}"
                    f"_page_{page['page']}"
                    f"_chunk_{chunk_index}"
                )

                ids.append(document_id)

                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "id": document_id,
                            "source": page["source"],
                            "page": page["page"],
                            "chunk": chunk_index
                        }
                    )
                )

        return documents, ids

    # =====================================================
    # Store Documents into ChromaDB
    # =====================================================

    def add_documents(
        self,
        pages: List[Dict]
    ) -> int:
        """
        Index extracted pages into ChromaDB.

        Returns
        -------
        int
            Number of newly indexed chunks.
        """

        documents, ids = self.create_documents(pages)

        # Existing IDs already stored
        existing = self.vector_db.get()

        existing_ids = set(existing.get("ids", []))

        new_documents = []
        new_ids = []

        for doc, doc_id in zip(documents, ids):

            if doc_id not in existing_ids:

                new_documents.append(doc)
                new_ids.append(doc_id)

        if new_documents:

            self.vector_db.add_documents(
                documents=new_documents,
                ids=new_ids
            )

        return len(new_documents)

    # =====================================================
    # Index Multiple PDFs
    # =====================================================

    def index_documents(
        self,
        pdf_pages: List[List[Dict]]
    ) -> int:
        """
        Index multiple PDFs.

        Parameters
        ----------
        pdf_pages :
            List containing extracted pages
            from multiple PDFs.

        Returns
        -------
        int
            Total indexed chunks.
        """

        total_chunks = 0

        for pages in pdf_pages:

            total_chunks += self.add_documents(
                pages
            )

        return total_chunks
    


    # =====================================================
    # Retrieve Relevant Documents
    # =====================================================

    def retrieve(self, query: str):
        """
        Retrieve the most relevant documents
        for the given user query.
        """

        return self.retriever.invoke(query)

    # =====================================================
    # Build Context for Gemini
    # =====================================================

    def build_context(
        self,
        documents: List[Document]
    ) -> Tuple[str, List[Dict]]:
        """
        Convert retrieved documents into
        context + source metadata.
        """

        context_parts = []

        sources = []

        seen = set()

        for doc in documents:

            context_parts.append(doc.page_content)

            key = (
                doc.metadata["source"],
                doc.metadata["page"]
            )

            if key not in seen:

                seen.add(key)

                sources.append(
                    {
                        "source": doc.metadata["source"],
                        "page": doc.metadata["page"]
                    }
                )

        context = "\n\n".join(context_parts)

        return context, sources

    # =====================================================
    # Search Pipeline
    # =====================================================

    def search(self, query: str) -> Dict:
        """
        Complete RAG retrieval pipeline.
        """

        retrieved_docs = self.retrieve(query)

        context, sources = self.build_context(
            retrieved_docs
        )

        return {
            "context": context,
            "sources": sources
        }

    # =====================================================
    # Collection Statistics
    # =====================================================

    def count_documents(self) -> int:
        """
        Return total indexed chunks.
        """

        try:

            return self.vector_db._collection.count()

        except Exception:

            return 0

    # =====================================================
    # Clear Vector Database
    # =====================================================

    def clear_database(self):
        """
        Remove every indexed document.
        Useful during development.
        """

        try:

            self.vector_db.delete_collection()

        except Exception:

            pass

        self.vector_db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding_model,
            persist_directory=str(CHROMA_DB_DIR)
        )

        self.retriever = self.vector_db.as_retriever(
            search_type=SEARCH_TYPE,
            search_kwargs={
                "k": TOP_K_RESULTS
            }
        )