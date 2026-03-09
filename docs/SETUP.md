# Awesome LLM Observability - Complete Setup Guide

A production-ready starter kit for LLM observability, monitoring, and evaluation.

## 📁 Project Structure

```
awesome-observability/
├── README.md                    # Main awesome list & tool comparison
├── QUICKSTART.md               # 30-second quick start guide
├── DEPLOYMENT.md               # Docker & Kubernetes deployment guides
├── 
├── observability.py            # Core observability client (Langfuse, Phoenix, etc.)
├── eval_utils.py              # Evaluation pipeline (DeepEval, Ragas, TruLens)
├── requirements.txt           # Python dependencies
├── 
├── docker-compose.yml         # Self-hosted infrastructure (Langfuse, Prometheus, Grafana)
├── Dockerfile                 # Application container
├── prometheus.yml             # Prometheus configuration
├── alerts.yml                 # Alert rules (hallucination, cost, errors)
├── 
├── examples/
│   ├── 01_fastapi_rag.py              # FastAPI RAG with tracing & evaluation
│   ├── 02_langchain_agent.py          # LangChain agent with Langfuse
│   ├── 03_llamaindex_phoenix.py       # LlamaIndex + Phoenix drift detection
│   └── 04_cost_monitoring.py          # Cost tracking & budget monitoring
├── 
├── configs/
│   ├── .env.template                  # Environment variable template
│   └── grafana-dashboard.json         # Grafana dashboard definition
│ 
├── tests/
│   └── test_observability.py          # Unit tests
└── 
└── LICENSE
```

## 🎯 Quick Selection Matrix

Use this to choose your observability stack:

| Your Situation | Recommended Stack | Setup Time | Cost |
|---|---|---|---|
| **MVP/Startup** | Langfuse (self-hosted) + DeepEval | 15 min | Free |
| **Scale-up** | Langfuse + Phoenix + DeepEval + Prometheus | 45 min | $0-100/mo |
| **Enterprise LangChain** | LangSmith + Langfuse + DeepEval | 30 min | $100-1000/mo |
| **Cost-sensitive SaaS** | Helicone + Langfuse + Ragas | 20 min | $0-50/mo |
| **RAG-heavy** | Phoenix + Ragas + Braintrust | 1 hour | $0-200/mo |
| **Maximum Compliance** | Self-hosted Langfuse + Prometheus + Grafana | 1 hour | Free |

## ⚡ Installation Methods

### Method 1: Local Development (5 minutes)

```bash
# Clone repo
git clone https://github.com/goabiaryan/awesome-observability
cd awesome-observability

# Setup Python
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp configs/.env.template .env
# Edit .env with your OpenAI key

# Start infrastructure
docker-compose up -d

# Verify
curl http://localhost:3000  # Langfuse health check
curl http://localhost:9090  # Prometheus health check
curl http://localhost:3001  # Grafana health check
```

### Method 2: Docker Only (3 minutes)

```bash
# Just the observability infrastructure
docker-compose up -d langfuse postgres prometheus grafana redis

# Then in your app:
from observability import create_langfuse_client
client = create_langfuse_client()  # Automatically connects to localhost:3000
```

### Method 3: Cloud Only (2 minutes)

```bash
# Sign up for Langfuse Cloud at https://langfuse.com
# Get API keys from dashboard
# Set environment variables:
export LANGFUSE_PUBLIC_KEY="your-key"
export LANGFUSE_SECRET_KEY="your-secret"
export LANGFUSE_HOST="https://cloud.langfuse.com"

# Install & run
pip install langfuse deepeval
python your_app.py
```

## 🚀 Integration in 3 Steps

### Step 1: Initialize Client

```python
from observability import create_langfuse_client, instrument_openai

# Create client
client = create_langfuse_client()

# Auto-instrument OpenAI
instrument_openai()
```

### Step 2: Trace Your Code

```python
# Option A: Automatic (OpenAI calls)
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[...]
)
# ✓ Automatically traced to Langfuse

# Option B: Manual trace
with client.trace("my_function"):
    result = process_data()
```

### Step 3: Add Evaluation

