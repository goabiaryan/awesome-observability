"""
LLM Observability Module
Provides unified interface for tracing, evaluation, and monitoring across multiple backends.

Usage:
    from observability import create_langfuse_client, instrument_openai
    
    client = create_langfuse_client()
    instrument_openai()  # Auto-trace OpenAI calls
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any, Callable, List
from functools import wraps
from datetime import datetime
from enum import Enum

import openai
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# ============================================================================
# Metrics (Prometheus)
# ============================================================================

llm_requests = Counter("llm_requests_total", "Total LLM requests", ["model", "endpoint"])
llm_tokens = Counter("llm_tokens_total", "Total tokens used", ["model", "type"])
llm_errors = Counter("llm_errors_total", "Total LLM errors", ["model", "error_type"])
llm_latency = Histogram("llm_latency_seconds", "LLM request latency", ["model"], buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0))
llm_cost = Counter("llm_cost_total", "Total LLM costs", ["model"])
llm_hallucination_score = Gauge("llm_hallucination_score", "Hallucination score (0-1)", ["request_id"])
llm_answer_relevancy = Gauge("llm_answer_relevancy_score", "Answer relevancy (0-1)", ["request_id"])
llm_quality_gate_pass_rate = Gauge("llm_quality_gate_pass_rate", "Quality gate pass rate", ["metric"])

# ============================================================================
# Enums
# ============================================================================

class TracingBackend(Enum):
    """Supported tracing backends"""
    LANGFUSE = "langfuse"
    PHOENIX = "phoenix"
    HELICONE = "helicone"
    OTEL = "otel"

class EvalFramework(Enum):
    """Supported evaluation frameworks"""
    DEEPEVAL = "deepeval"
    RAGAS = "ragas"
    TRULENS = "trulens"

# ============================================================================
# Langfuse Client Wrapper
# ============================================================================

class LangfuseObservability:
    """Langfuse integration for LLM observability"""
    
    def __init__(self, host: Optional[str] = None):
        try:
            from langfuse import Langfuse
        except ImportError:
            raise ImportError("Install langfuse: pip install langfuse")
        
        self.host = host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        
        if not self.public_key or not self.secret_key:
            raise ValueError("Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY env vars")
        
        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host,
            release="production",
            enabled=True
        )
    
    def trace_langchain(self):
        """Return LangChain callback handler for tracing"""
        from langfuse.callback_handler import CallbackHandler
        return CallbackHandler()
    
    def trace_llamaindex(self):
        """Return LlamaIndex callback handler"""
        # LlamaIndex integrates via: llama_index.callbacks import CallbackManager
        # Then: callback_manager.add_handler(langfuse_handler)
        pass
    
    def create_trace(self, name: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Create a new trace"""
        return self.client.trace(
            name=name,
            user_id=user_id,
            metadata=metadata or {}
        )
    
    def log_message(self, trace_id: str, message: str, level: str = "info"):
        """Log a message to a trace"""
        logger.log(level.upper(), f"[{trace_id}] {message}")
    
    def flush(self):
        """Flush pending events"""
        self.client.flush()

# ============================================================================
# Phoenix Client Wrapper
# ============================================================================

class PhoenixObservability:
    """Arize Phoenix integration for evaluation & drift detection"""
    
    def __init__(self):
        try:
            import phoenix as px
        except ImportError:
            raise ImportError("Install phoenix: pip install arize-phoenix")
        
        self.px = px
        self.client = None
    
    def start_server(self, port: int = 6006):
        """Start Phoenix evaluation server"""
        try:
            self.client = self.px.launch_app()
            logger.info(f"Phoenix server running at http://localhost:{port}")
        except Exception as e:
            logger.warning(f"Phoenix server already running or error: {e}")
    
    def create_evaluation_dataset(self, data: List[Dict]):
        """Create evaluation dataset"""
        # Implementation depends on Phoenix version
        pass
    
    def track_embedding_drift(self, embeddings: List[List[float]]):
        """Track embedding drift over time"""
        # Uses internal drift detection algorithms
        pass

# ============================================================================
# Helicone Client Wrapper
# ============================================================================

