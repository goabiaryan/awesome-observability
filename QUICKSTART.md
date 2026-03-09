# Quick Start Guide: Agent Observability with abidex

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose
- OpenAI/Anthropic API key
- 2-4 GB RAM

## 🚀 60-Second Setup (abidex + SigNoz)

### Step 1: Clone & Install

```bash
cd awesome-observability

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Start Infrastructure

```bash
docker-compose up -d

# Wait for services to be healthy (~1 min)
docker-compose ps
```

### Step 3: Configure Environment

```bash
cp configs/.env.template .env

# Edit .env with your API keys:
# - OPENAI_API_KEY=sk-...
# - OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 (already set)
```

### Step 4: Run Your First Agent

```bash
python examples/05_crewai_with_abidex.py
```

### Step 5: View Traces in SigNoz

Open http://localhost:3301 and browse the traces!

## 🔍 What You Get Automatically

With abidex (zero-code setup):

✅ **Agent Tracing** - All agent steps traced automatically
✅ **GenAI Attributes** - role, goal, backstory, task captured
✅ **Tool Call Tracking** - Tool latency and errors traced
✅ **Multi-Agent Coordination** - See how agents work together
✅ **OTLP Export** - Traces sent to SigNoz/Uptrace/Jaeger

No decorators, no middleware, no code instrumentation!

## 🛠️ Configuration

### Environment Variables

**Required:**
```bash
OPENAI_API_KEY=sk-...
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=my-agent-app
```

**Optional:**
```bash
LANGFUSE_ENABLED=false
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...

PHOENIX_ENABLED=false
PHOENIX_HOST=http://localhost:6006
```

### Using Different OTLP Backends

**SigNoz (Self-Hosted, Recommended):**
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
docker-compose up -d
# Visit http://localhost:3301
```

**Uptrace (Managed):**
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.uptrace.dev
OTEL_EXPORTER_OTLP_HEADERS="uptrace-dsn=<your_dsn>"
```

**Jaeger (Local Tracing):**
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
docker-compose up -d
# Visit http://localhost:16686
```

## 💻 Integration Examples

### 1. CrewAI Crew (Multi-Agent)

```python
import abidex
from crewai import Agent, Task, Crew

abidex.instrument_crew()

research_agent = Agent(
    role="Researcher",
    goal="Research trends",
    backstory="Expert researcher"
)

crew = Crew(
    agents=[research_agent],
    tasks=[...],
    verbose=True
)

result = crew.kickoff()

abidex.trace.print_summary()
abidex.trace.export_to_opentelemetry()
```

Run: `python examples/05_crewai_with_abidex.py`

### 2. LangGraph Agent

```python
import abidex
from langgraph.graph import StateGraph

abidex.instrument_langgraph()

workflow = StateGraph(state_schema)
workflow.add_node("agent_1", agent_1_func)
workflow.add_node("agent_2", agent_2_func)

graph = workflow.compile()
result = graph.invoke({"input": "solve X"})

abidex.trace.print_summary()
```

Run: `python examples/06_langgraph_with_abidex.py`

### 3. Using Optional Langfuse (for Prompts)

```python
import abidex
from langfuse.callback_handler import CallbackHandler

abidex.instrument_crew()
langfuse_handler = CallbackHandler()

crew = Crew(
    agents=[...],
    tasks=[...],
    callbacks=[langfuse_handler]
)
```

## 🎯 Common Tasks

### View Traces in SigNoz

```
1. Go to http://localhost:3301
2. Click "Traces" on the left
3. Filter by service: llm-agent-app
4. Click any trace to see:
   - Agent role, goal, backstory
   - Task execution spans
   - Tool calls and latency
   - Token usage per agent
```

### Export Traces to File

```python
import abidex

traces = abidex.trace.export_all()
with open("traces.json", "w") as f:
    json.dump(traces, f, indent=2)
```

### Run Batch Evaluation

```python
from eval_utils import EvalPipeline

pipeline = EvalPipeline(metrics=["hallucination", "faithfulness"])

for record in test_cases:
    scores = await pipeline.evaluate(
        output=record["output"],
        context=record["context"],
        question=record["question"]
    )
    print(f"Hallucination: {scores['hallucination_score']}")
```

### Monitor Agent Iterations

```python
import abidex

@abidex.observe
def run_agents_with_monitoring():
    iterations = 0
    while iterations < 10 and not task_complete:
        result = agent.step()
        iterations += 1
        
    abidex.trace.log_info(
        f"Completed {iterations} iterations",
        {"iterations": iterations}
    )
```

## 🚨 Alerts & Monitoring

### Pre-configured Alerts

Edit `alerts.yml` to customize:

```yaml
- alert: HighHallucinationRate
  expr: llm_hallucination_score < 0.80
  for: 5m
  labels:
    severity: warning
```

### Set Budget Limits

```python
# In your app
from observability import CostTracker

daily_budget = 100.0
spent_today = get_daily_cost()

if spent_today > daily_budget * 0.8:
    logger.warning("Budget 80% used")
    # Reduce model quality to save costs
```

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Manual Testing
```bash
# Test Langfuse connection
python -c "from observability import create_langfuse_client; client = create_langfuse_client(); print('✓ Connected')"

# Test evaluation
python -c "from eval_utils import EvalPipeline; p = EvalPipeline(['hallucination']); print('✓ Ready')"
```

## 🐛 Troubleshooting

### Langfuse not responsive
```bash
# Check container
docker-compose ps langfuse

# View logs
docker-compose logs langfuse

# Restart
docker-compose restart langfuse
```

### Cannot connect to OpenAI
```bash
# Verify key
echo $OPENAI_API_KEY

# Test connection
python -c "import openai; openai.ChatCompletion.create(...)"
```

### Grafana showing no data
```bash
# Check Prometheus scrape targets
curl http://localhost:9090/api/targets

# Check metrics exist
curl http://localhost:9090/api/query?query=llm_requests_total
```

## 📚 Further Learning

- [Langfuse Docs](https://langfuse.com/docs)
- [Arize Phoenix README](https://github.com/Arize-ai/phoenix)
- [DeepEval Documentation](https://docs.confident-ai.com/)
- [Ragas Setup Guide](https://docs.ragas.io/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

## 🆘 Getting Help

1. Check existing issues: https://github.com/goabiaryan/awesome-observability/issues
2. Read troubleshooting above
3. Consult tool-specific documentation
4. Submit detailed issue with logs and config

## Next Steps

- [ ] Set up in development environment
- [ ] Configure with your LLM provider
- [ ] Integrate with your application
- [ ] Create custom Grafana dashboards
- [ ] Set up alerting & notifications
- [ ] Deploy to production (see docker-compose for security checklist)

---

**Happy Observing! 🔍**
