"""
Example 2: LangChain Agent with Tracing & Evaluation

This example demonstrates:
- LangChain ReAct agent with tools
- Automatic tracing with Langfuse
- Quality evaluation of agent outputs
- Token/cost tracking
- Agent loop monitoring
"""

import os
import logging
from typing import Optional

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.callbacks import StdOutCallbackHandler

# Observability
from observability import (
    create_langfuse_client,
    instrument_openai,
    track_llm_call,
    CostTracker
)
from eval_utils import EvalPipeline

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize observability
langfuse_client = create_langfuse_client()
instrument_openai()

# Initialize evaluation
eval_pipeline = EvalPipeline(
    metrics=["answer_relevancy", "coherence"],
    backend="deepeval"
)

# ============================================================================
# Tools for Agent
# ============================================================================

def search_web(query: str) -> str:
    """Mock web search tool"""
    return f"Search results for '{query}': Found 5 relevant pages (mock implementation)"

def calculate(expression: str) -> str:
    """Calculator tool"""
    try:
        result = eval(expression)
        return f"Result of {expression}: {result}"
    except Exception as e:
        return f"Error calculating {expression}: {e}"

def get_weather(location: str) -> str:
    """Mock weather tool"""
    return f"Weather in {location}: Clear, 72°F (mock data)"

# Define tools for agent
tools = [
    Tool(
        name="Search",
        func=search_web,
        description="Useful for searching the internet for information"
    ),
    Tool(
        name="Calculator",
        func=calculate,
        description="Useful for doing mathematical calculations"
    ),
    Tool(
        name="Weather",
        func=get_weather,
        description="Get weather information for a location"
    )
]

# ============================================================================
# Agent Setup
# ============================================================================

class ObservedLangChainAgent:
    """Wrapper for LangChain agent with observability"""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0):
        """Initialize agent with tracing"""
        
        # LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Agent with Langfuse callback
        from langfuse.callback_handler import CallbackHandler
        
        self.langfuse_handler = CallbackHandler(
            tags=["agent", "production"]
        )
        
        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=10,
            callbacks=[
                self.langfuse_handler,
                StdOutCallbackHandler()  # Console output
            ],
            handle_parsing_errors=True
        )
        
        logger.info(f"Agent initialized with {len(tools)} tools")
    
    async def run(self, query: str, trace_name: Optional[str] = None) -> dict:
        """Run agent with obs and evaluation
        
        Args:
            query: User query
            trace_name: Optional trace name for grouping
        
        Returns:
            Dict with answer, evaluation scores, and metrics
        """
        import time
        start_time = time.time()
        
        # Create trace
        trace = self.langfuse_handler.trace(
            name=trace_name or f"agent_query_{int(start_time)}"
        )
        
        try:
            # Run agent
            logger.info(f"Running agent for query: {query}")
            response = self.agent.run(query)
            
            # Evaluate response
            logger.info("Evaluating agent response...")
            eval_result = await eval_pipeline.evaluate(
                output=response,
                question=query
            )
            
            # Metrics
            latency = time.time() - start_time
            scores = {s.metric_name: s.score for s in eval_result.scores}
            
            result = {
                "answer": response,
                "trace_id": trace.id if hasattr(trace, 'id') else None,
                "evaluation": {
                    "answer_relevancy": scores.get("answer_relevancy", 0.5),
                    "coherence": scores.get("coherence", 0.5),
                    "average_score": eval_result.average_score
                },
                "metrics": {
                    "latency_seconds": latency,
                    "iterations": getattr(self.agent, 'iterations', 0)
                }
            }
            
            logger.info(f"Agent response evaluated: quality={eval_result.average_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise
        finally:
            # Flush traces
            # langfuse_client.flush()
            pass

# ============================================================================
# Usage
# ============================================================================

async def main():
    """Example usage"""
    agent = ObservedLangChainAgent()
    
    # Example queries
    queries = [
        "What is the capital of France?",
        "Calculate 25 * 4",
        "What's the weather in New York?",
        "Search for information about machine learning and tell me what you find"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = await agent.run(query)
        
        print(f"\nAnswer: {result['answer']}")
        print(f"Quality Score: {result['evaluation']['average_score']:.2f}")
        print(f"Latency: {result['metrics']['latency_seconds']:.2f}s")
        print(f"Trace ID: {result['trace_id']}")

# ============================================================================
# Run
# ============================================================================

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
    # View results in:
    # - Langfuse: http://localhost:3000
    # - Prometheus: http://localhost:9090
