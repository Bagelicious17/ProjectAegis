"""
Analysis API routes.

Endpoints:
    POST /api/analyze              — Start analysis with default sample data
    POST /api/analyze/upload       — Start analysis with uploaded CSV
    POST /api/analyze/live         — Start analysis with live Yahoo Finance data
    POST /api/analyze/compare      — Compare multiple companies
    GET  /api/jobs/{job_id}        — Get job status
    GET  /api/report/{job_id}      — Get the final report
    GET  /api/report/{job_id}/pdf  — Download PDF report
    POST /api/chat/{job_id}        — Ask follow-up questions
    GET  /api/jobs                 — List all jobs
"""

import os
import uuid
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel, Field

from api.models.schemas import (
    AnalysisRequest,
    JobCreatedResponse,
    JobStatusResponse,
    AnalysisReportResponse,
    JobStatus,
)
from api.services.job_manager import job_manager

logger = logging.getLogger("aegis.api.routes")

router = APIRouter(prefix="/api", tags=["Analysis"])


# ==========================================
# Additional Request Models
# ==========================================
class LiveAnalysisRequest(BaseModel):
    """Request for analysis using live Yahoo Finance data."""
    company_name: str = Field(..., min_length=1, max_length=200)
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol (e.g., BA, TSLA, AAPL)",
    )


class CompareRequest(BaseModel):
    """Request for comparative multi-company analysis."""
    companies: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of company names to compare (2-5 companies)",
    )


