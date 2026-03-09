# 🔍 Awesome LLM Observability & Agent Monitoring 2026

A **production-grade starter kit** for LLM observability, agent monitoring, and evaluation. This guide prioritizes **abidex** for zero-code agent tracing, with Langfuse, Arize Phoenix, and other tools for complementary observability.

> **Last Updated:** March 2026 | Lead with **abidex** for agents, plus Langfuse, Phoenix, Helicone, DeepEval, Ragas, and more.

---

## 📋 Table of Contents

1. [Quick Decision Tree](#quick-decision-tree)
2. [Tool Comparison](#tool-comparison)
3. [Quick Start](#quick-start)
4. [Installation & Setup](#installation--setup)
5. [Integration Examples](#integration-examples)
6. [Evaluation Pipeline](#evaluation-pipeline)
7. [Best Practices](#best-practices)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Docker Deployment](#docker-deployment)
10. [Awesome Lists](#awesome-lists)
11. [Resources & References](#resources--references)

---

## 🎯 Quick Decision Tree

Choose your observability stack based on your needs:

```
┌─ Start here: What's your primary use case?
│
├─ 🤖 "Agent-heavy (CrewAI, LangGraph, LlamaIndex) + want ZERO-CODE auto-tracing"
│  └─→ abidex (lead) + OTLP backend (SigNoz/Uptrace/Jaeger)
│      Optional: + Langfuse (prompts/evals) or Phoenix (drift)
│      (Best: zero code changes, auto GenAI attributes, OpenTelemetry native)
│
├─ 🔓 "Self-hosted + full control + open-source + agents"
│  └─→ abidex + SigNoz (OTLP) + Langfuse + DeepEval
│      (Best: cost-effective, no lock-in, rich agent visibility)
│
├─ 🐍 "Heavy LangChain/LangGraph + full evals + dashboards"
│  └─→ abidex (tracing) + LangSmith (optional, if LangChain-only)
│      + Langfuse (prompts/sessions) + DeepEval (quality)
│      (Best: deep debugging, agent steps, quality gates)
│
├─ ⚡ "Cost-sensitive: Just track costs/latency + minimal tracing"
│  └─→ Helicone (proxy) + abidex (light tracing)
│      (Best: lightweight, transparent, low overhead)
│
├─ 📊 "Evaluation-first: hallucination/bias checks on agent outputs"
│  └─→ abidex (tracing) + DeepEval (evals) + DeepEval dashboards
│      (Best: 50+ metrics, auto quality gates, monitoring)
│
├─ 👥 "Team collab + experiments + multi-agent coordination"
│  └─→ abidex (tracing) + Braintrust (experiments) + Langfuse (optional)
│      (Best: tracing + experiment tracking + eval collab)
│
└─ 🌐 "RAG/embeddings: agent chains with drift + retrieval quality"
   └─→ abidex (agent tracing) + Phoenix  Agent-Ready |
|----------|-------|------|-----------|-------------|
| **Agent MVP (CrewAI/LangGraph)** | **abidex** + local SigNoz | Low | Very Low | ✅ Yes |
| **Startup with agents** | **abidex** + Langfuse + DeepEval | Low | Low | ✅ Yes |
| **Scale-up (multi-agent)** | **abidex** + SigNoz/Uptrace + Langfuse + DeepEval | Medium | Medium | ✅ Yes |
| **Enterprise (LangChain/agents)** | **abidex** + LangSmith + Langfuse + DeepEval | High | High | ✅ Yes |
| **Cost-sensitive SaaS with agents** | **abidex** + Helicone + Langfuse + Ragas | Low | Low | ✅ Yes |
| **Eval-heavy (RAG agents)** | **abidex** + Phoenix + Ragas + Braintrust | Medium | Medium | ✅ Yes |
| **Maximum compliance (self-hosted agents)** | **abidex** + SigNoz + DeepEval + Prometheus | Medium | Medium | ✅ Yes
| **Startup / MVP** | Langfuse (self-hosted) + DeepEval | Low | Low |
| **Scale-up** | Langfuse + Arize Phoenix + DeepEval + Prometheus | Medium | Medium |
| **Enterprise LangChain** | LangSmith + Langfuse + DeepEval | High | High |
| **Cost-sensitive SaaS** | Helicone + Langfuse + Ragas | Low | Low |
| **EvalTools for Agent Observability

| Feature | **abidex** | Langfuse | Arize Phoenix | Helicone | LangSmith | DeepEval | Braintrust | OpenLLMetry |
|---------|-----------|----------|---------------|----------|-----------|----------|-----------|-------------|
| **Type** | Zero-code agent tracer | All-in-one | Evaluation-first | Cost proxy | Agent tracing | Eval metrics | Eval + collab | OTel-based |
| **OSS** | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Self-hosted** | ✅ (local spans) | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ (local) |
| **Auto Agent Tracing** | ✅✅ | Basic | Basic | ❌ | ✅ | ❌ | ❌ | ❌ |
| **GenAI Attributes** | ✅✅ (role/goal/task) | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **OTel Native** | ✅ (spans only) | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **OTLP Export** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Prompt Mgmt** | ❌ | ✅✅ | ❌ | ❌ | ✅✅ | ❌ | ❌ | ❌ |
| **Evals (50+ metrics)** | ❌ | ✅ | ✅✅ | ❌ | ✅ | ✅✅ | ✅✅ | ❌ |
| **Drift Detection** | ❌ | ✅ | ✅✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **CrewAI/LangGraph support** | ✅✅ | ✅ | Basic | ❌ | ✅ | ❌ | ❌ | Basic |
| **Code changes needed** | ❌ ZERO | Some | Some | None (proxy) | Some | Some | Some | Some |
| **Setup time** | <1 min | 5 min | 5 min | 1 min | 5 min | 5 min | 5 min | 10 min |
| **Pricing** | Free | Free (OSS) | Free (OSS) | Cheap | | Free | Medium | Free (OSS)
| **Prompt Management** | ✅✅ | ❌ | ❌ | ✅✅ | ✅ | ❌ | ❌ |
| **Evals (50+ metrics)** | ✅ | ✅✅ | ❌ | ✅ | ✅✅ | ✅✅ | ❌ |
| **Drift Detection** | ✅ | ✅✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **RAG/Embeddings** | Basic | ✅✅ | Basic | Basic | ✅ | ✅ | Basic |
| **Team Collab** | ✅ | Basic | N/A | ✅ | Basic | ✅✅ | ❌ |
| **Pricing** | Free (OSS) | Free (OSS) | Cheap | | Medium | Medium | Free (OSS) |
| **Learning Curve** | Low | Medium | Low | Low | Medium | Low | High |

### Open-Source Eval Frameworks

| Framework | Hallucinations | Bias | RAGAS Metrics | Faithfulness | Context | License |
|-----------|----------------|------|---------------|--------------|---------|---------|
| **DeepEval** | ✅✅ | ✅ | ✅ | ✅✅ | ✅ | MIT |
| **Ragas** | ✅ | ❌ | ✅✅ | ✅ | ✅ | Apache 2.0 |
python --version
cd awesome-observability
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 60-Second Setup (Recommended: abidex + CrewAI/LangGraph)

```python
import abidex

from crewai import Agent, Task, Crew

crew = Crew(
    agents=[
        Agent(role="Researcher", goal="Research topics", backstory="Expert researcher"),
        Agent(role="Writer", goal="Write articles", backstory="Excellent writer")
    ],
    tasks=[
        Task(description="Research AI", agent=agents[0]),
        Task(description="Write article", agent=agents[1])
    ]
)

result = crew.kickoff()

abidex.trace.print_summary()
```

Or with SigNoz backend:

```bash
export OTEL_SDK_DISABLED=false
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="my-agent-app"
```

Then run your agent—trace automatically exported to SigNoz.
@client.trace_openai_calls
def rag_chain(query: str) -> str:
    # Your RAG logic here
    return f"Answer to: {query}"

# 3. Evaluate
result = rag_chain("What is observability?")
score = evaluate_output(result, query, context)
print(f"Quality score: {score}")
```

---

## 📦 Installation & Setup

### 1. Install Core Dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt`** (key packages):
```
abidex>=0.3.0

langfuse>=2.26.0
arize-phoenix>=4.2.0
opentelemetry-api>=1.21.0
opentelemetry-sdk>=1.21.0
opentelemetry-exporter-otlp>=0.40b0

deepeval>=1.5.0
ragas>=0.1.10

crewai>=0.30.0
langchain>=0.2.0
llama-index>=0.10.0

openai>=1.30.0
anthropic>=0.28.0
fastapi>=0.104.0
uvicorn>=0.24.0
```

### 2. Start with abidex (Zero-Code Agent Tracing)

**Minimal setup:**
```python
import abidex

@abidex.observe
def your_agent_function():
    pass
```

**Or auto-instrument CrewAI/LangGraph:**
```python
import abidex
from crewai import Crew

abidex.instrument_crew()

crew = Crew(agents=[...], tasks=[...])
result = crew.kickoff()
```

**Export to SigNoz/Uptrace via OTLP:**
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="my-agent"
```

### 3. Optional: Add Langfuse for Prompt Management

```python
from langfuse.callback_handler import CallbackHandler

langfuse_handler = CallbackHandler()

agent = initialize_agent(
    tools=tools,
    llm=llm,
    callbacks=[langfuse_handler]
)
```

### 4. Environment Variables

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

export OTEL_SDK_DISABLED=false
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=my-agent-app

export LANGFUSE_PUBLIC_KEY=...
export LANGFUSE_SECRET_KEY=...
export LANGFUSE_HOST=http://localhost:3000
```

---

## 💻 Integration Examples

### Example 1: CrewAI Agent with abidex (Zero-Code)

```python
import abidex
from crewai import Agent, Task, Crew

abidex.instrument_crew()

research_agent = Agent(
    role="Researcher",
    goal="Discover cutting-edge AI trends",
    backstory="Expert AI researcher with deep knowledge"
)

writer_agent = Agent(
    role="Technical Writer",
    goal="Write clear technical articles",
    backstory="Award-winning tech writer"
)

research_task = Task(
    description="Research top AI trends in 2024",
    agent=research_agent
)

write_task = Task(
    description="Write article based on research",
    agent=writer_agent,
    expected_output="Technical article"
)

crew = Crew(
    agents=[research_agent, writer_agent],
    tasks=[research_task, write_task],
    verbose=True
)

result = crew.kickoff()

abidex.trace.print_summary()
abidex.trace.export_to_opentelemetry()
```

### Example 2: LangGraph Multi-Agent with abidex

```python
import abidex
from langgraph.graph import StateGraph
from langchain.agents import initialize_agent

abidex.instrument_langgraph()

workflow = StateGraph(state_schema)

workflow.add_node("agent_1", agent_1_func)
workflow.add_node("agent_2", agent_2_func)
workflow.add_edge("agent_1", "agent_2")

graph = workflow.compile()
state = graph.invoke({"input": "solve problem"})

abidex.trace.print_summary()
```

### Example 3: RAG Agent with abidex + DeepEval

```python
import abidex
import asyncio
from eval_utils import EvalPipeline

@abidex.observe
async def rag_agent(question: str):
    documents = retrieve(question)
    context = "\n".join([d.content for d in documents])
    
    response = llm.generate(f"Context:\n{context}\n\nQuestion: {question}")
    
    pipeline = EvalPipeline(metrics=["hallucination", "faithfulness"])
    scores = await pipeline.evaluate(
        output=response,
        context=context,
        question=question
    )
    
    return {"answer": response, "scores": scores}

result = asyncio.run(rag_agent("What is RAG?"))
abidex.trace.print_summary()
```

### Example 4: FastAPI Endpoint with abidex

```python
import abidex
from fastapi import FastAPI

app = FastAPI()
abidex.instrument_fastapi(app)

@app.post("/agent/query")
async def query(question: str):
    crew = create_crew()
    result = crew.kickoff(input=question)
    
    return {"answer": result, "trace_id": abidex.trace.current_trace_id()}

@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    return abidex.trace.get(trace_id)
```

---

## 📊 Evaluation Pipeline

### Production Evaluation Setup

```python
# eval_utils.py - See full code below
from eval_utils import EvalPipeline

# Initialize
pipeline = EvalPipeline(
    metrics=[
        "hallucination",        # Is response factually grounded?
        "faithfulness",         # Does it match source documents?
        "answer_relevancy",     # Is it relevant to question? (RAGAS)
        "context_precision",    # Is ranked context correct? (RAGAS)
        "bias",                # Any harmful biases?
        "toxicity"              # Is response safe?
    ],
    backend="deepeval",  # Fastest for production
    batch_eval=True
)

# Online evaluation (during request)
scores = await pipeline.evaluate(
    output="The answer is...",
    context="Retrieved context...",
    question="User question..."
)

print(scores)
# Output:
# {
#   "hallucination_score": 0.95,      # 1.0 = no hallucination
#   "faithfulness_score": 0.88,
#   "answer_relevancy_score": 0.92,
#   "bias_score": 0.97,
#   "average": 0.93,
#   "passed_quality_gate": True
# }
```

### Offline Batch Evaluation

```python
# batch_eval.py
from eval_utils import batch_evaluate_dataset

# Evaluate your entire test set
results = batch_evaluate_dataset(
    dataset_path="test_queries.jsonl",  # [{q, context, expected_answer}, ...]
    model="gpt-4",
    metrics=["hallucination", "faithfulness", "answer_relevancy"],
    output_file="eval_results.json"
)

# Generate report
print(f"Average hallucination score: {results['avg_hallucination']}")
print(f"Pass rate (>0.80): {results['pass_rate']}")
```

---

## ✅ Best Practices

### 1. Monitoring Agent Loops

```python
import abidex
from abidex.agent_monitoring import AgentLoopMonitor

monitor = AgentLoopMonitor(
    max_iterations=15,
    max_tokens_per_agent=10000,
    alert_threshold=10000
)

agent = Agent(callbacks=[monitor.callback])
result = agent.run(task)

monitor.check_health()
```

### 2. Detecting Hallucinations in Agent Outputs

```python
import abidex
from eval_utils import HallucinationDetector

abidex.observe

async def validate_agent_output(output: str, context: str):
    detector = HallucinationDetector(threshold=0.85)
    
    is_hallucinating = await detector.is_hallucinating(output, context)
    
    if is_hallucinating:
        abidex.trace.log_warning("Hallucination detected in agent output", {
            "agent_role": abidex.trace.get_agent_role(),
            "task": abidex.trace.get_task(),
            "output": output[:200]
        })
        return False
    
    return True
```

### 3. Token Usage Spikes in Agent Chains

```python
import abidex
from prometheus_client import Gauge

token_gauge = Gauge('agent_tokens_per_task', 'Tokens used per task', ['agent_role'])

@abidex.observe
def run_agent_task(agent, task):
    result = agent.execute(task)
    
    tokens_used = abidex.trace.get_tokens_used()
    agent_role = abidex.trace.get_agent_role()
    
    token_gauge.labels(agent_role=agent_role).set(tokens_used)
    
    return result
```

### 4. Agent Retry Tracking

```python
import abidex

@abidex.observe(name="agent_with_retry")
def agent_execution_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            abidex.trace.log_info(f"Attempt {attempt + 1}/{max_retries}", {
                "attempt": attempt + 1
            })
            
            result = crew.kickoff()
            return result
            
        except Exception as e:
            abidex.trace.log_error(str(e), {
                "attempt": attempt + 1,
                "error_type": type(e).__name__
            })
            
            if attempt == max_retries - 1:
                raise
```

### 5. Safety & Guardrails in Agents

```python
import abidex

def apply_agent_safety_gates(output):
    gates = {
        "blocked_topics": ["financial_advice", "medical_advice"],
        "pii_detection": True,
        "toxicity_threshold": 0.7
    }
    
    for gate_name, gate_config in gates.items():
        if not validate_gate(gate_name, output, gate_config):
            abidex.trace.log_warning(f"Safety gate failed: {gate_name}", {
                "agent_role": abidex.trace.get_agent_role(),
                "gate": gate_name
            })
            return False
    
    return True
```

---

## 📈 Monitoring & Alerting

### OTLP Backends (Primary - Recommended for Agent Tracing)

**Option 1: SigNoz (Self-Hosted, Open-Source)**

```bash
docker run -d -p 3301:3301 signoz/signoz:latest
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="my-agent-app"
```

Access UI at `http://localhost:3301`

**Option 2: Uptrace (Managed SaaS)**

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.uptrace.dev"
export OTEL_EXPORTER_OTLP_HEADERS="uptrace-dsn=<your_dsn>"
export OTEL_SERVICE_NAME="my-agent-app"
```

**Option 3: Jaeger (Distributed Tracing)**

```bash
docker run -d -p 16686:16686 -p 4317:4317 jaegertracing/all-in-one
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

Access UI at `http://localhost:16686`

### Agent-Specific Monitoring in SigNoz

**Traces dashboard shows:**
- Agent role, goal, backstory (from GenAI attributes)
- Task execution spans
- Tool call latency + errors
- Token usage per agent
- Retry/loop detection

**Example query (SigNoz ClickHouse):**
```sql
SELECT
    span_name,
    attributes['agent.role'] as agent_role,
    COUNT() as count,
    AVG(duration) as avg_duration_ms
FROM traces
WHERE span_name LIKE 'agent.%'
GROUP BY span_name, attributes['agent.role']
```

### Prometheus + Grafana (Secondary - for Custom Metrics)

**Configure abidex to export custom metrics:**

```python
from prometheus_client import Counter, Gauge, Histogram

agent_iterations = Counter('agent_iterations_total', 'Agent iterations', ['agent_role'])
agent_tokens = Gauge('agent_tokens_used', 'Tokens used', ['agent_role'])
tool_latency = Histogram('tool_call_duration_ms', 'Tool latency', ['tool_name'])
```

**Prometheus scrape config:**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agent-app'
    static_configs:
      - targets: ['localhost:8000']
```

### Alert Rules (Prometheus)

```yaml
groups:
  - name: agent_monitoring
    rules:
      - alert: AgentMaxIterationsReached
        expr: agent_iterations_total > 15
        annotations:
          summary: "Agent reached max iterations"
          
      - alert: HighToolErrorRate
        expr: rate(tool_errors_total[5m]) > 0.1
        annotations:
          summary: "Tool call error rate > 10%"
          
      - alert: HallucinationDetected
        expr: hallucination_score < 0.80
        annotations:
          summary: "Response hallucination score too low"
          
      - alert: AgentTokenBudgetExceeded
        expr: agent_tokens_used > 10000
        annotations:
          summary: "Agent exceeded token budget"
```
- **Requests/min** (rate over time)
- **Avg latency P50/P99** (response time)
- **Hallucination score** (time series)
- **Cost per hour** (stacked by model)
- **Token usage distribution** (histogram)
- **Quality gates pass rate** (0-100%)

---

## 🐳 Docker Deployment

### Self-Hosted Langfuse + Postgres

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse_password
      POSTGRES_DB: langfuse
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U langfuse"]
      interval: 10s
      timeout: 5s
      retries: 5

  langfuse:
    image: ghcr.io/langfuse/langfuse:latest
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: "postgresql://langfuse:langfuse_password@postgres:5432/langfuse"
      NEXTAUTH_SECRET: "your-secret-key-change-this"
      NEXTAUTH_URL: "http://localhost:3000"
      SALT: "your-salt-change-this"
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    depends_on:
      - prometheus
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_SECURITY_ADMIN_USER: admin
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana

  # Your LLM app
  app:
    build: .
    depends_on:
      - langfuse
      - prometheus
    environment:
      LANGFUSE_HOST: "http://langfuse:3000"
      PROMETHEUS_PUSHGATEWAY: "http://prometheus:9090"
    ports:
      - "8000:8000"

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:
```

### Quick start:

```bash
# Deploy
docker-compose up -d

# Check status
docker-compose ps

# Logs
docker-compose logs -f langfuse

# Access:
# - Langfuse: http://localhost:3000
# - Grafana: http://localhost:3001 (admin/admin)
# - Prometheus: http://localhost:9090
# - Your app: http://localhost:8000

# Shutdown
docker-compose down
```

---

## 📚 Awesome Lists

### Agent Monitoring (Primary)

#### Zero-Code Agent Tracing
- [abidex](https://github.com/abidex-io/abidex) - Zero-code OpenTelemetry agent tracing (CrewAI, LangGraph, LlamaIndex)
- [OpenLLMetry](https://github.com/traceloop/openllmetry) - OpenTelemetry SDK for LLMs & agents
- [LangSmith](https://www.langchain.com/langsmith) - Deep LangChain/LangGraph debugging
- [Trace Loop](https://github.com/traceloop/traceloop-sdk-python) - Lightweight OTel for agents

#### Agent Frameworks
- [CrewAI](https://github.com/joaomdmoura/crewai) - Multi-agent orchestration framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Graph-based agent workflows
- [LlamaIndex](https://www.llamaindex.ai/) - RAG + agent pipelines
- [Pydantic AI](https://github.com/pydantic/pydantic-ai) - Lightweight agent framework

### OTLP Backends (Trace Storage & Visualization)

- [SigNoz](https://github.com/SigNoz/signoz) - Open-source OTLP backend (self-hosted)
- [Uptrace](https://uptrace.dev) - Managed OTLP SaaS
- [Jaeger](https://www.jaegertracing.io/) - Distributed tracing & span visualization
- [Grafana Tempo](https://grafana.com/oss/tempo/) - OSS trace backend

### Traditional Observability (Complementary)

#### Tracing & Observability
- [Langfuse](https://langfuse.com) - Prompt management + evals + sessions
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) - Evaluation + drift detection
- [Helicone](https://helicone.ai) - Cost proxy for OpenAI/Anthropic
- [Braintrust](https://www.braintrust.dev) - Evals + experiments + collaboration

#### Evaluation Frameworks
- [DeepEval](https://github.com/confident-ai/deepeval) - 50+ metrics (hallucination, bias, faithfulness)
- [Ragas](https://github.com/explodinggradients/ragas) - RAG evaluation metrics
- [TruLens](https://www.trulens.org/) - Feedback functions & explainability
- [ARES](https://github.com/stanford-futuredata/ares) - Query optimizer for RAG

#### Cost & Metrics
- [Helicone](https://helicone.ai) - Cost tracking (proxy-based)
- [Token Counter](https://github.com/openai/tiktoken) - Token counting
- [Prometheus](https://prometheus.io) - Metrics collection
- [Grafana](https://grafana.com) - Visualization & alerting

#### Embeddings & Drift
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) - Embedding drift visualization
- [WhyLabs](https://whylabs.ai) - Data quality monitoring
- [Evidently AI](https://www.evidentlyai.com/) - Drift detection

### Best Practices & Research

- [abidex Documentation](https://github.com/abidex-io/abidex/tree/main/docs)
- [OpenTelemetry for Python](https://opentelemetry.io/docs/instrumentation/python/)
- [SigNoz LLM Monitoring Guide](https://signoz.io/blog/llm-monitoring/)
- [Langfuse LLM Observability Guide](https://langfuse.com/docs/guides)
- [Arize "What is LLM Observability?"](https://arize.com/blog/what-is-llm-monitoring-and-observability)
- [Confident AI Top Eval Tools](https://www.confident-ai.com/blog/)
- [LangChain Agent Debugging](https://docs.smith.langchain.com/)

---

## 🚀 Resources & References

### abidex (Zero-Code Agent Tracing)

- [abidex GitHub](https://github.com/abidex-io/abidex) - Main repository & documentation
- [abidex PyPI](https://pypi.org/project/abidex/) - Package & installation
- [abidex Documentation](https://abidex.io/docs) - Setup guide & API reference
- [abidex CLI Guide](https://abidex.io/docs/cli) - Trace inspection & export commands

### Agent Framework Documentation

- [CrewAI Docs](https://docs.crewai.com/) - Multi-agent orchestration framework
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Graph-based agents
- [LlamaIndex Agent Guide](https://docs.llamaindex.ai/en/stable/module_guides/agents/) - RAG + agents
- [Pydantic AI Documentation](https://github.com/pydantic/pydantic-ai) - Lightweight agent builder

### OTLP Backends & OpenTelemetry

- [SigNoz Setup Guide](https://signoz.io/docs/install/docker-compose/) - Docker deployment
- [Uptrace Getting Started](https://uptrace.dev/get/started.html) - Managed OTLP backend
- [Jaeger Installation](https://www.jaegertracing.io/docs/getting-started/) - Distributed tracing
- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/) - OTel SDK

### Evaluation & Quality Frameworks

- [DeepEval Docs](https://docs.confident-ai.com/) - 50+ metrics & LLM-as-judge
- [Ragas Documentation](https://docs.ragas.io/) - RAG evaluation metrics
- [TruLens Docs](https://www.trulens.org/trulens_eval/) - Feedback functions
- [Langfuse Evals](https://langfuse.com/docs/scores/overview) - Prompt management + evals

### Key Articles & Guides

- **"Agent Observability with OpenTelemetry"** (OpenTelemetry blog)
- **"Zero-Code Tracing for CrewAI & LangGraph"** (abidex docs)
- **"Best Practices for Multi-Agent Monitoring"** (SigNoz blog)
- **"Hallucination Detection in Agent Chains"** (DeepEval blog)
- **"Self-Hosted vs Managed OTLP Backends"** (SigNoz comparison)
- **"Cost Tracking in Multi-Agent Systems"** (Helicone blog)

### Community & Support

- [abidex GitHub Discussions](https://github.com/abidex-io/abidex/discussions)
- [LangChain Discord Community](https://discord.gg/langchain)
- [OpenTelemetry Slack](https://cloud-native.slack.com/archives/C015NRPQ13C)
- [SigNoz Community Slack](https://signoz.io/community-slack/)

### Code Examples & Repositories

- [abidex Examples](https://github.com/abidex-io/abidex/tree/main/examples) - CrewAI, LangGraph samples
- [SigNoz Agent Monitoring Setup](https://github.com/SigNoz/signoz/tree/main/examples) - Docker examples
- [DeepEval Cookbook](https://github.com/confident-ai/deepeval/tree/main/examples) - Eval patterns
- [Langfuse SDK Examples](https://github.com/langfuse/langfuse/tree/main/examples)
- [LlamaIndex Observability Examples](https://github.com/run-llama/llama_index/tree/main/examples)

---

## 📝 Contributing

Have a tool, pattern, or best practice to add? Submit a PR!

### Guidelines
1. Add tools in alphabetical order within sections
2. Include GitHub URL, key features, and licensing info
3. For code examples, ensure they follow patterns in this repo
4. Test Docker Compose setup before submitting

---

## 📄 License

MIT License - Feel free to use in your projects!

---

## 🙏 Acknowledgments

Built with insights from the LLM observability community, including contributions from:
- Langfuse team
- Arize Phoenix community
- DeepEval/Confident AI
- OpenTelemetry contributors
- LangChain ecosystem

---

**Last updated:** March 2026 | Follow for updates: [Watch on GitHub](https://github.com/goabiaryan/awesome-observability)
