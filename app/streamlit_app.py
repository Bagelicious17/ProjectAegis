"""
Aegis Due Diligence — Streamlit Web Application.

Run with:
    streamlit run app/streamlit_app.py
"""

import os
import sys
import tempfile

import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_llm
from src.crews import build_aegis_crew

# ==========================================
# 1. PAGE SETUP & UI
# ==========================================
st.set_page_config(page_title="Aegis Due Diligence", page_icon="🛡️", layout="wide")

st.title("🛡️ Aegis: Autonomous Due Diligence Swarm")
st.markdown(
    "Enter a company name and upload their internal financial CSV. "
    "The Aegis Swarm will deploy 3 AI agents to analyze web data, "
    "financial health, and synthesize a final Risk Report."
)

# Sidebar for API Keys
with st.sidebar:
    st.header("🔑 API Credentials")
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
    )
    serper_key = st.text_input(
        "Serper API Key",
        type="password",
        value=os.environ.get("SERPER_API_KEY", ""),
    )
    st.info("Aegis uses Gemini 2.5 Flash and Serper.dev for live OSINT research.")

# ==========================================
# 2. USER INPUTS
# ==========================================
col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input(
        "Target Company Name", placeholder="e.g., Boeing, OpenAI, Tesla"
    )

with col2:
    uploaded_file = st.file_uploader("Upload Internal Financials (CSV)", type=["csv"])

# ==========================================
# 3. THE CREW AI LOGIC
# ==========================================
if st.button("🚀 Deploy Aegis Swarm"):
    if not company_name:
        st.error("Please enter a company name.")
    elif not uploaded_file:
        st.error("Please upload a CSV file.")
    elif not gemini_key or not serper_key:
        st.error("Please enter both API keys in the sidebar.")
    else:
        # Inject keys into environment for this session
        os.environ["GEMINI_API_KEY"] = gemini_key
        os.environ["SERPER_API_KEY"] = serper_key

        # Save uploaded CSV to a temp file
        temp_csv_path = os.path.join("data", "uploads", "temp_financial_data.csv")
        os.makedirs(os.path.dirname(temp_csv_path), exist_ok=True)
        with open(temp_csv_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.status("🤖 Initializing AI Agent Swarm...", expanded=True) as status:
            st.write("🧠 Booting up Gemini 2.5 Flash...")
            llm = get_llm()

            st.write("🕵️‍♂️ Deploying OSINT Researcher...")
            st.write("📊 Deploying Financial Data Analyst...")
            st.write("⚖️ Deploying Chief Risk Officer...")

            crew = build_aegis_crew(
                company_name=company_name,
                csv_path=temp_csv_path,
                llm=llm,
                verbose=False,  # Keep web UI clean
            )

            st.write("⚙️ Swarm is actively analyzing data. Please wait (30-60 seconds)...")
            result_output = crew.kickoff()
            final_report = str(result_output)

            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

        # ==========================================
        # 4. DISPLAY THE RESULTS
        # ==========================================
        st.success(f"Final Report Generated for {company_name}")

        with st.container(border=True):
            st.markdown(final_report)

        # Cleanup temp file
        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)