class ChatRequest(BaseModel):
    """Request for follow-up chat about a report."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Follow-up question about the analysis report",
    )


class ChatResponse(BaseModel):
    """Response from the follow-up chat."""
    job_id: str
    company_name: str
    question: str
    answer: str


class CompareJobsResponse(BaseModel):
    """Response for comparative analysis job creation."""
    jobs: list[JobCreatedResponse]
    message: str


# ==========================================
# POST /api/analyze — Start analysis (default CSV)
# ==========================================
@router.post("/analyze", response_model=JobCreatedResponse)
async def start_analysis(request: AnalysisRequest):
    """Start a new due diligence analysis using the default sample data.

    The analysis runs in the background. Use the returned job_id
    to poll for status and retrieve the final report.
    """
    logger.info(f"New analysis requested for '{request.company_name}'")

    job = job_manager.create_job(
        company_name=request.company_name,
        csv_path="data/financial_data.csv",
    )

    return JobCreatedResponse(
        job_id=job.job_id,
        status=job.status,
        company_name=job.company_name,
    )


# ==========================================
# POST /api/analyze/upload — Start analysis with CSV upload
# ==========================================
@router.post("/analyze/upload", response_model=JobCreatedResponse)
async def start_analysis_with_upload(
    company_name: str = Form(..., description="Target company name"),
    file: UploadFile = File(..., description="Financial data CSV file"),
):
    """Start a new analysis with an uploaded CSV file.

    The CSV is saved to a unique temp path to prevent multi-user conflicts.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    # Save to unique path (prevents multi-user overwrites)
    upload_dir = os.path.join("data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    csv_path = os.path.join(upload_dir, unique_filename)

    try:
        contents = await file.read()
        with open(csv_path, "wb") as f:
            f.write(contents)
        logger.info(f"Uploaded CSV saved: {csv_path} ({len(contents)} bytes)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    job = job_manager.create_job(company_name=company_name, csv_path=csv_path)

    return JobCreatedResponse(
        job_id=job.job_id,
        status=job.status,
        company_name=company_name,
    )


# ==========================================
# POST /api/analyze/live — Start analysis with Yahoo Finance
# ==========================================
@router.post("/analyze/live", response_model=JobCreatedResponse, tags=["Live Data"])
async def start_live_analysis(request: LiveAnalysisRequest):
    """Start analysis using live data from Yahoo Finance.

    No CSV upload needed — financial data is fetched in real-time
    using the provided stock ticker symbol.
    """
    logger.info(f"Live analysis requested for '{request.company_name}' (ticker: {request.ticker})")

    job = job_manager.create_job(
        company_name=request.company_name,
        csv_path=None,
        ticker=request.ticker,
    )

    return JobCreatedResponse(
        job_id=job.job_id,
        status=job.status,
        company_name=request.company_name,
        message=f"Live analysis started with Yahoo Finance data for {request.ticker.upper()}",
    )


# ==========================================
# POST /api/analyze/compare — Compare multiple companies
# ==========================================
@router.post("/analyze/compare", response_model=CompareJobsResponse, tags=["Comparison"])
async def start_comparative_analysis(request: CompareRequest):
    """Start parallel analysis for multiple companies for side-by-side comparison.

    Creates a separate analysis job for each company. Poll each job_id
    individually for status, then compare the results.
    """
    logger.info(f"Comparative analysis requested for: {request.companies}")

    created_jobs = []
    for company in request.companies:
        job = job_manager.create_job(
            company_name=company,
            csv_path="data/financial_data.csv",
        )
        created_jobs.append(
            JobCreatedResponse(
                job_id=job.job_id,
                status=job.status,
                company_name=company,
            )
        )

    return CompareJobsResponse(
        jobs=created_jobs,
        message=f"Started {len(created_jobs)} parallel analyses for comparison.",
    )


# ==========================================
# GET /api/jobs/{job_id} — Poll job status
# ==========================================
@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Check the current status and progress of an analysis job."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        company_name=job.company_name,
        created_at=job.created_at,
        completed_at=job.completed_at,
        progress=job.progress,
    )


# ==========================================
# GET /api/report/{job_id} — Get final report
# ==========================================
@router.get("/report/{job_id}", response_model=AnalysisReportResponse)
async def get_report(job_id: str):
    """Retrieve the final analysis report for a completed job."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    if job.status in (JobStatus.PENDING, JobStatus.RUNNING):
        raise HTTPException(
            status_code=202,
            detail=f"Analysis still in progress: {job.progress}",
        )

    return AnalysisReportResponse(
        job_id=job.job_id,
        status=job.status,
        company_name=job.company_name,
        report=job.report,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error=job.error,
    )


# ==========================================
# GET /api/report/{job_id}/pdf — Download PDF report
# ==========================================
@router.get("/report/{job_id}/pdf", tags=["Export"])
async def download_pdf_report(job_id: str):
    """Download the analysis report as a professional PDF document."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    if job.status != JobStatus.COMPLETED or not job.report:
        raise HTTPException(
            status_code=400,
            detail="Report not ready. Wait for analysis to complete.",
        )

    try:
        from api.services.pdf_generator import generate_pdf_report

        pdf_bytes = generate_pdf_report(
            company_name=job.company_name,
            report_markdown=job.report,
        )

        filename = f"Aegis_Report_{job.company_name.replace(' ', '_')}_{job.job_id[:8]}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires 'reportlab'. Install with: pip install reportlab",
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ==========================================
# POST /api/chat/{job_id} — Follow-up chat
# ==========================================
@router.post("/chat/{job_id}", response_model=ChatResponse, tags=["Chat"])
async def chat_about_analysis(job_id: str, request: ChatRequest):
    """Ask a follow-up question about a completed analysis report.

    The AI uses the full report as context to answer your question
    with specific references to the findings.
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    if job.status != JobStatus.COMPLETED or not job.report:
        raise HTTPException(
            status_code=400,
            detail="Analysis must be completed before chatting. Check job status.",
        )

    from api.services.chat_service import chat_about_report

    answer = chat_about_report(
        report=job.report,
        company_name=job.company_name,
        question=request.question,
    )

    return ChatResponse(
        job_id=job_id,
        company_name=job.company_name,
        question=request.question,
        answer=answer,
    )


# ==========================================
# GET /api/jobs — List all jobs
# ==========================================
@router.get("/jobs", response_model=list[JobStatusResponse])
async def list_jobs(limit: int = 20):
    """List recent analysis jobs, newest first."""
    jobs = job_manager.list_jobs(limit=limit)

    return [
        JobStatusResponse(
            job_id=j.job_id,
            status=j.status,
            company_name=j.company_name,
            created_at=j.created_at,
            completed_at=j.completed_at,
            progress=j.progress,
        )
        for j in jobs
    ]
