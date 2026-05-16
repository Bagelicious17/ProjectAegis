"""
Background job manager for the Aegis Swarm.

Uses threading to run CrewAI analysis in the background while the API
remains responsive. Jobs are stored in-memory (suitable for hackathon demo).
For production, replace with Redis/Celery/PostgreSQL.
"""

import os
import uuid
import logging
import threading
from datetime import datetime
from typing import Optional

from api.models.schemas import JobStatus

logger = logging.getLogger("aegis.jobs")


class AnalysisJob:
    """Represents a single analysis job with its state and result."""

    def __init__(
        self,
        company_name: str,
        csv_path: Optional[str] = None,
        ticker: Optional[str] = None,
    ):
        self.job_id: str = str(uuid.uuid4())
        self.company_name: str = company_name
        self.csv_path: str = csv_path or "data/financial_data.csv"
        self.ticker: Optional[str] = ticker
        self.status: JobStatus = JobStatus.PENDING
        self.progress: str = "Waiting to start..."
        self.report: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at: datetime = datetime.utcnow()
        self.completed_at: Optional[datetime] = None


class JobManager:
    """Manages background analysis jobs.

    Thread-safe in-memory job store. Each job runs crew.kickoff()
    in a separate thread so the API doesn't block.
    """

    def __init__(self):
        self._jobs: dict[str, AnalysisJob] = {}
        self._lock = threading.Lock()

    def create_job(
        self,
        company_name: str,
        csv_path: Optional[str] = None,
        ticker: Optional[str] = None,
    ) -> AnalysisJob:
        """Create a new analysis job and start it in the background.

        Args:
            company_name: Target company name.
            csv_path: Optional path to the uploaded CSV.
            ticker: Optional stock ticker for live Yahoo Finance data.

        Returns:
            The newly created AnalysisJob.
        """
        job = AnalysisJob(company_name, csv_path, ticker)

        with self._lock:
            self._jobs[job.job_id] = job

        mode = f"ticker={ticker}" if ticker else f"csv={csv_path or 'default'}"
        logger.info(f"Job {job.job_id} created for '{company_name}' ({mode})")

        # Start the analysis in a background thread
        thread = threading.Thread(
            target=self._run_analysis,
            args=(job,),
            daemon=True,
            name=f"aegis-job-{job.job_id[:8]}",
        )
        thread.start()

        return job

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        """Retrieve a job by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self, limit: int = 20) -> list[AnalysisJob]:
        """List recent jobs, newest first."""
        with self._lock:
            jobs = sorted(
                self._jobs.values(),
                key=lambda j: j.created_at,
                reverse=True,
            )
            return jobs[:limit]

    def _run_analysis(self, job: AnalysisJob) -> None:
        """Execute the CrewAI analysis in a background thread.

        Supports both CSV-based and ticker-based (live) analysis.
        Updates the job status/progress as it runs.
        """
        try:
            job.status = JobStatus.RUNNING
            job.progress = "Initializing AI agents..."

            # Import here to avoid circular imports and keep startup fast
            from src.crews import run_aegis_analysis

            if job.ticker:
                job.progress = f"Fetching live data for {job.ticker.upper()} from Yahoo Finance..."
                logger.info(f"Job {job.job_id}: live mode (ticker={job.ticker})")
                # For live analysis, we modify the CSV path instruction
                # The financial analyst agent has the Yahoo Finance tool
                csv_path = f"LIVE_TICKER:{job.ticker}"
            else:
                csv_path = job.csv_path

            job.progress = "Agents deployed — analyzing data (30-90 seconds)..."
            logger.info(f"Job {job.job_id}: kickoff started")

            result = run_aegis_analysis(
                company_name=job.company_name,
                csv_path=csv_path,
                verbose=False,
            )

            if result["success"]:
                job.status = JobStatus.COMPLETED
                job.report = result["report"]
                job.progress = "Analysis complete."
                logger.info(f"Job {job.job_id}: completed successfully")
            else:
                job.status = JobStatus.FAILED
                job.error = result["error"]
                job.progress = f"Analysis failed: {result['error']}"
                logger.error(f"Job {job.job_id}: failed — {result['error']}")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.progress = f"Unexpected error: {e}"
            logger.error(f"Job {job.job_id}: unexpected error", exc_info=True)

        finally:
            job.completed_at = datetime.utcnow()

            # Cleanup temp CSV if it was an upload
            if job.csv_path and "uploads" in job.csv_path:
                try:
                    if os.path.exists(job.csv_path):
                        os.remove(job.csv_path)
                        logger.debug(f"Cleaned up temp file: {job.csv_path}")
                except OSError:
                    pass


# Singleton instance — shared across the FastAPI app
job_manager = JobManager()
