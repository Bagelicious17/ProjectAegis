"""
Centralized configuration for ProjectAegis.

Handles environment variable loading, LLM initialization, and logging
so every module uses a single, consistent setup.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from crewai import LLM

# Fix encoding for Windows terminals
sys.stdout.reconfigure(encoding="utf-8")

# Load .env from project root (works regardless of cwd)
load_dotenv()

# ==========================================
# Logging Configuration
# ==========================================
LOG_FORMAT = "%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the root Aegis logger.

    Args:
        level: Logging level (default: INFO).

    Returns:
        The configured root logger for the Aegis project.
    """
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=level)
    logger = logging.getLogger("aegis")
    logger.setLevel(level)
    return logger


# Create a default logger available at import time
logger = setup_logging()


# ==========================================
# LLM Configuration
# ==========================================
def get_llm(model: str = "gemini/gemini-2.5-flash", temperature: float = 0.2) -> LLM:
    """Create and return a configured LLM instance.

    Args:
        model: The model identifier string.
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).

    Returns:
        A configured CrewAI LLM instance.
    """
    logger.info(f"Initializing LLM: {model} (temperature={temperature})")
    return LLM(model=model, temperature=temperature)


# ==========================================
# Environment Validation
# ==========================================
def validate_api_keys() -> bool:
    """Check that required API keys are present in the environment.

    Returns:
        True if all required keys are set, False otherwise.
    """
    required_keys = ["GEMINI_API_KEY", "SERPER_API_KEY"]
    missing = [key for key in required_keys if not os.environ.get(key)]

    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.error("Copy .env.example to .env and fill in your keys.")
        return False

    logger.info("All API keys validated successfully.")
    return True
