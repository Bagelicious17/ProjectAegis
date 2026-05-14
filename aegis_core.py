import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool
from crewai.tools import tool # This lets us build custom tools!

from dotenv import load_dotenv

# 1. API Keys
load_dotenv()

# 2. Initialize Brain
llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.2
)

# ==========================================
# 3. DEFINE THE TOOLS
# ==========================================
search_tool = SerperDevTool()

# YOUR DATA SCIENCE FLEX: A Custom Pandas Tool
@tool("Read Financial Data")
def analyze_financial_csv(file_path: str) -> str:
    """Reads a CSV file containing financial data and returns a statistical summary and trend analysis."""
    try:
        df = pd.read_csv(file_path)
        
        # Let Pandas do the heavy lifting: Summary Statistics
        summary = df.describe().to_string()
        
        # Compute overall trend (percentage change from first to last period)
        numeric_cols = df.select_dtypes(include=['number']).columns
        trends = "Overall Changes (First to Last Row):\n"
        for col in numeric_cols:
            start_val = df[col].iloc[0]
            end_val = df[col].iloc[-1]
            if start_val != 0:
                pct_change = ((end_val - start_val) / start_val) * 100
                trends += f"- {col}: {pct_change:.2f}% (from {start_val} to {end_val})\n"
                
        # Get the most recent quarter's snapshot
        recent_status = df.iloc[-1].to_string()
        
        return f"--- Statistical Summary ---\n{summary}\n\n--- Trend Analysis ---\n{trends}\n\n--- Most Recent Data Snapshot ---\n{recent_status}"
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

# ==========================================
# 4. CREATE THE AGENT TEAM (Now 3 Agents!)
# ==========================================

researcher = Agent(
    role='Corporate OSINT Researcher',
    goal='Search the web to uncover recent news and controversies about a company.',
    backstory='You are an elite investigator. You only report factual news found online.',
    verbose=True,
    tools=[search_tool],
    llm=llm
)

financial_analyst = Agent(
    role='Senior Financial Data Analyst',
    goal='Analyze internal CSV financial data to identify trends, risks, and cash flow issues.',
    backstory='You are a master of corporate finance. You read data tables and immediately spot if a company is going bankrupt or growing.',
    verbose=True,
    tools=[analyze_financial_csv], # Giving it your custom Pandas tool!
    llm=llm
)

cro_agent = Agent(
    role='Chief Risk Officer (CRO)',
    goal='Synthesize web research and financial data into a final Risk Assessment Report.',
    backstory='You are a strict Chief Risk Officer. You take the Web Researcher notes and Financial Analyst notes and write a brilliant Executive Summary.',
    verbose=True,
    llm=llm
)

# ==========================================
# 5. CREATE THE TASKS
# ==========================================
company_name = "Boeing" # We can change this to any company later

task_1 = Task(
    description=f'Search for the most recent news and legal issues facing {company_name} in the last 6 months.',
    expected_output='A bulleted list of recent news and controversies.',
    agent=researcher
)

task_2 = Task(
    description='Use the "Read Financial Data" tool to read the file "financial_data.csv". Analyze the Quarter-over-Quarter trends for Revenue, Debt, and Cash Flow. Tell me if this company is financially healthy.',
    expected_output='A summary of the financial trends and a verdict on financial health.',
    agent=financial_analyst
)

task_3 = Task(
    description=f'Combine the notes from the Researcher (Task 1) and the Financial Analyst (Task 2) to write a comprehensive "Final Risk Assessment" on {company_name}. Include headers: 1. Public Perception & Legal Risk, 2. Financial Health Risk, 3. Final Executive Verdict.',
    expected_output='A highly professional Markdown report.',
    agent=cro_agent
)

# ==========================================
# 6. ASSEMBLE THE SWARM
# ==========================================
crew = Crew(
    agents=[researcher, financial_analyst, cro_agent],
    tasks=[task_1, task_2, task_3],
    verbose=True,
    process=Process.sequential 
)

print("Booting up Aegis Swarm (Web + Data + Logic)...")
result = crew.kickoff()

print("\n================================================")
print("FINAL AEGIS REPORT:")
print("================================================")
print(result)