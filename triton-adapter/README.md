# Triton Adapter

OpenVINO-compatible API wrapper for NVIDIA Triton Inference Server.

## Purpose

This adapter allows the `shared-ai-gateway` to use either:
- **OpenVINO** (CPU) - for NAS deployments without GPU
- **Triton** (GPU) - for GPU-accelerated inference

No code changes required - just swap the `INFERENCE_URL` environment variable.

## Architecture

```
shared-ai-gateway (port 8002)
        │
        ▼
   INFERENCE_URL
        │
   ┌────┴────┐
   │         │
   ▼         ▼
OpenVINO   Triton Adapter (this service)
 (CPU)           │
                 ▼
           Triton Server
             (GPU)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Text generation (OpenVINO-compatible) |
| `/health` | GET | Health check with model status |
| `/v2/health/ready` | GET | Triton-native ready check |
| `/v2/health/live` | GET | Triton-native liveness check |

## Setup

### 1. Fix model directory permissions

```bash
sudo chown -R $USER:$USER ~/GitHub_Projects/code-talk/models/
```

### 2. Set up model repository

```bash
mkdir -p models/tinyllama/1
cp triton-adapter/model-config.pbtxt models/tinyllama/config.pbtxt
cp triton-adapter/model.py models/tinyllama/1/model.py
```

### 3. Start GPU deployment

```bash
cp .env.gpu .env
docker compose -f docker-compose.yml -f docker-compose.triton.yml up --build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8001 | Adapter listen port |
| `TRITON_URL` | triton:8001 | Triton HTTP endpoint |
| `TRITON_GRPC_URL` | triton:8002 | Triton gRPC endpoint |
| `USE_GRPC` | true | Use gRPC (faster) or HTTP |
| `MODEL_NAME` | tinyllama | Model name in Triton |

## Switching Between Backends

### NAS (OpenVINO/CPU)
```bash
cp .env.nas .env
docker compose up
```

### GPU (Triton)
```bash
cp .env.gpu .env
docker compose -f docker-compose.yml -f docker-compose.triton.yml up
```
