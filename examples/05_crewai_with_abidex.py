import os
import abidex
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI


abidex.instrument_crew()

llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)

research_agent = Agent(
    role="Research Analyst",
    goal="Identify and analyze emerging trends in AI agents",
    backstory="Expert AI researcher with 10+ years in LLM field. Deep knowledge of agent architectures, multi-agent systems, and industry trends.",
    llm=llm,
    verbose=True
)

writer_agent = Agent(
    role="Technical Content Writer",
    goal="Transform research into clear, engaging technical content",
    backstory="Award-winning technical writer specializing in AI/ML. Excellent at explaining complex concepts for diverse audiences.",
    llm=llm,
    verbose=True
)

reviewer_agent = Agent(
    role="Quality Assurance Reviewer",
    goal="Ensure accuracy and clarity of final content",
    backstory="Meticulous editor with background in AI research and technical writing. Catches subtle errors and improves clarity.",
    llm=llm,
    verbose=True
)

research_task = Task(
    description="Research the latest trends in multi-agent systems, focusing on: 1) CrewAI framework capabilities, 2) LangGraph graph-based agents, 3) Agent coordination patterns, 4) Real-world use cases. Compile findings into structured notes.",
    agent=research_agent,
    expected_output="Detailed research notes with 5-7 key trends and supporting evidence"
)

write_task = Task(
    description="Based on research findings, write a comprehensive technical article (800-1000 words) about multi-agent systems. Include: introduction, key trends, architectural patterns, use cases, and conclusion.",
    agent=writer_agent,
    expected_output="Well-structured technical article ready for publication"
)

review_task = Task(
    description="Review the article for: technical accuracy, clarity, grammar, structure. Provide specific feedback and corrections.",
    agent=reviewer_agent,
    expected_output="Final review with corrections and improvement suggestions"
)

crew = Crew(
    agents=[research_agent, writer_agent, reviewer_agent],
    tasks=[research_task, write_task, review_task],
    verbose=True,
    max_rpm=None
)

if __name__ == "__main__":
    result = crew.kickoff()

    print("\n" + "="*80)
    print("CREW EXECUTION COMPLETE")
    print("="*80)
    print(result)

    print("\n" + "="*80)
    print("TRACE SUMMARY")
    print("="*80)
    abidex.trace.print_summary()

    print("\n" + "="*80)
    print("EXPORTING TO OTLP BACKEND")
    print("="*80)
    abidex.trace.export_to_opentelemetry()
    print("Traces exported to OTLP backend (check SigNoz/Uptrace for visualization)")