```python
from eval_utils import EvalPipeline

pipeline = EvalPipeline(metrics=["hallucination", "faithfulness"])
scores = await pipeline.evaluate(
    output=llm_response,
    context=retrieved_docs,
    question=user_question
)
```

## 📊 Monitoring at a Glance

### Langfuse (Traces & Prompts)
- View all API calls and their latency
- Manage prompt versions & A/B test
- Session tracking for conversations
- Cost attribution by model

**URL**: http://localhost:3000

### Prometheus (Raw Metrics)
- Token usage over time
- Request latency percentiles
- Error rates
- Cost trends

**URL**: http://localhost:9090  
**Query example**: `rate(llm_requests_total[5m])`

### Grafana (Dashboards & Alerts)
- Beautiful time-series visualization
- Cost breakdown by model
- Quality score trends
- Alert notifications

**URL**: http://localhost:3001

### Jaeger (Distributed Tracing - Optional)
- Detailed request flows
- Service dependencies
- Latency breakdown

**URL**: http://localhost:16686

## 🔍 Commonly Used Metrics

```
# Request metrics
llm_requests_total              # Total requests by model
llm_tokens_total               # Tokens used (input/output)
llm_latency_seconds            # Request duration
llm_cost_total                 # Cumulative cost

# Quality metrics
llm_hallucination_score        # Hallucination likelihood (0-1)
llm_answer_relevancy_score     # Answer quality (0-1)
llm_quality_gate_pass_rate     # % passing quality checks

# Error metrics
llm_errors_total               # Failed requests
llm_error_rate                 # % of requests failing
```

## 🚨 Pre-configured Alerts

Edit `alerts.yml` to customize:

```yaml
# Hallucination detection
- alert: HighHallucinationRate
  expr: llm_hallucination_score < 0.80
  for: 5m
  
# Cost spike detection
- alert: CostSpike
  expr: rate(llm_cost_total[5m]) > 100

# Error rate monitoring
- alert: HighErrorRate
  expr: rate(llm_errors_total[5m]) > 0.05
```

## 💰 Cost Management

### Track Costs in Real-time

```python
from examples.cost_monitoring import CostOptimizedLLM

llm = CostOptimizedLLM(max_daily_budget=100.0)
response = llm.call_openai("Your question")

stats = llm.get_report()
print(f"Today's cost: {stats['today_cost']}")
print(f"Remaining: {stats['remaining_budget']}")
```

### Auto-scaling Model Selection

```python
# Automatically choose cheaper models if budget running low
model = llm.choose_model(quality_needed="high")  # Returns gpt-4 or gpt-3.5-turbo based on budget
```

## 🧪 Testing Quality

### Run Batch Evaluation

```python
from eval_utils import batch_evaluate_dataset

results = await batch_evaluate_dataset(
    dataset=[
        {"question": "What is X?", "answer": "...", "context": "..."},
        {"question": "What is Y?", "answer": "...", "context": "..."},
    ],
    metrics=["hallucination", "faithfulness", "answer_relevancy"],
    output_file="eval_results.json"
)

print(f"Pass rate: {results['metrics']['hallucination']['pass_rate']}")
```

### Detect Hallucinations

```python
from eval_utils import HallucinationDetector

detector = HallucinationDetector(threshold=0.85)
if await detector.is_hallucinating(response, context):
    logger.warning("Hallucination detected!")
```

## 🔐 Security Best Practices

✅ **Do**:
- Store API keys in environment variables
- Use `.env` file locally (gitignored)
- Enable HTTPS in production
- Use network policies to restrict access
- Rotate secrets regularly
- Enable database encryption

❌ **Don't**:
- Commit `.env` to git
- Use hardcoded credentials
- Expose Prometheus/Grafana without auth
- Log sensitive information
- Leave default passwords unchanged

## 📈 Performance Tips

### 1. Batch Evaluation for Speed
```python
# Slower (sequential)
for item in items:
    score = await eval_pipeline.evaluate(item)

# Faster (parallel)
results = await asyncio.gather(*[
    eval_pipeline.evaluate(item) for item in items
])
```

