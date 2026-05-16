"""
Pydantic schemas for the Aegis API.

Defines request and response models for all endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ==========================================
# Enums
# ==========================================
class JobStatus(str, Enum):
    """Possible states of an analysis job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ==========================================
# Request Models
# ==========================================
class AnalysisRequest(BaseModel):
    """Request body for starting a new analysis."""
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the target company to investigate.",
        examples=["Boeing", "Tesla", "OpenAI"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Boeing",
            }
        }


# ==========================================
# Response Models
# ==========================================
class JobCreatedResponse(BaseModel):
    """Response after successfully creating an analysis job."""
    job_id: str = Field(..., description="Unique identifier for the analysis job.")
    status: JobStatus = Field(default=JobStatus.PENDING)
    company_name: str
    message: str = Field(default="Analysis job created successfully.")


class JobStatusResponse(BaseModel):
    """Response for job status polling."""
    job_id: str
    status: JobStatus
    company_name: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    progress: str = Field(
        default="Waiting to start...",
        description="Human-readable progress message.",
    )


class AnalysisReportResponse(BaseModel):
    """Response containing the final analysis report."""
    job_id: str
    status: JobStatus
    company_name: str
    report: Optional[str] = Field(
        default=None,
        description="The final Markdown risk assessment report.",
    )
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = Field(
        default=None,
        description="Error message if the analysis failed.",
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
