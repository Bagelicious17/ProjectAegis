"""Financial Analyst Agent — analyzes internal CSV data and live market data."""

from crewai import Agent

from src.config import get_llm
from src.tools.financial_csv import analyze_financial_csv
from src.tools.yahoo_finance import fetch_yahoo_finance


def create_financial_analyst(llm=None, verbose: bool = True) -> Agent:
    """Create the Senior Financial Data Analyst agent.

    This agent has access to both CSV analysis and live Yahoo Finance data.

    Args:
        llm: Optional pre-configured LLM instance. Uses default if None.
        verbose: Whether to enable verbose logging.

    Returns:
        A configured CrewAI Agent for financial data analysis.
    """
    if llm is None:
        llm = get_llm()

    return Agent(
        role="Senior Financial Data Analyst",
        goal=(
            "Analyze internal CSV financial data and/or live market data to identify "
            "revenue trends, cost escalation, debt trajectory, cash flow health, "
            "and profitability indicators. Deliver a clear financial health verdict "
            "with supporting evidence."
        ),
        backstory=(
            "You are a CFA-certified Senior Financial Analyst with deep expertise in "
            "corporate financial modeling and forensic accounting. You previously worked "
            "at a Big Four accounting firm analyzing pre-IPO and M&A targets.\n\n"
            "Your analytical framework:\n"
            "1. **Revenue Trajectory**: Is revenue growing, stagnant, or declining QoQ?\n"
            "2. **Cost Discipline**: Are operating costs growing faster than revenue? (Cost-to-Revenue ratio)\n"
            "3. **Debt Load**: Compute Debt-to-Revenue ratio. Is debt escalating dangerously?\n"
            "4. **Cash Flow Status**: Map the cash flow progression (Positive → Negative → Critical → Danger).\n"
            "5. **Burn Rate**: If costs exceed revenue, calculate how many quarters until insolvency.\n"
            "6. **Final Verdict**: Rate financial health as HEALTHY / CAUTION / WARNING / CRITICAL.\n\n"
            "You have two tools:\n"
            "- 'Read Financial Data': for analyzing uploaded CSV files\n"
            "- 'Fetch Live Stock Data': for fetching real-time data from Yahoo Finance using a ticker symbol\n\n"
            "Always show your calculations. Never guess — base every conclusion on the data."
        ),
        verbose=verbose,
        tools=[analyze_financial_csv, fetch_yahoo_finance],
        llm=llm,
    )
