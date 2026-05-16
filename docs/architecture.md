# Aegis Architecture

## Overview

ProjectAegis is a **multi-agent AI system** built on [CrewAI](https://www.crewai.com/) that automates corporate due diligence by combining live web intelligence (OSINT) with internal financial data analysis.

## Agent Pipeline

The system uses a **sequential pipeline** of three specialized agents:

```
Input (Company Name + CSV)
        │
        ▼
┌───────────────────────────────┐
│   Agent 1: OSINT Researcher   │
│   ─────────────────────────   │
│   • Uses Serper.dev API       │
│   • Searches live Google      │
│   • Finds news, lawsuits,     │
│     controversies             │
│   Output: Bulleted fact list  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Agent 2: Financial Analyst  │
│   ─────────────────────────   │
│   • Custom Pandas tool        │
│   • Statistical summary       │
│   • Trend analysis (% change) │
│   • Health verdict            │
│   Output: Financial report    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Agent 3: Chief Risk Officer │
│   ─────────────────────────   │
│   • Synthesizes Agent 1 + 2   │
│   • Structured risk report    │
│   • Executive verdict         │
│   Output: Markdown report     │
└───────────────────────────────┘
```

## Key Design Decisions

### Modular Agent Definitions
Each agent is defined in its own file (`src/agents/`) with a factory function that accepts an optional LLM parameter. This allows:
- **Reuse** across CLI and web interfaces
- **Testing** with mock LLMs
- **Easy swapping** of agent configurations

### Centralized Configuration (`src/config.py`)
All environment variable loading and LLM initialization happens in one place, eliminating scattered `load_dotenv()` and `LLM()` calls.

### Custom Pandas Tool (`src/tools/financial_csv.py`)
Instead of dumping raw CSV data to the LLM, the tool performs **automated statistical aggregation**:
1. `df.describe()` for summary statistics
2. First-to-last percentage change for trend detection
3. Most recent row snapshot

This keeps the LLM context window efficient and scalable.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | CrewAI v1.14+ |
| LLM | Google Gemini 2.5 Flash |
| Web Search | Serper.dev API |
| Data Analysis | Pandas |
| Web Interface | Streamlit |
| Language | Python 3.10+ |
