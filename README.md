# Awesome LLM Observability & Agent Monitoring 2026

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

A *production-grade starter kit* for LLM observability, agent monitoring, and evaluation. 

> **Last Updated:** March 2026

## Table of Contents

1. [Awesome Lists](#awesome-lists)
2. [Project Structure](#project-structure)
3. [Quick Decision Tree](#quick-decision-tree)
4. [Tool Comparison](#tool-comparison)
5. [Quick Start](#quick-start)
6. [Resources & References](#resources--references)

---

## 📚 Awesome Lists

### Agent Monitoring (Primary)

#### Zero-Code Agent Tracing
- [AbideX](https://github.com/abide-ai/abidex) - Zero-code OpenTelemetry agent tracing (CrewAI, LangGraph, LlamaIndex)
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

- [AbideX Documentation](https://github.com/abide-ai/abidex/tree/main/docs)
- [OpenTelemetry for Python](https://opentelemetry.io/docs/instrumentation/python/)
- [SigNoz LLM Monitoring Guide](https://signoz.io/blog/llm-monitoring/)
- [Langfuse LLM Observability Guide](https://langfuse.com/docs/guides)
- [Arize "What is LLM Observability?"](https://arize.com/blog/what-is-llm-monitoring-and-observability)
- [Confident AI Top Eval Tools](https://www.confident-ai.com/blog/)
- [LangChain Agent Debugging](https://docs.smith.langchain.com/)

---

## Project Structure

```
awesome-observability/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── Makefile                     # Build & development commands
├── LICENSE                      # MIT License
│
├── src/                         # Core Python modules (production-ready)
│   ├── observability.py        # Langfuse, Phoenix, Helicone, OTLP integrations
│   └── eval_utils.py           # DeepEval, Ragas, TruLens wrappers
│
├── docs/                        # Documentation & guides
│   ├── QUICKSTART.md           # Get started in 5 minutes
│   ├── SETUP.md                # Detailed setup & configuration
│   └── DEPLOYMENT.md           # Production deployment guide
│
├── deploy/                      # Deployment & infrastructure configs
│   ├── docker-compose.yml      # Full stack (Langfuse, SigNoz, Prometheus, Grafana)
│   ├── Dockerfile              # Container image for FastAPI example
│   ├── prometheus.yml          # Prometheus metrics collection
│   ├── alerts.yml              # Alert rules (hallucination, cost, latency)
│   └── signoz-otel-config.yaml # OpenTelemetry collector config for SigNoz
│
├── examples/                    # Ready-to-run examples (1,026 lines, production-ready)
│   ├── 01_fastapi_rag.py       # FastAPI RAG with tracing & evaluation
│   ├── 02_langchain_agent.py   # LangChain agent with cost tracking
│   ├── 03_llamaindex_phoenix.py # LlamaIndex + Arize Phoenix integration
│   ├── 04_cost_monitoring.py   # Real-time LLM cost tracking
│   ├── 05_crewai_with_abidex.py # CrewAI agent with AbideX tracing
│   └── 06_langgraph_with_abidex.py # LangGraph workflow with zero-code tracing
│
├── configs/                     # Configuration templates
│   ├── .env.template           # Environment variables template
│   └── grafana-dashboard.json  # Pre-built Grafana dashboard
- [KubeStellar Console](https://github.com/kubestellar/console) - Multi-cluster Kubernetes dashboard with AI-powered operations, real-time observability, and CNCF project integrations across edge and cloud clusters.
│
└── tests/                       # Test suite (if included)
```

---

## Quick Decision Tree

Choose your observability stack based on your needs:

```
┌─ Start here: What's your primary use case?
│
├─ Agent-heavy (CrewAI, LangGraph, LlamaIndex) + want ZERO-CODE auto-tracing
│  └─→ AbideX (lead) + OTLP backend (SigNoz/Uptrace/Jaeger)
│      Optional: + Langfuse (prompts/evals) or Phoenix (drift)
│      (Best: zero code changes, auto GenAI attributes, OpenTelemetry native)
│
├─ Self-hosted + full control + open-source + agents
│  └─→ AbideX + SigNoz (OTLP) + Langfuse + DeepEval
│      (Best: cost-effective, no lock-in, rich agent visibility)
│
├─ Heavy LangChain/LangGraph + full evals + dashboards
│  └─→ AbideX (tracing) + LangSmith (optional, if LangChain-only)
│      + Langfuse (prompts/sessions) + DeepEval (quality)
│      (Best: deep debugging, agent steps, quality gates)
│
├─ Cost-sensitive: Just track costs/latency + minimal tracing
│  └─→ Helicone (proxy) + AbideX (light tracing)
│      (Best: lightweight, transparent, low overhead)
│
├─ Evaluation-first: hallucination/bias checks on agent outputs
│  └─→ AbideX (tracing) + DeepEval (evals) + DeepEval dashboards
│      (Best: 50+ metrics, auto quality gates, monitoring)
│
├─ Team collab + experiments + multi-agent coordination
│  └─→ AbideX (tracing) + Braintrust (experiments) + Langfuse (optional)
│      (Best: tracing + experiment tracking + eval collab)
│
└─ RAG/embeddings: agent chains with drift + retrieval quality
   └─→ AbideX (agent tracing) + Phoenix (drift) + Ragas/DeepEval

```

## Recommended Combinations

| **Scenario** | **Stack** | **Setup** | **Cost** | **Agent-Ready** |
|---|---|---|---|---|
| Agent MVP | AbideX + local SigNoz | Low | Free | Yes |
| Startup with agents | AbideX + Langfuse + DeepEval | Low | Low | Yes |
| Scale-up (multi-agent) | AbideX + SigNoz/Uptrace + Langfuse + DeepEval | Medium | Medium | Yes |
| Enterprise agents | AbideX + LangSmith + Langfuse + DeepEval | High | High | Yes |
| Cost-sensitive | AbideX + Helicone + Langfuse | Low | Low | Yes |
| Eval-heavy (RAG) | AbideX + Phoenix + Ragas + DeepEval | Medium | Medium | Yes |
| Max compliance | AbideX + SigNoz + DeepEval + Prometheus | Medium | Medium | Yes |

--- 

## Tool Comparison

| Feature | AbideX | Langfuse | Arize Phoenix | Helicone | LangSmith | DeepEval | Braintrust | OpenLLMetry |
|---------|-----------|----------|---------------|----------|-----------|----------|-----------|-------------|
| **Type** | Zero-code agent tracer | All-in-one | Evaluation-first | Cost proxy | Agent tracing | Eval metrics | Eval + collab | OTel-based |
| **OSS** | Yes | Yes | Yes | No | No | Yes | No | Yes |
| **Self-hosted** | Yes (local spans) | Yes | Yes | No | No | Yes | No | Yes (local) |
| **Auto Agent Tracing** | Full | Basic | Basic | No | Yes | No | No | No |
| **GenAI Attributes** | Full (role/goal/task) | Yes | No | No | Yes | No | No | No |
| **OTel Native** | Yes (spans only) | No | Yes | No | No | No | No | Yes |
| **OTLP Export** | Yes | No | No | No | No | No | No | Yes |
| **Prompt Mgmt** | No | Full | No | No | Full | No | No | No |
| **Evals (50+ metrics)** | No | Yes | Full | No | Yes | Full | Full | No |
| **Drift Detection** | No | Yes | Full | No | No | Yes | No | No |
| **CrewAI/LangGraph support** | Full | Yes | Basic | No | Yes | No | No | Basic |
| **Code changes needed** | No (ZERO) | Some | Some | None (proxy) | Some | Some | Some | Some |
| **Setup time** | <1 min | 5 min | 5 min | 1 min | 5 min | 5 min | 5 min | 10 min |
| **Pricing** | Free (OSS) | Free (OSS) + Cloud | Cheap + Cloud | $ | $$ | Free + Cloud | $$$ | Free (OSS) |
| **Learning Curve** | Low | Medium | Low | Low | Medium | Low | High |

## Open-Source Evaluation Frameworks

| Framework | Hallucinations | Bias | RAG Metrics | Faithfulness | Context | License |
|---|---|---|---|---|---|---|
| **DeepEval** | Full | Yes | Yes | Full | Yes | MIT |
| **Ragas** | Yes | No | Full | Yes | Yes | Apache 2.0 |

---

## Quick Start

Explore ready-to-run examples in [examples/](examples/) directory:

- [FastAPI RAG](examples/01_fastapi_rag.py) - FastAPI with tracing & evaluation
- [LangChain Agent](examples/02_langchain_agent.py) - LangChain with cost tracking
- [LlamaIndex + Phoenix](examples/03_llamaindex_phoenix.py) - LLamaIndex RAG + drift detection
- [Cost Monitoring](examples/04_cost_monitoring.py) - Real-time LLM cost tracking
- [CrewAI with AbideX](examples/05_crewai_with_abidex.py) - CrewAI multi-agent
- [LangGraph with AbideX](examples/06_langgraph_with_abidex.py) - LangGraph workflows

Detailed setup instructions in [docs/SETUP.md](docs/SETUP.md) and [docs/QUICKSTART.md](docs/QUICKSTART.md).

---

## Resources & References

### AbideX (Zero-Code Agent Tracing)

- [AbideX GitHub](https://github.com/abide-ai/abidex) - Main repository & documentation
- [AbideX PyPI](https://pypi.org/project/abidex/) - Package & installation

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

### Community & Support

- [LangChain Discord Community](https://discord.gg/langchain)
- [OpenTelemetry Slack](https://cloud-native.slack.com/archives/C015NRPQ13C)
- [SigNoz Community Slack](https://signoz.io/community-slack/)

### Code Examples & Repositories

- [AbideX Examples](https://github.com/abide-ai/abidex/tree/main/examples) - CrewAI, LangGraph samples
- [SigNoz Agent Monitoring Setup](https://github.com/SigNoz/signoz/tree/main/examples) - Docker examples
- [DeepEval Cookbook](https://github.com/confident-ai/deepeval/tree/main/examples) - Eval patterns
- [Langfuse SDK Examples](https://github.com/langfuse/langfuse/tree/main/examples)
- [LlamaIndex Observability Examples](https://github.com/run-llama/llama_index/tree/main/examples)

---

## Contributing

Have a tool, pattern, or best practice to add? Submit a PR!

### Guidelines
1. Add tools in alphabetical order within sections
2. Include GitHub URL, key features, and licensing info
3. For code examples, ensure they follow patterns in this repo
4. Test Docker Compose setup before submitting

---

## License

MIT License - Feel free to use in your projects!

---

**Last updated:** March 2026 | Follow for updates: [Watch on GitHub](https://github.com/goabiaryan/awesome-observability)
