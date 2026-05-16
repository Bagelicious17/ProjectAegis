"""
Aegis API — FastAPI Application Server.

Run with:
    uvicorn api.main:app --reload --port 8000

Or:
    python -m api.main
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analysis import router as analysis_router
from src.config import validate_api_keys, setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger("aegis.api")

# ==========================================
# FastAPI App
# ==========================================
app = FastAPI(
    title="Aegis Due Diligence API",
    description=(
        "Autonomous AI-powered corporate due diligence system. "
        "Deploys a swarm of 3 AI agents (OSINT Researcher, Financial Analyst, "
        "Chief Risk Officer) to generate comprehensive risk assessment reports."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ==========================================
# CORS — Allow frontend to connect
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Next.js dev server
        "http://localhost:5173",     # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Routes
# ==========================================
app.include_router(analysis_router)


# ==========================================
# Health Check & Startup
# ==========================================
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "Aegis Due Diligence API",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check with API key validation."""
    keys_valid = validate_api_keys()
    return {
        "status": "healthy" if keys_valid else "degraded",
        "api_keys_configured": keys_valid,
    }


@app.on_event("startup")
async def startup_event():
    """Log startup info and validate configuration."""
    logger.info("=" * 50)
    logger.info("🛡️  Aegis API Server Starting")
    logger.info("=" * 50)

    if not validate_api_keys():
        logger.warning("API keys not configured — analysis requests will fail!")
    else:
        logger.info("All systems operational. Ready for analysis requests.")

    logger.info("API docs available at: http://localhost:8000/docs")


# ==========================================
# Direct execution support
# ==========================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
