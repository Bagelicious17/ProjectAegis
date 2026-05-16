# 🛡️ ProjectAegis

**Autonomous Due Diligence Swarm** — A multi-agent AI system that performs comprehensive company risk assessment using live web intelligence and internal financial data analysis.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/framework-CrewAI-purple.svg)](https://www.crewai.com/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## 🏗️ Architecture

Aegis deploys a **3-agent swarm** in sequential pipeline:

```
┌─────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│  🕵️ OSINT Researcher │ ──▶ │  📊 Financial Analyst     │ ──▶ │  ⚖️ Chief Risk Officer │
│  (Live Web Search)  │     │  (CSV Data + Pandas)     │     │  (Final Report)      │
└─────────────────────┘     └──────────────────────────┘     └──────────────────────┘
```

| Agent | Role | Tools |
|-------|------|-------|
| **OSINT Researcher** | Searches live web for recent news, lawsuits, controversies | Serper.dev (Google Search) |
| **Financial Analyst** | Reads and analyzes uploaded CSV financial data | Custom Pandas Tool |
| **Chief Risk Officer** | Synthesizes both inputs into a scored Risk Report | — |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/ProjectAegis.git
cd ProjectAegis
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
copy .env.example .env
# Edit .env and fill in your keys
```

| Key | Source |
|-----|--------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `SERPER_API_KEY` | [Serper.dev](https://serper.dev) |

### 3. Run

**API Server (for custom frontend):**
```bash
uvicorn api.main:app --reload --port 8000
# API docs at: http://localhost:8000/docs
```

**CLI Mode:**
```bash
python scripts/run_cli.py
```

**Streamlit UI (fallback):**
```bash
streamlit run app/streamlit_app.py
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Detailed health + API key validation |
| `POST` | `/api/analyze` | Start analysis (default sample data) |
| `POST` | `/api/analyze/upload` | Start analysis with CSV upload |
| `GET` | `/api/jobs/{job_id}` | Poll job status & progress |
| `GET` | `/api/report/{job_id}` | Get final report (after completion) |
| `GET` | `/api/jobs` | List recent analysis jobs |

Interactive API documentation: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
ProjectAegis/
├── .env.example                 # Environment variable template
├── requirements.txt             # Pinned dependencies
├── README.md                    # This file
│
├── src/                         # Core source code
│   ├── config.py                # Centralized LLM & env config + logging
│   ├── agents/                  # Agent definitions
│   │   ├── researcher.py        # OSINT Researcher (15yr OSINT analyst)
│   │   ├── financial_analyst.py # Financial Data Analyst (CFA-certified)
│   │   └── cro.py               # Chief Risk Officer (FRM/CISA certified)
│   ├── tools/                   # Custom CrewAI tools
│   │   └── financial_csv.py     # Pandas-based CSV analyzer
│   └── crews/                   # Crew assembly
│       └── aegis_crew.py        # Crew factory + run_aegis_analysis()
│
├── api/                         # FastAPI REST backend
│   ├── main.py                  # App factory + CORS + startup
│   ├── routes/
│   │   └── analysis.py          # /api/analyze, /api/jobs, /api/report
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   └── services/
│       └── job_manager.py       # Background thread job runner
│
├── app/                         # Streamlit web interface (fallback)
│   └── streamlit_app.py
│
├── scripts/                     # CLI entrypoints & utilities
│   └── run_cli.py
│
├── data/                        # Sample data & temp uploads
│   └── financial_data.csv       # 8 quarters × 10 financial metrics
│
├── tests/                       # Unit & integration tests
│   └── test_tools.py
│
└── docs/                        # Extended documentation
    └── architecture.md
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 📊 Sample Data Format

Your CSV should contain quarterly financial metrics:

| Quarter | Revenue_Millions | Operating_Costs_Millions | Net_Income_Millions | EBITDA_Millions | Debt_Millions | Cash_Reserves_Millions | RnD_Spend_Millions | Employee_Count | Cash_Flow_Status |
|---------|-----------------|------------------------|--------------------|-----------------|--------------|-----------------------|-------------------|---------------|-----------------|
| Q1_2023 | 1250 | 900 | 280 | 350 | 450 | 620 | 85 | 32000 | Positive |

---

## 📜 License

This project is for educational and research purposes.