# Makefile for LLM Observability Project
# Simplifies common commands

.PHONY: help install setup start stop restart logs clean test eval run-example deploy

help:
	@echo "LLM Observability - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install Python dependencies"
	@echo "  make setup            Setup environment (.env file)"
	@echo ""
	@echo "Docker Management:"
	@echo "  make start            Start all services (docker-compose up -d)"
	@echo "  make stop             Stop all services"
	@echo "  make restart          Restart all services"
	@echo "  make logs             View live logs from all services"
	@echo "  make logs-langfuse    View Langfuse logs"
	@echo "  make status           Show service status (ps)"
	@echo "  make clean            Stop and remove all containers/volumes"
	@echo ""
	@echo "Development:"
	@echo "  make test             Run tests"
	@echo "  make eval             Run batch evaluation"
	@echo "  make run-example1     Run FastAPI RAG example"
	@echo "  make run-example2     Run LangChain agent example"
	@echo "  make run-example3     Run LlamaIndex Phoenix example"
	@echo "  make run-example4     Run cost monitoring example"
	@echo ""
	@echo "Utility:"
	@echo "  make health           Check all service health"
	@echo "  make install-hooks    Install git pre-commit hooks"
	@echo "  make metrics          Show Prometheus metrics"
	@echo ""
	@echo "Access:"
	@echo "  Langfuse:  http://localhost:3000"
	@echo "  Grafana:   http://localhost:3001 (admin/admin)"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Jaeger:    http://localhost:16686"

# ============================================================================
# Installation & Setup
# ============================================================================

install:
	@echo "Installing Python dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

setup:
	@echo "Setting up environment..."
	@test -f .env && echo "✓ .env already exists" || (cp deploy/.env.template .env && echo "✓ Created .env from template")
	@echo ""
	@echo "⚠️  Please edit .env with your API keys:"
	@echo "   OPENAI_API_KEY=sk-..."
	@echo "   LANGFUSE_PUBLIC_KEY=..."
	@echo "   LANGFUSE_SECRET_KEY=..."
	@echo ""

venv:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "✓ Virtual environment created"
	@echo "Activate with: source venv/bin/activate"

# ============================================================================
# Docker Management
# ============================================================================

start:
	@echo "Starting services..."
	docker-compose -f deploy/docker-compose.yml up -d
	@echo "✓ Services started"
	@echo ""
	@echo "Waiting for services to be ready..."
	@sleep 10
	@make health

stop:
	@echo "Stopping services..."
	docker-compose -f deploy/docker-compose.yml stop
	@echo "✓ Services stopped"

restart: stop start

logs:
	@echo "Showing live logs (Ctrl+C to exit)..."
	docker-compose -f deploy/docker-compose.yml logs -f

logs-langfuse:
	docker-compose -f deploy/docker-compose.yml logs -f langfuse

logs-prometheus:
	docker-compose -f deploy/docker-compose.yml logs -f prometheus

logs-grafana:
	docker-compose -f deploy/docker-compose.yml logs -f grafana

status:
	@echo "Service Status:"
	@docker-compose -f deploy/docker-compose.yml ps

health:
	@echo "Checking service health..."
	@echo ""
	@echo -n "Langfuse: "
	@curl -s http://localhost:3000/health > /dev/null && echo "✓ Running" || echo "✗ Down"
	@echo -n "Prometheus: "
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "✓ Running" || echo "✗ Down"
	@echo -n "Grafana: "
	@curl -s http://localhost:3001/api/health > /dev/null && echo "✓ Running" || echo "✗ Down"
	@echo -n "PostgreSQL: "
	@docker-compose -f deploy/docker-compose.yml exec -T postgres pg_isready -U langfuse > /dev/null 2>&1 && echo "✓ Running" || echo "✗ Down"
	@echo ""

clean:
	@echo "Cleaning up containers and volumes..."
	@docker-compose -f deploy/docker-compose.yml down -v
	@echo "✓ Cleanup complete"

# ============================================================================
# Development
# ============================================================================

test:
	@echo "Running tests..."
	pytest tests/ -v --tb=short
	@echo "✓ Tests complete"

test-observability:
	@echo "Testing observability module..."
	python -c "from src.observability import create_langfuse_client; client = create_langfuse_client(); print('✓ Observability ready')"

test-eval:
	@echo "Testing evaluation module..."
	python -c "from src.eval_utils import EvalPipeline; p = EvalPipeline(['hallucination']); print('✓ Evaluation ready')"

test-all: test-observability test-eval
	@echo "✓ All modules ready"

eval:
	@echo "Running evaluation example..."
	python -m pytest tests/test_evaluation.py -v

run-example1:
	@echo "Running FastAPI RAG example..."
	python examples/01_fastapi_rag.py

run-example2:
	@echo "Running LangChain agent example..."
	python examples/02_langchain_agent.py

run-example3:
	@echo "Running LlamaIndex Phoenix example..."
	python examples/03_llamaindex_phoenix.py

run-example4:
	@echo "Running cost monitoring example..."
	python examples/04_cost_monitoring.py

# ============================================================================
# Database
# ============================================================================

db-shell:
	@echo "Opening PostgreSQL shell..."
	docker-compose -f deploy/docker-compose.yml exec postgres psql -U langfuse -d langfuse