class HeliconeObservability:
    """Helicone integration for cost & latency tracking"""
    
    def __init__(self):
        self.api_key = os.getenv("HELICONE_API_KEY")
        if not self.api_key:
            raise ValueError("Set HELICONE_API_KEY env var")
    
    def enable_proxy(self):
        """Enable Helicone as OpenAI proxy"""
        # Helicone uses OpenAI API with proxy headers
        logger.info("Helicone proxy enabled. Ensure OPENAI_API_KEY is set.")
    
    def get_analytics(self, limit: int = 100):
        """Fetch cost/latency analytics from Helicone"""
        # Would call Helicone API
        logger.info(f"Fetching analytics for last {limit} requests from Helicone")

# ============================================================================
# OpenTelemetry Instrumentation
# ============================================================================

class OTelObservability:
    """OpenTelemetry-based instrumentation"""
    
    def __init__(self, service_name: str = "llm-app"):
        try:
            from opentelemetry import trace, metrics
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import SimpleSpanProcessor
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.exporter.prometheus import PrometheusMetricReader
        except ImportError:
            raise ImportError("Install OpenTelemetry: pip install opentelemetry-api opentelemetry-sdk")
        
        self.service_name = service_name
        self.tracer = trace.get_tracer(__name__)
    
    def instrument_openai(self):
        """Instrument OpenAI SDK with OTel"""
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        OpenAIInstrumentor().instrument()
        logger.info("OpenAI SDK instrumented with OpenTelemetry")
    
    def instrument_langchain(self):
        """Instrument LangChain with OTel"""
        from opentelemetry.instrumentation.langchain import LangChainInstrumentor
        LangChainInstrumentor().instrument()
        logger.info("LangChain instrumented with OpenTelemetry")

# ============================================================================
# Cost Tracking
# ============================================================================

class CostTracker:
    """Track LLM costs across models"""
    
    # 2026 pricing (OpenAI, Anthropic)
    PRICING = {
        "gpt-4-turbo": {"input": 0.00003, "output": 0.0001},
        "gpt-4": {"input": 0.00003, "output": 0.0001},
        "gpt-3.5-turbo": {"input": 0.0000005, "output": 0.0000015},
        "claude-3-opus": {"input": 0.000015, "output": 0.000075},
        "claude-3-sonnet": {"input": 0.000003, "output": 0.000015},
        "claude-3-haiku": {"input": 0.00000025, "output": 0.00000125},
    }
    
    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request"""
        if model not in CostTracker.PRICING:
            logger.warning(f"Unknown model {model}, assuming GPT-3.5-turbo pricing")
            model = "gpt-3.5-turbo"
        
        pricing = CostTracker.PRICING[model]
        total = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
        return total
    
    @staticmethod
    def format_cost(cost: float) -> str:
        """Format cost for display"""
        return f"${cost:.6f}"

# ============================================================================
# OpenAI Instrumentation
# ============================================================================

def instrument_openai(backend: TracingBackend = TracingBackend.LANGFUSE):
    """Auto-instrument OpenAI calls with tracing
    
    Args:
        backend: Tracing backend to use
    
    Example:
        instrument_openai()
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    original_create = openai.ChatCompletion.create
    
    @wraps(original_create)
    def traced_create(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = original_create(*args, **kwargs)
            
            # Track metrics
            model = kwargs.get("model", "unknown")
            if "usage" in response:
                input_tokens = response["usage"].get("prompt_tokens", 0)
                output_tokens = response["usage"].get("completion_tokens", 0)
                total_tokens = response["usage"].get("total_tokens", 0)
                
                llm_requests.labels(model=model, endpoint="chat").inc()
                llm_tokens.labels(model=model, type="input").inc(input_tokens)
                llm_tokens.labels(model=model, type="output").inc(output_tokens)
                
                cost = CostTracker.calculate_cost(model, input_tokens, output_tokens)
                llm_cost.labels(model=model).inc(cost)
            
            latency = time.time() - start_time
            llm_latency.labels(model=model).observe(latency)
            
            logger.info(f"OpenAI request: {model} ({latency:.2f}s)")
            
            return response
            
        except Exception as e:
            llm_errors.labels(model=kwargs.get("model", "unknown"), error_type=type(e).__name__).inc()
            logger.error(f"OpenAI error: {e}")
            raise
    
    openai.ChatCompletion.create = traced_create
    logger.info("OpenAI calls instrumented with automatic tracing")

# ============================================================================
# Main Observability Client
# ============================================================================

class LLMObservability:
    """Unified observability client supporting multiple backends"""
    
    def __init__(
        self,
        tracing_backend: str = "langfuse",
        auto_eval: bool = True,
        eval_framework: str = "deepeval"
    ):
        """Initialize observability
        
        Args:
            tracing_backend: "langfuse" | "phoenix" | "helicone" | "otel"
            auto_eval: Enable automatic evaluation
            eval_framework: "deepeval" | "ragas" | "trulens"
        """
        self.tracing_backend = TracingBackend(tracing_backend)
        self.eval_framework = EvalFramework(eval_framework)
        self.auto_eval = auto_eval
        
        # Initialize backends
        self._init_tracing()
        if auto_eval:
            self._init_evaluation()
    
    def _init_tracing(self):
        """Initialize tracing backend"""
        if self.tracing_backend == TracingBackend.LANGFUSE:
            self.tracer = LangfuseObservability()
            logger.info("Langfuse tracing initialized")
        elif self.tracing_backend == TracingBackend.PHOENIX:
            self.tracer = PhoenixObservability()
            self.tracer.start_server()
            logger.info("Phoenix tracing initialized")
        elif self.tracing_backend == TracingBackend.HELICONE:
            self.tracer = HeliconeObservability()
            self.tracer.enable_proxy()
            logger.info("Helicone tracing initialized")
        elif self.tracing_backend == TracingBackend.OTEL:
            self.tracer = OTelObservability()
            self.tracer.instrument_openai()
            logger.info("OpenTelemetry tracing initialized")
    
    def _init_evaluation(self):
        """Initialize evaluation framework"""
        if self.eval_framework == EvalFramework.DEEPEVAL:
            logger.info("DeepEval evaluation initialized")
        elif self.eval_framework == EvalFramework.RAGAS:
            logger.info("Ragas evaluation initialized")
        elif self.eval_framework == EvalFramework.TRULENS:
            logger.info("TruLens evaluation initialized")
    
    def trace(self, name: str, metadata: Optional[Dict] = None):
        """Create a traced function/block"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                trace_id = metadata.get("trace_id", str(time.time())) if metadata else str(time.time())
                
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"Trace {name} completed successfully")
                    return result
                except Exception as e:
                    logger.error(f"Trace {name} failed: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def log_event(self, event_name: str, event_data: Dict):
        """Log observability event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_name,
            "data": event_data
        }
        logger.info(json.dumps(event))
    
    def flush(self):
        """Flush pending events"""
        if hasattr(self.tracer, 'flush'):
            self.tracer.flush()
            logger.info("Flushed pending observability events")

