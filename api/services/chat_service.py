"""
Chat service for interactive follow-up conversations about analysis reports.

Allows users to ask questions about a completed report, with the LLM
using the full report as context for its answers.
"""

import logging
from src.config import get_llm

logger = logging.getLogger("aegis.services.chat")


def chat_about_report(report: str, company_name: str, question: str) -> str:
    """Answer a follow-up question about a completed analysis report.

    Uses the full report as context and answers the user's question
    with specific references to the report findings.

    Args:
        report: The full Markdown report text from the CRO.
        company_name: The company that was analyzed.
        question: The user's follow-up question.

    Returns:
        The LLM's response as a string.
    """
    try:
        llm = get_llm(temperature=0.3)

        prompt = (
            f"You are an AI assistant for the Aegis Due Diligence system. "
            f"A comprehensive risk assessment has been completed for {company_name}. "
            f"The full report is provided below.\n\n"
            f"--- BEGIN REPORT ---\n{report}\n--- END REPORT ---\n\n"
            f"The user has a follow-up question. Answer it clearly and concisely, "
            f"referencing specific data points from the report when possible. "
            f"If the question is outside the scope of the report, say so.\n\n"
            f"User Question: {question}"
        )

        response = llm.call(prompt)
        logger.info(f"Chat response generated for '{company_name}' ({len(str(response))} chars)")
        return str(response)

    except Exception as e:
        logger.error(f"Chat failed: {e}", exc_info=True)
        return f"Sorry, I encountered an error while processing your question: {str(e)}"
