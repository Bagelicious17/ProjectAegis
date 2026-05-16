"""Agent factory functions for the Aegis Swarm."""

from src.agents.researcher import create_researcher
from src.agents.financial_analyst import create_financial_analyst
from src.agents.esg_analyst import create_esg_analyst
from src.agents.cro import create_cro

__all__ = [
    "create_researcher",
    "create_financial_analyst",
    "create_esg_analyst",
    "create_cro",
]
