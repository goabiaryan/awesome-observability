FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "examples.01_fastapi_rag:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Build:
#   docker build -t llm-observability:latest .
#
# Run:
#   docker run \
#     -e OPENAI_API_KEY=$OPENAI_API_KEY \
#     -e LANGFUSE_PUBLIC_KEY=$LANGFUSE_PUBLIC_KEY \
#     -e LANGFUSE_SECRET_KEY=$LANGFUSE_SECRET_KEY \
#     -p 8000:8000 \
#     llm-observability:latest
#
# With compose (see docker-compose.yml):
#   docker-compose up
# ============================================================================
