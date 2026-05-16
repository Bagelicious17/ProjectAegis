"""OSINT Researcher Agent — searches the web for company intelligence."""

from crewai import Agent
from crewai_tools import SerperDevTool

from src.config import get_llm


def create_researcher(llm=None, verbose: bool = True) -> Agent:
    """Create the Corporate OSINT Researcher agent.

    Args:
        llm: Optional pre-configured LLM instance. Uses default if None.
        verbose: Whether to enable verbose logging.

    Returns:
        A configured CrewAI Agent for web research.
    """
    if llm is None:
        llm = get_llm()

    return Agent(
        role="Corporate OSINT Researcher",
        goal=(
            "Search the web to uncover recent news, legal proceedings, regulatory actions, "
            "executive changes, and public controversies about a target company. "
            "Prioritize information from the last 6 months."
        ),
        backstory=(
            "You are an elite Open Source Intelligence (OSINT) analyst with 15 years of "
            "experience in corporate investigations. You previously worked for a top-tier "
            "management consulting firm conducting pre-acquisition due diligence. "
            "Your methodology:\n"
            "1. Search for recent lawsuits, SEC filings, and regulatory penalties.\n"
            "2. Identify executive departures, layoffs, or restructuring signals.\n"
            "3. Look for negative press coverage, whistleblower reports, or ESG controversies.\n"
            "4. Cross-reference multiple sources before reporting any claim.\n"
            "5. Always note the date and source of each finding.\n\n"
            "You NEVER fabricate information. If you cannot find data, you say so explicitly."
        ),
        verbose=verbose,
        tools=[SerperDevTool()],
        llm=llm,
    )