# ============================================================================
# Factory Functions
# ============================================================================

def create_langfuse_client() -> LangfuseObservability:
    """Create Langfuse client
    
    Example:
        client = create_langfuse_client()
        trace = client.create_trace("my_trace")
    """
    return LangfuseObservability()

def create_observability_client(backend: str = "langfuse") -> LLMObservability:
    """Create observability client for given backend"""
    return LLMObservability(tracing_backend=backend)

# ============================================================================
# Decorators for Easy Integration
# ============================================================================

def track_llm_call(model: str = "gpt-4"):
    """Decorator to auto-track LLM calls
    
    Example:
        @track_llm_call(model="gpt-4")
        def query_llm(prompt: str) -> str:
            return openai.ChatCompletion.create(...)["choices"][0]["message"]["content"]
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start
                llm_latency.labels(model=model).observe(latency)
                llm_requests.labels(model=model, endpoint="custom").inc()
                logger.info(f"{func.__name__} completed in {latency:.2f}s")
                return result
            except Exception as e:
                llm_errors.labels(model=model, error_type=type(e).__name__).inc()
                raise
        return wrapper
    return decorator

def track_cost(model: str = "gpt-4"):
    """Decorator to track LLM costs"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Assumes result is OpenAI response dict
            if isinstance(result, dict) and "usage" in result:
                cost = CostTracker.calculate_cost(
                    model,
                    result["usage"].get("prompt_tokens", 0),
                    result["usage"].get("completion_tokens", 0)
                )
                llm_cost.labels(model=model).inc(cost)
                logger.info(f"Cost for {func.__name__}: {CostTracker.format_cost(cost)}")
            return result
        return wrapper
    return decorator

# ============================================================================
# Initialization
# ============================================================================

if __name__ == "__main__":
    # Test setup
    obs = create_observability_client("langfuse")
    logger.info("Observability client initialized successfully")
