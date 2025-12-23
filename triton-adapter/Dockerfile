# Triton Adapter - Lightweight Python service
# Translates OpenVINO API to Triton Inference Server

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for tritonclient and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .

# Environment defaults
ENV PORT=8001
ENV TRITON_URL=triton:8001
ENV TRITON_GRPC_URL=triton:8002
ENV USE_GRPC=true
ENV MODEL_NAME=tinyllama

EXPOSE 8001

CMD ["python", "server.py"]
