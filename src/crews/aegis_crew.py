"""Aegis Crew — assembles agents and tasks into a runnable swarm."""

import logging

from crewai import Crew, Task, Process

from src.agents import (
    create_researcher,
    create_financial_analyst,
    create_esg_analyst,
    create_cro,
)
from src.config import get_llm

logger = logging.getLogger("aegis.crew")


def build_aegis_crew(
    company_name: str,
    csv_path: str = "data/financial_data.csv",
    llm=None,
    verbose: bool = True,
) -> Crew:
    """Build the full 4-agent Aegis Due Diligence crew.

    Pipeline: Researcher → Financial Analyst → ESG Analyst → CRO

    Args:
        company_name: Name of the target company to investigate.
        csv_path: Path to the financial data CSV file.
        llm: Optional pre-configured LLM instance. Uses default if None.
        verbose: Whether to enable verbose logging for agents and crew.

    Returns:
        A configured CrewAI Crew ready to kickoff().
    """
    if llm is None:
        llm = get_llm()

    logger.info(f"Building Aegis Crew (4 agents) for '{company_name}'")

    # --- Agents ---
    researcher = create_researcher(llm=llm, verbose=verbose)
    analyst = create_financial_analyst(llm=llm, verbose=verbose)
    esg_analyst = create_esg_analyst(llm=llm, verbose=verbose)
    cro = create_cro(llm=llm, verbose=verbose)

    logger.info("All 4 agents initialized successfully")

    # --- Tasks ---
    task_research = Task(
        description=(
            f"Conduct a comprehensive OSINT investigation on {company_name}. "
            f"Search for: (1) Recent news from the last 6 months, (2) Any pending "
            f"lawsuits or regulatory actions, (3) Executive changes or layoffs, "
            f"(4) Public controversies or scandals. "
            f"For each finding, note the date and source."
        ),
        expected_output=(
            "A structured bulleted list organized by category: "
            "Legal/Regulatory, Financial News, Leadership Changes, Public Controversies. "
            "Each item must include a date and source."
        ),
        agent=researcher,
    )

    task_financial = Task(
        description=(
            f'Use the "Read Financial Data" tool to read the file "{csv_path}". '
            f"Perform a complete financial analysis including: "
            f"(1) Quarter-over-Quarter revenue and cost trends, "
            f"(2) Net Income trajectory — is the company profitable or losing money? "
            f"(3) Debt-to-Revenue ratio progression, "
            f"(4) Cash Reserves runway — at current burn rate, how many quarters until cash runs out? "
            f"(5) R&D investment trend — is the company still investing in growth? "
            f"(6) Employee headcount changes — signs of restructuring? "
            f"Conclude with a clear financial health verdict."
        ),
        expected_output=(
            "A detailed financial analysis with specific numbers and calculations. "
            "Must include: revenue trend %, cost-to-revenue ratio, debt trajectory, "
            "cash runway estimate, and a final verdict of HEALTHY / CAUTION / WARNING / CRITICAL."
        ),
        agent=analyst,
    )

    task_esg = Task(
        description=(
            f"Analyze the ESG (Environmental, Social, Governance) risk profile of {company_name}. "
            f"Using the OSINT research already gathered, investigate:\n"
            f"(1) ENVIRONMENTAL: Any pollution incidents, carbon emission controversies, "
            f"environmental fines, or failure to meet sustainability commitments.\n"
            f"(2) SOCIAL: Workplace safety violations, labor disputes, diversity issues, "
            f"product safety recalls, data breaches, or human rights concerns in supply chain.\n"
            f"(3) GOVERNANCE: Board independence issues, executive pay controversies, "
            f"accounting irregularities, whistleblower reports, or compliance failures.\n"
            f"Assign a severity (LOW/MEDIUM/HIGH/CRITICAL) to each finding "
            f"and provide an overall ESG Risk Score (1-10)."
        ),
        expected_output=(
            "A structured ESG analysis with three sections (Environmental, Social, Governance). "
            "Each section should list findings with severity levels. "
            "Must conclude with an overall ESG Risk Score (1-10) and brief assessment."
        ),
        agent=esg_analyst,
    )

    task_report = Task(
        description=(
            f"You are writing the final Risk Assessment Report for {company_name}. "
            f"Synthesize ALL findings from: (1) the OSINT Researcher, (2) the Financial Analyst, "
            f"and (3) the ESG Analyst into a comprehensive, board-ready report. "
            f"Follow your report template exactly. "
            f"Assign quantitative risk scores (1-10) for each of the THREE categories "
            f"(Public/Legal, Financial, ESG) and provide a clear "
            f"GO / CONDITIONAL / NO-GO recommendation with justification."
        ),
        expected_output=(
            "A professional Markdown report with these sections: "
            "1. Executive Summary, 2. Public Perception & Legal Risk (with score), "
            "3. Financial Health Risk (with score), 4. ESG Risk (with score), "
            "5. Overall Risk Matrix (table with all 3 categories), "
            "6. Final Executive Verdict (GO/CONDITIONAL/NO-GO). "
            "Must be decisive and actionable."
        ),
        agent=cro,
    )

    # --- Crew Assembly ---
    crew = Crew(
        agents=[researcher, analyst, esg_analyst, cro],
        tasks=[task_research, task_financial, task_esg, task_report],
        verbose=verbose,
        process=Process.sequential,
    )

    logger.info("Crew assembled (4 agents, 4 tasks) and ready for kickoff")
    return crew


def run_aegis_analysis(
    company_name: str,
    csv_path: str = "data/financial_data.csv",
    llm=None,
    verbose: bool = True,
) -> dict:
    """Build and run the Aegis crew, returning a structured result.

    This is the main entry point for programmatic access (API, scripts).
    Wraps crew.kickoff() with error handling and structured output.

    Args:
        company_name: Name of the target company.
        csv_path: Path to the financial CSV file.
        llm: Optional pre-configured LLM instance.
        verbose: Whether to enable verbose logging.

    Returns:
        A dict with keys: 'success', 'company', 'report', 'error'.
    """
    try:
        crew = build_aegis_crew(company_name, csv_path, llm, verbose)

        logger.info(f"Kickoff started for '{company_name}'")
        result = crew.kickoff()
        report_text = str(result)

        logger.info(f"Analysis completed for '{company_name}' ({len(report_text)} chars)")
        return {
            "success": True,
            "company": company_name,
            "report": report_text,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Analysis failed for '{company_name}': {e}", exc_info=True)
        return {
            "success": False,
            "company": company_name,
            "report": None,
            "error": str(e),
        }
