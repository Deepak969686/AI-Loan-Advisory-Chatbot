from typing import List
from pydantic import BaseModel, Field


# =====================================================
# Chat Models
# =====================================================

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        description="User's loan-related question"
    )


class Source(BaseModel):
    source: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


# =====================================================
# Upload Models
# =====================================================

class FailedUpload(BaseModel):
    filename: str
    reason: str


class UploadResponse(BaseModel):
    message: str
    uploaded_files: List[str]
    skipped_files: List[str]
    failed_files: List[FailedUpload]
    indexed_chunks: int


class ReindexResponse(BaseModel):
    message: str
    processed_files: int
    indexed_chunks: int


# =====================================================
# EMI Calculator Models
# =====================================================

class EMIRequest(BaseModel):
    principal: float = Field(
        ...,
        gt=0,
        description="Loan Amount"
    )

    annual_interest_rate: float = Field(
        ...,
        ge=0,
        description="Annual Interest Rate"
    )

    tenure_years: int = Field(
        ...,
        gt=0,
        description="Loan Tenure in Years"
    )


class EMIResponse(BaseModel):
    monthly_emi: float
    total_interest: float
    total_payment: float


# =====================================================
# Health Models
# =====================================================

class HealthResponse(BaseModel):
    status: str
    version: str


# =====================================================
# Generic API Response
# =====================================================

class APIResponse(BaseModel):
    success: bool
    message: str