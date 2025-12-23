"""
Triton Adapter Service

Provides an OpenVINO-compatible API that translates requests to Triton Inference Server.
This allows the shared-ai-gateway to use either OpenVINO (CPU/NAS) or Triton (GPU)
without any code changes - just swap the INFERENCE_URL environment variable.

API Endpoints (matching OpenVINO backend):
  POST /generate  - Text generation
  GET  /health    - Health check with model status
"""

import os
import json
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TRITON_URL = os.environ.get("TRITON_URL", "triton:8001")
TRITON_GRPC_URL = os.environ.get("TRITON_GRPC_URL", "triton:8002")
USE_GRPC = os.environ.get("USE_GRPC", "true").lower() == "true"
MODEL_NAME = os.environ.get("MODEL_NAME", "tinyllama")
PORT = int(os.environ.get("PORT", "8001"))

app = FastAPI(
    title="Triton Adapter",
    description="OpenVINO-compatible API for Triton Inference Server",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models matching OpenVINO API
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 200
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50

class GenerateResponse(BaseModel):
    response: str
    tokens_generated: int = 0
    model: str = MODEL_NAME

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    triton_url: str
    model_name: str


def get_triton_client():
    """Create Triton client (gRPC preferred for performance)"""
    try:
        if USE_GRPC:
            client = grpcclient.InferenceServerClient(url=TRITON_GRPC_URL)
        else:
            client = httpclient.InferenceServerClient(url=TRITON_URL)
        return client
    except Exception as e:
        logger.error(f"Failed to create Triton client: {e}")
        return None


def check_model_ready(client) -> bool:
    """Check if the model is loaded and ready"""
    try:
        if USE_GRPC:
            return client.is_model_ready(MODEL_NAME)
        else:
            return client.is_model_ready(MODEL_NAME)
    except Exception as e:
        logger.error(f"Model ready check failed: {e}")
        return False


def tokenize_prompt(prompt: str) -> np.ndarray:
    """
    Simple tokenization for TinyLlama.

    For production, you'd use the actual tokenizer:
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

    This is a placeholder that works with pre-tokenized models.
    """
    # For models that accept raw text input
    # Convert string to bytes array
    text_bytes = prompt.encode('utf-8')
    return np.array([[text_bytes]], dtype=object)


def detokenize_output(output: np.ndarray) -> str:
    """Convert model output back to text"""
    try:
        if output.dtype == object:
            # Text output
            return output[0][0].decode('utf-8') if isinstance(output[0][0], bytes) else str(output[0][0])
        else:
            # Token IDs - would need tokenizer to decode
            return str(output.tolist())
    except Exception as e:
        logger.error(f"Detokenization error: {e}")
        return str(output)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint matching OpenVINO API.
    Returns model loading status for the gateway to verify.
    """
    client = get_triton_client()

    if client is None:
        return HealthResponse(
            status="error",
            model_loaded=False,
            triton_url=TRITON_GRPC_URL if USE_GRPC else TRITON_URL,
            model_name=MODEL_NAME
        )

    try:
        # Check server is live
        if USE_GRPC:
            is_live = client.is_server_live()
            is_ready = client.is_server_ready()
        else:
            is_live = client.is_server_live()
            is_ready = client.is_server_ready()

        model_ready = check_model_ready(client) if is_ready else False

        return HealthResponse(
            status="ok" if is_live and is_ready else "degraded",
            model_loaded=model_ready,
            triton_url=TRITON_GRPC_URL if USE_GRPC else TRITON_URL,
            model_name=MODEL_NAME
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            model_loaded=False,
            triton_url=TRITON_GRPC_URL if USE_GRPC else TRITON_URL,
            model_name=MODEL_NAME
        )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Text generation endpoint matching OpenVINO API.

    Translates the simple { prompt, max_new_tokens } format
    to Triton's inference request format.
    """
    client = get_triton_client()

    if client is None:
        raise HTTPException(status_code=503, detail="Triton server unavailable")

    if not check_model_ready(client):
        raise HTTPException(status_code=503, detail=f"Model '{MODEL_NAME}' not ready")

    try:
        logger.info(f"Generating for prompt: {request.prompt[:50]}...")

        # Prepare input tensor
        prompt_data = tokenize_prompt(request.prompt)

        if USE_GRPC:
            # gRPC inference
            inputs = [
                grpcclient.InferInput("text_input", prompt_data.shape, "BYTES")
            ]
            inputs[0].set_data_from_numpy(prompt_data)

            # Add generation parameters as inputs if model supports them
            max_tokens = np.array([[request.max_new_tokens]], dtype=np.int32)
            inputs.append(grpcclient.InferInput("max_tokens", max_tokens.shape, "INT32"))
            inputs[1].set_data_from_numpy(max_tokens)

            outputs = [grpcclient.InferRequestedOutput("text_output")]

            response = client.infer(
                model_name=MODEL_NAME,
                inputs=inputs,
                outputs=outputs
            )

            output_data = response.as_numpy("text_output")
        else:
            # HTTP inference
            inputs = [
                httpclient.InferInput("text_input", list(prompt_data.shape), "BYTES")
            ]
            inputs[0].set_data_from_numpy(prompt_data)

            max_tokens = np.array([[request.max_new_tokens]], dtype=np.int32)
            inputs.append(httpclient.InferInput("max_tokens", list(max_tokens.shape), "INT32"))
            inputs[1].set_data_from_numpy(max_tokens)

            outputs = [httpclient.InferRequestedOutput("text_output")]

            response = client.infer(
                model_name=MODEL_NAME,
                inputs=inputs,
                outputs=outputs
            )

            output_data = response.as_numpy("text_output")

        # Convert output to text
        generated_text = detokenize_output(output_data)

        logger.info(f"Generated {len(generated_text)} chars")

        return GenerateResponse(
            response=generated_text,
            tokens_generated=len(generated_text.split()),  # Approximate
            model=MODEL_NAME
        )

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "name": "Triton Adapter",
        "version": "1.0.0",
        "description": "OpenVINO-compatible API for Triton Inference Server",
        "triton_url": TRITON_GRPC_URL if USE_GRPC else TRITON_URL,
        "model": MODEL_NAME,
        "endpoints": {
            "POST /generate": "Text generation (OpenVINO-compatible)",
            "GET /health": "Health check with model status",
        }
    }


@app.get("/v2/health/ready")
async def triton_health_ready():
    """Triton-native health endpoint for compatibility"""
    client = get_triton_client()
    if client and check_model_ready(client):
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Not ready")


@app.get("/v2/health/live")
async def triton_health_live():
    """Triton-native liveness endpoint"""
    client = get_triton_client()
    if client:
        try:
            if client.is_server_live():
                return {"status": "live"}
        except:
            pass
    raise HTTPException(status_code=503, detail="Not live")


if __name__ == "__main__":
    import uvicorn
    logger.info(f"""
    ========================================
    Triton Adapter Starting
    ----------------------------------------
    Port: {PORT}
    Triton URL: {TRITON_GRPC_URL if USE_GRPC else TRITON_URL}
    Protocol: {"gRPC" if USE_GRPC else "HTTP"}
    Model: {MODEL_NAME}
    ========================================
    """)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
