import os
import logging
from typing import Optional
import time
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.callbacks import StdOutCallbackHandler

from src.observability import (
    create_langfuse_client,
    instrument_openai,
    track_llm_call,
    CostTracker
)
from src.eval_utils import EvalPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

langfuse_client = create_langfuse_client()
instrument_openai()

eval_pipeline = EvalPipeline(
    metrics=["answer_relevancy", "coherence"],
    backend="deepeval"
)


def search_web(query: str) -> str:
    return f"Search results for '{query}': Found 5 relevant pages (mock implementation)"


def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"Result of {expression}: {result}"
    except Exception as e:
        return f"Error calculating {expression}: {e}"


def get_weather(location: str) -> str:
    return f"Weather in {location}: Clear, 72°F (mock data)"


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


class ObservedLangChainAgent:
    def __init__(self, model: str = "gpt-4", temperature: float = 0):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
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
                StdOutCallbackHandler()
            ],
            handle_parsing_errors=True
        )
        
        logger.info(f"Agent initialized with {len(tools)} tools")
    
    async def run(self, query: str, trace_name: Optional[str] = None) -> dict:
        start_time = time.time()
        
        trace = self.langfuse_handler.trace(
            name=trace_name or f"agent_query_{int(start_time)}"
        )
        
        try:
            logger.info(f"Running agent for query: {query}")
            response = self.agent.run(query)
            
            logger.info("Evaluating agent response...")
            eval_result = await eval_pipeline.evaluate(
                output=response,
                question=query
            )
            
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


async def main():
    agent = ObservedLangChainAgent()
    
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


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
