import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from crewai import Agent, Task, Crew, Process, LLM

# 1. Set your API Key (Replace with your actual key)
os.environ["GEMINI_API_KEY"] = "AIzaSyB8N23uOP6h9Vycrt_mLNe3xj3KiVV6Rgk"

# 2. Initialize the Gemini 2.5 Flash Model (Fast and great for logic)
llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.5
)

# 3. Create your first Agent
researcher_agent = Agent(
    role='Senior Corporate OSINT Researcher',
    goal='Uncover critical background information, history, and potential risks regarding a specific company.',
    backstory='You are an elite corporate investigator. You excel at taking a company name and providing a clear, structured summary of what they do, who their competitors are, and any major public controversies.',
    verbose=True,
    allow_delegation=False,
    llm=llm # Giving the agent its brain!
)

# 4. Create the Task for the Agent
research_task = Task(
    description='Write a brief, 3-paragraph summary on the company "OpenAI". Include what they do, their flagship products, and one major challenge they face.',
    expected_output='A 3-paragraph markdown report summarizing the company.',
    agent=researcher_agent
)

# 5. Assemble the Crew and Kick it off!
crew = Crew(
    agents=[researcher_agent],
    tasks=[research_task],
    verbose=True,
    process=Process.sequential # Runs tasks one after the other
)

print("Starting the Agent...")
result = crew.kickoff()

print("\n================================================")
print("AGENT OUTPUT:")
print("================================================")
print(result)