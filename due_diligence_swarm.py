import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# 1. Set your API Keys
load_dotenv()

# 2. Initialize the Brain and the Tool
llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.5
)
search_tool = SerperDevTool() # This gives the agent Google Search!

# ==========================================
# 3. CREATE THE AGENT TEAM
# ==========================================

# Agent 1: The Researcher (Now has internet access!)
researcher_agent = Agent(
    role='Senior Corporate OSINT Researcher',
    goal='Search the web to uncover recent news, controversies, and financial updates about a specific company.',
    backstory='You are an elite corporate investigator. You use search tools to find recent articles and facts about a company. You never make things up; you only report what you find online.',
    verbose=True,
    tools=[search_tool], # Giving the agent its hands!
    llm=llm
)

# Agent 2: The Chief Risk Officer (CRO)
cro_agent = Agent(
    role='Chief Risk Officer (CRO)',
    goal='Analyze research data and write a strict, professional Risk Assessment Report for the CEO.',
    backstory='You are a skeptical, highly analytical Chief Risk Officer. You take raw research from your team and format it into a brilliant, easy-to-read Markdown report highlighting potential business risks.',
    verbose=True,
    llm=llm
)

# ==========================================
# 4. CREATE THE TASKS
# ==========================================

# We will target a company that recently had news. Let's use "Boeing" as an example for good risk data.
company_name = "Boeing"

task_1_research = Task(
    description=f'Use your search tool to find the most recent news, legal issues, and financial challenges facing {company_name} in the last 6 months. Gather as much factual data as possible.',
    expected_output='A raw bulleted list of facts, links, and recent news events.',
    agent=researcher_agent
)

task_2_report = Task(
    description=f'Take the research provided by the Researcher Agent and write a "Final Risk Assessment" report on {company_name}. Structure it with headers: 1. Executive Summary, 2. Key Risks (Financial & Legal), 3. Final Verdict (Should we partner with them?).',
    expected_output='A highly professional Markdown report.',
    agent=cro_agent
)

# ==========================================
# 5. ASSEMBLE AND KICKOFF THE SWARM
# ==========================================

# Notice how the agents and tasks are in a list. It processes them in order!
crew = Crew(
    agents=[researcher_agent, cro_agent],
    tasks=[task_1_research, task_2_report],
    verbose=True,
    process=Process.sequential 
)

print(f"Starting the Due Diligence Swarm for {company_name}...")
result = crew.kickoff()

print("\n================================================")
print("FINAL CRO RISK REPORT:")
print("================================================")
print(result)