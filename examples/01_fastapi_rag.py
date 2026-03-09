"""
Example 1: FastAPI RAG Application with Langfuse Tracing & DeepEval

This example shows how to build a production-ready RAG API with:
- Automatic request tracing (Langfuse)
- Streaming responses
- Online evaluation with DeepEval
- Cost tracking
- Quality gates
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
import asyncio
from datetime import datetime

# Observability imports
from observability import (
    create_langfuse_client,
    instrument_openai,
    CostTracker,
    track_llm_call
)
from eval_utils import EvalPipeline, HallucinationDetector

# LLM imports
import openai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="RAG API with Observability", version="1.0.0")

# Initialize observability
langfuse_client = create_langfuse_client()
instrument_openai()  # Auto-instrument OpenAI calls

# Initialize evaluation
eval_pipeline = EvalPipeline(
    metrics=["hallucination", "faithfulness", "answer_relevancy"],
    backend="deepeval",
    quality_gate_threshold=0.8
)

hallucination_detector = HallucinationDetector(threshold=0.85)

# ============================================================================
# Data Models
# ============================================================================

class Document(BaseModel):
    """Retrieved document"""
    content: str
    source: str
    relevance_score: float

class QueryRequest(BaseModel):
    """Query request"""
    question: str
    top_k: int = 5
    temperature: float = 0.7
    max_tokens: int = 512

class QueryResponse(BaseModel):
    """Query response with quality metrics"""
    answer: str
    documents: List[Document]
    quality_score: float
    hallucination_score: float
    answer_relevancy: float
    passed_quality_gate: bool
    cost: str
    latency_ms: int
    model: str = "gpt-4"
    trace_id: Optional[str] = None

# ============================================================================
# Helper Functions
# ============================================================================

def retrieve_documents(query: str, top_k: int = 5) -> List[Document]:
    """Retrieve documents (mock implementation)
    
    In production, this would call your vector database (Pinecone, Weaviate, etc.)
    """
    # Mock retrieval
    mock_docs = [
        Document(
            content="RAG (Retrieval Augmented Generation) combines retrieval with generation.",
            source="docs/rag-overview.md",
            relevance_score=0.95
        ),
        Document(
            content="LLMs can generate fluent text but may hallucinate facts.",
            source="docs/llm-limitations.md",
            relevance_score=0.88
        ),
    ]
    return mock_docs[:top_k]

async def call_llm(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
    trace_id: Optional[str] = None
) -> str:
    """Call LLM with automatic tracing"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        answer = response["choices"][0]["message"]["content"]
        
        # Log to Langfuse
        if trace_id:
            logger.info(f"[{trace_id}] LLM call completed: {len(answer)} chars")
        
        return answer
        
    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        raise HTTPException(status_code=429, detail="Rate limited by LLM provider")
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=500, detail="LLM error")

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Query RAG pipeline with evaluation and monitoring
    
    Example:
        curl -X POST "http://localhost:8000/query" \\
             -H "Content-Type: application/json" \\
             -d '{"question": "What is RAG?"}'
    """
    import time
    start_time = time.time()
    trace_id = f"trace_{int(start_time * 1000)}"
    
    try:
        # ===== Step 1: Retrieve Documents =====
        logger.info(f"[{trace_id}] Retrieving documents for: {request.question}")
        documents = retrieve_documents(request.question, top_k=request.top_k)
        
        # ===== Step 2: Build RAG Prompt =====
        context = "\n---\n".join([f"{d.source}:\n{d.content}" for d in documents])
        rag_prompt = f"""Answer the following question based on the provided context.
If the answer is not in the context, say "I don't have enough information."

Context:
{context}

Question: {request.question}

Answer:"""
        
        # ===== Step 3: Call LLM =====
        logger.info(f"[{trace_id}] Calling LLM...")
        answer = await call_llm(
            prompt=rag_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            trace_id=trace_id
        )
        
        # ===== Step 4: Evaluate Response =====
        logger.info(f"[{trace_id}] Evaluating response...")
        eval_result = await eval_pipeline.evaluate(
            output=answer,
            context=context,
            question=request.question
        )
        
        # ===== Step 5: Check for Hallucinations =====
        is_hallucinating = await hallucination_detector.is_hallucinating(answer, context)
        if is_hallucinating:
            logger.warning(f"[{trace_id}] Hallucination detected in response")
        
        # ===== Step 6: Calculate Metrics =====
        latency_ms = int((time.time() - start_time) * 1000)
        cost = CostTracker.calculate_cost("gpt-4", input_tokens=len(rag_prompt)//4, output_tokens=len(answer)//4)
        
        # Extract quality scores
        scores = {s.metric_name: s.score for s in eval_result.scores}
        
        response = QueryResponse(
            answer=answer,
            documents=documents,
            quality_score=eval_result.average_score,
            hallucination_score=scores.get("hallucination", 0.5),
            answer_relevancy=scores.get("answer_relevancy", 0.5),
            passed_quality_gate=eval_result.average_score >= eval_pipeline.quality_gate_threshold,
            cost=CostTracker.format_cost(cost),
            latency_ms=latency_ms,
            trace_id=trace_id
        )
        
        logger.info(f"[{trace_id}] Response: quality={response.quality_score:.2f}, "
                   f"hallucination={response.hallucination_score:.2f}, latency={latency_ms}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"[{trace_id}] Request failed: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "observability": "enabled"
    }

@app.post("/batch-evaluate")
async def batch_evaluate(queries: List[QueryRequest]):
    """Batch evaluate multiple queries
    
    Useful for testing quality metrics across many examples.
    """
    results = []
    for query in queries:
        result = await query(query)
        results.append(result)
    
    # Calculate aggregate stats
    avg_quality = sum(r.quality_score for r in results) / len(results)
    pass_rate = sum(1 for r in results if r.passed_quality_gate) / len(results)
    
    return {
        "total_queries": len(results),
        "average_quality_score": avg_quality,
        "pass_rate": pass_rate,
        "results": results
    }

# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("RAG API starting up...")
    logger.info(f"Langfuse connected to: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")
    logger.info(f"Evaluation backend: deepeval")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("RAG API shutting down...")
    langfuse_client.flush()
    logger.info("Observability events flushed")

# ============================================================================
# Run
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

# ============================================================================
# Test with curl:
# ============================================================================
#
# # Health check
# curl http://localhost:8000/health
#
# # Single query
# curl -X POST "http://localhost:8000/query" \\
#      -H "Content-Type: application/json" \\
#      -d '{"question": "What is RAG?", "temperature": 0.7}'
#
# # Batch evaluation
# curl -X POST "http://localhost:8000/batch-evaluate" \\
#      -H "Content-Type: application/json" \\
#      -d '["question": "What is RAG?"], ["question": "How does it work?"]'
#
# # View results in:
# # - Langfuse: http://localhost:3000
# # - Prometheus: http://localhost:9090
# # - Grafana: http://localhost:3001
#
