import os
import json
import abidex
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools import tool


abidex.instrument_langgraph()

llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)


class AgentState(TypedDict):
    input: str
    research_output: str
    analysis_output: str
    final_output: str


@tool
def search_knowledge_base(query: str) -> str:
    return f"Found information about {query}: [relevant documents]"


@tool
def fetch_market_data(topic: str) -> str:
    return f"Market data for {topic}: [structured data]"


def research_node(state: AgentState) -> dict:
    query = state["input"]
    research_result = search_knowledge_base(query)
    return {
        "research_output": research_result,
        "input": state["input"]
    }


def analysis_node(state: AgentState) -> dict:
    research = state["research_output"]
    market_data = fetch_market_data(state["input"])

    analysis_prompt = f"""
    Based on research: {research}
    Market data: {market_data}
    Provide analysis of {state['input']}
    """

    analysis = llm.invoke(analysis_prompt).content
    return {
        "analysis_output": analysis,
        "input": state["input"],
        "research_output": research
    }


def synthesis_node(state: AgentState) -> dict:
    synthesis_prompt = f"""
    Research: {state['research_output']}
    Analysis: {state['analysis_output']}
    Create final summary
    """

    final = llm.invoke(synthesis_prompt).content
    return {
        "final_output": final,
        "input": state["input"],
        "research_output": state["research_output"],
        "analysis_output": state["analysis_output"]
    }


def should_analyze(state: AgentState) -> str:
    if len(state["research_output"]) > 10:
        return "analyze"
    return END


def should_synthesize(state: AgentState) -> str:
    if len(state["analysis_output"]) > 10:
        return "synthesize"
    return END


workflow = StateGraph(AgentState)

workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("synthesis", synthesis_node)

workflow.set_entry_point("research")

workflow.add_conditional_edges(
    "research",
    should_analyze,
    {
        "analyze": "analysis",
        END: END
    }
)

workflow.add_conditional_edges(
    "analysis",
    should_synthesize,
    {
        "synthesize": "synthesis",
        END: END
    }
)

workflow.add_edge("synthesis", END)

app = workflow.compile()


if __name__ == "__main__":
    initial_state = {
        "input": "What are emerging trends in AI agent frameworks?",
        "research_output": "",
        "analysis_output": "",
        "final_output": ""
    }

    print("="*80)
    print("LANGGRAPH AGENT EXECUTION WITH ABIDEX TRACING")
    print("="*80)

    result = app.invoke(initial_state)

    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(json.dumps(result, indent=2))

    print("\n" + "="*80)
    print("TRACE SUMMARY")
    print("="*80)
    abidex.trace.print_summary()

    print("\n" + "="*80)
    print("EXPORTING TRACES TO OTLP")
    print("="*80)
    abidex.trace.export_to_opentelemetry()
    print("Traces available in SigNoz/Uptrace/Jaeger")