db-migrate:
	@echo "Running database migrations..."
	docker-compose -f deploy/docker-compose.yml exec langfuse npm run migrate
	@echo "✓ Migrations complete"

db-reset:
	@echo "Resetting database..."
	docker-compose -f deploy/docker-compose.yml down -v postgres
	docker-compose -f deploy/docker-compose.yml up -d postgres
	@echo "✓ Database reset"

# ============================================================================
# Monitoring & Metrics
# ============================================================================

metrics:
	@echo "Fetching Prometheus metrics..."
	curl -s "http://localhost:9090/api/query?query=llm_requests_total" | jq .

dashboards:
	@echo "Available Grafana dashboards:"
	@echo "  - LLM Observability: http://localhost:3001/d/llm-observability"
	@echo ""
	@echo "Create custom dashboards at:"
	@echo "  http://localhost:3001/dashboard/new"

prometheus-shell:
	@echo "Opening Prometheus expression browser..."
	@echo "Visit: http://localhost:9090"
	@echo ""
	@echo "Try these queries:"
	@echo "  - rate(llm_requests_total[5m])"
	@echo "  - histogram_quantile(0.95, rate(llm_latency_seconds_bucket[5m]))"
	@echo "  - rate(llm_cost_total[1h])"

# ============================================================================
# Utility
# ============================================================================

install-hooks:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "✓ Hooks installed"

format:
	@echo "Formatting code..."
	black *.py examples/ tests/
	isort *.py examples/ tests/
	@echo "✓ Code formatted"

lint:
	@echo "Linting code..."
	pylint *.py examples/ tests/
	@echo "✓ Linting complete"

type-check:
	@echo "Type checking..."
	mypy src/observability.py src/eval_utils.py
	@echo "✓ Type check complete"

quality: format lint type-check test-all
	@echo "✓ All quality checks passed"

# ============================================================================
# Documentation
# ============================================================================

docs:
	@echo "Opening documentation..."
	@echo ""
	@echo "Quick References:"
	@echo "  - Setup Guide: cat docs/SETUP.md"
	@echo "  - Quick Start: cat docs/QUICKSTART.md"
	@echo "  - Deployment: cat docs/DEPLOYMENT.md"
	@echo ""
	@echo "Resource Links:"
	@echo "  - Langfuse Docs: https://langfuse.com/docs"
	@echo "  - DeepEval Docs: https://docs.confident-ai.com"
	@echo "  - Ragas Docs: https://docs.ragas.io"
	@echo "  - Phoenix: https://github.com/Arize-ai/phoenix"

readme:
	@less README.md

# ============================================================================
# Deployment
# ============================================================================

docker-build:
	@echo "Building Docker image..."
	docker build -f deploy/Dockerfile -t llm-observability:latest .
	@echo "✓ Image built"

docker-push:
	@echo "⚠️  Configure REGISTRY variable first"
	@echo "Usage: make docker-push REGISTRY=myregistry"
	ifdef REGISTRY
		docker tag llm-observability:latest $(REGISTRY)/llm-observability:latest
		docker push $(REGISTRY)/llm-observability:latest
		@echo "✓ Image pushed to $(REGISTRY)"
	endif

k8s-deploy:
	@echo "Deploying to Kubernetes..."
	@echo "See DEPLOYMENT.md for full instructions"
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/postgres-statefulset.yaml
	kubectl apply -f k8s/langfuse-deployment.yaml
	@echo "✓ Deployment initiated"

# ============================================================================
# Development Server
# ============================================================================

serve:
	@echo "Starting development server..."
	uvicorn examples.01_fastapi_rag:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# Backup & Restore
# ============================================================================

backup:
	@echo "Backing up PostgreSQL..."
	docker-compose -f deploy/docker-compose.yml exec -T postgres pg_dump -U langfuse langfuse > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup created"

restore:
	@echo "Restoring PostgreSQL from backup..."
	@echo "Usage: make restore BACKUP=backup_20240101_000000.sql"
	ifdef BACKUP
		docker-compose -f deploy/docker-compose.yml exec -T postgres psql -U langfuse langfuse < $(BACKUP)
		@echo "✓ Restore complete"
	endif

# ============================================================================
# Troubleshooting
# ============================================================================

troubleshoot:
	@echo "Troubleshooting Information"
	@echo "============================"
	@echo ""
	@echo "System Info:"
	@uname -a
	@echo ""
	@echo "Docker:"
	@docker --version
	@echo ""
	@echo "Docker Compose:"
	@docker-compose --version
	@echo ""
	@echo "Python:"
	@python --version
	@echo ""
	@echo "Running Services:"
	@docker-compose -f deploy/docker-compose.yml ps
	@echo ""
	@echo "Service Logs:"
	@echo "  make logs              # All services"
	@echo "  make logs-langfuse     # Langfuse only"
	@echo ""
	@echo "For more help, see:"
	@echo "  - QUICKSTART.md"
	@echo "  - SETUP.md"
	@echo "  - DEPLOYMENT.md"

# ============================================================================
# Default Target
# ============================================================================

.DEFAULT_GOAL := help

# Print help on `make` without arguments
ifeq ($(MAKECMDGOALS),)
    MAKECMDGOALS := help
endif