### 2. Cache Retrieved Documents
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def retrieve_documents(query):
    # Only retrieve once per unique query
    return vector_db.search(query)
```

### 3. Use Streaming for Long Outputs
```python
# For long generations, use streaming to start evaluation sooner
for chunk in llm.stream(prompt):
    # Start evaluation on first chunks
    partial_score = eval_pipeline.quick_eval(chunk)
```

## 🛠️ Troubleshooting

### Services Not Starting?
```bash
# Check what's running
docker-compose ps

# View logs
docker-compose logs -f langfuse

# Restart service
docker-compose restart langfuse
```

### Cannot Connect to OpenAI?
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test connection
python -c "import openai; openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': 'test'}])"
```

### Grafana Not Showing Data?
```bash
# Check Prometheus targets
curl http://localhost:9090/api/targets

# Verify metrics exist
curl http://localhost:9090/api/query?query=llm_requests_total
```

## 📚 Learning Resources

### Official Docs
- [Langfuse Documentation](https://langfuse.com/docs)
- [Arize Phoenix README](https://github.com/Arize-ai/phoenix)
- [DeepEval Docs](https://docs.confident-ai.com/)
- [Ragas Setup](https://docs.ragas.io/)

### Comparison Articles
- "Best LLM Observability Tools 2026" (Firecrawl)
- "Top 5 LLM Evaluation Frameworks" (Confident AI)
- "Self-Hosted vs Cloud Observability" (Langfuse Blog)

### Community
- [Langfuse Discord](https://discord.gg/langfuse)
- [LangChain Community](https://discord.gg/langchain)
- [Arize Community](https://gitter.im/Arize-ai/community)

## 🎓 Example Workflows

### Workflow 1: Basic LLM App Monitoring

```
1. Init Langfuse client
2. Instrument OpenAI calls
3. Monitor costs with Prometheus
4. Create Grafana dashboard
5. Set up alerts for errors
```

### Workflow 2: RAG Quality Assurance

```
1. Setup evaluation pipeline (DeepEval + Ragas)
2. Run batch evaluation on test suite
3. Track quality metrics over time
4. Alert on hallucination spikes
5. A/B test model changes
```

### Workflow 3: Agent Observability

```
1. Use Langfuse callback handler
2. Track agent steps and tool calls
3. Monitor token usage per tool
4. Evaluate final outputs
5. Optimize prompt based on failures
```

## 🚀 Next Steps

1. **Start Local** (5 minutes)
   - Run `docker-compose up`
   - Try one of the examples
   
2. **Integrate** (30 minutes)
   - Add observability to your app
   - Set up evaluation pipeline
   
3. **Monitor** (1 hour)
   - Create custom Grafana dashboards
   - Set up alerting rules
   
4. **Deploy** (2-4 hours)
   - Choose deployment platform (Docker/K8s)
   - Configure for production
   - Set up backups & monitoring

## 💡 Tips & Tricks

### Organize Traces by Project
```python
trace = client.trace(
    name="rag_query",
    user_id="user_123",
    metadata={"project": "my_project", "version": "1.0"}
)
```

### Compare Evaluations Over Time
```python
# Save evaluations with timestamps
# Use Prometheus for historical analysis
# Create time-series graphs in Grafana
```

### Cost Optimization
```python
# Use cheaper models for non-critical tasks
# Implement caching to reduce API calls
# Batch process similar queries together
```

## 📞 Getting Help

1. Check [README.md](README.md) for tool comparison
2. See [QUICKSTART.md](QUICKSTART.md) for quick setup
3. Review [examples/](examples/) for code patterns
4. Check [alerts.yml](alerts.yml) for monitoring patterns
5. Check docs of each tool (Langfuse, Phoenix, etc.)

## 🤝 Contributing

Contributions welcome! Please:

1. Add new tools to README.md with comparison table
2. Create examples for new integration patterns
3. Improve documentation and guides
4. Share your use cases and best practices

## 📄 License

MIT - Use freely in your projects!

---

**Start observing your LLMs in 5 minutes! 👉 [QUICKSTART.md](QUICKSTART.md)**
