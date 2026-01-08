"""
Triton Adapter Service

Provides an OpenVINO-compatible API that translates requests to Triton Inference Server.
This allows the shared-ai-gateway to use either OpenVINO (CPU/NAS) or Triton (GPU)
without any code changes - just swap the INFERENCE_URL environment variable.

API Endpoints:
  POST /generate              - Text generation (OpenVINO-compatible)
  POST /v1/chat/completions   - OpenAI-compatible chat completions
  GET  /health                - Health check with model status
"""

import os
import json
import logging
import time
from typing import Optional, List
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
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3_2_3b")
PORT = int(os.environ.get("PORT", "8001"))

app = FastAPI(
    title="Triton Adapter",
    description="OpenVINO and OpenAI-compatible API for Triton Inference Server",
    version="1.1.0"
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

# OpenAI-compatible models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage


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
    """Convert string to bytes array for Triton"""
    text_bytes = prompt.encode('utf-8')
    return np.array([[text_bytes]], dtype=object)


def detokenize_output(output: np.ndarray) -> str:
    """Convert model output back to text"""
    try:
        if output.dtype == object:
            return output[0][0].decode('utf-8') if isinstance(output[0][0], bytes) else str(output[0][0])
        else:
            return str(output.tolist())
    except Exception as e:
        logger.error(f"Detokenization error: {e}")
        return str(output)


def call_triton(prompt: str, max_tokens: int = 512) -> str:
    """Call Triton for inference"""
    client = get_triton_client()

    if client is None:
        raise HTTPException(status_code=503, detail="Triton server unavailable")

    if not check_model_ready(client):
        raise HTTPException(status_code=503, detail=f"Model '{MODEL_NAME}' not ready")

    prompt_data = tokenize_prompt(prompt)

    if USE_GRPC:
        inputs = [grpcclient.InferInput("text_input", prompt_data.shape, "BYTES")]
        inputs[0].set_data_from_numpy(prompt_data)

        max_tokens_arr = np.array([[max_tokens]], dtype=np.int32)
        inputs.append(grpcclient.InferInput("max_tokens", max_tokens_arr.shape, "INT32"))
        inputs[1].set_data_from_numpy(max_tokens_arr)

        outputs = [grpcclient.InferRequestedOutput("text_output")]

        response = client.infer(model_name=MODEL_NAME, inputs=inputs, outputs=outputs)
        output_data = response.as_numpy("text_output")
    else:
        inputs = [httpclient.InferInput("text_input", list(prompt_data.shape), "BYTES")]
        inputs[0].set_data_from_numpy(prompt_data)

        max_tokens_arr = np.array([[max_tokens]], dtype=np.int32)
        inputs.append(httpclient.InferInput("max_tokens", list(max_tokens_arr.shape), "INT32"))
        inputs[1].set_data_from_numpy(max_tokens_arr)

        outputs = [httpclient.InferRequestedOutput("text_output")]

        response = client.infer(model_name=MODEL_NAME, inputs=inputs, outputs=outputs)
        output_data = response.as_numpy("text_output")

    return detokenize_output(output_data)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint matching OpenVINO API."""
    client = get_triton_client()

    if client is None:
        return HealthResponse(
            status="error",
            model_loaded=False,
            triton_url=TRITON_GRPC_URL if USE_GRPC else TRITON_URL,
            model_name=MODEL_NAME
        )

    try:
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
    """Text generation endpoint matching OpenVINO API."""
    try:
        logger.info(f"Generating for prompt: {request.prompt[:50]}...")
        generated_text = call_triton(request.prompt, request.max_new_tokens)
        logger.info(f"Generated {len(generated_text)} chars")

        return GenerateResponse(
            response=generated_text,
            tokens_generated=len(generated_text.split()),
            model=MODEL_NAME
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    try:
        # Format messages into a single prompt
        # For chat models, combine messages with role prefixes
        prompt_parts = []
        for msg in request.messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
            else:
                prompt_parts.append(msg.content)

        prompt = "\n".join(prompt_parts)
        if not prompt.endswith("Assistant:"):
            prompt += "\nAssistant:"

        logger.info(f"Chat completion for {len(request.messages)} messages")

        generated_text = call_triton(prompt, request.max_tokens)

        # Approximate token counts
        prompt_tokens = len(prompt.split())
        completion_tokens = len(generated_text.split())

        return ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model or MODEL_NAME,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=generated_text),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "name": "Triton Adapter",
        "version": "1.2.0",
        "description": "Multi-API adapter for Triton Inference Server",
        "triton_url": TRITON_GRPC_URL if USE_GRPC else TRITON_URL,
        "model": MODEL_NAME,
        "endpoints": {
            "POST /generate": "Text generation (OpenVINO-compatible)",
            "POST /v1/chat/completions": "Chat completions (OpenAI-compatible)",
            "POST /api/chat": "Chat completions (Ollama-compatible)",
            "GET /api/tags": "List models (Ollama-compatible)",
            "GET /health": "Health check with model status",
        }
    }


# ============================================================
# Ollama-compatible API endpoints (for gateway Tier 1)
# ============================================================

class OllamaChatMessage(BaseModel):
    role: str
    content: str

class OllamaChatRequest(BaseModel):
    model: str
    messages: List[OllamaChatMessage]
    stream: bool = False
    options: Optional[dict] = None

class OllamaChatResponse(BaseModel):
    model: str
    created_at: str
    message: OllamaChatMessage
    done: bool = True
    total_duration: int = 0
    eval_count: int = 0

@app.get("/api/tags")
async def ollama_tags():
    """Ollama-compatible model list endpoint (used for health check)"""
    client = get_triton_client()
    model_ready = client and check_model_ready(client)

    return {
        "models": [
            {
                "name": MODEL_NAME,
                "model": MODEL_NAME,
                "modified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "size": 0,
                "digest": "triton-adapter",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "llama",
                    "parameter_size": "3B",
                    "quantization_level": "Q4_K_M"
                }
            }
        ] if model_ready else []
    }

@app.post("/api/chat")
async def ollama_chat(request: OllamaChatRequest):
    """Ollama-compatible chat endpoint"""
    try:
        # Format messages into prompt
        prompt_parts = []
        for msg in request.messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
            else:
                prompt_parts.append(msg.content)

        prompt = "\n".join(prompt_parts)
        if not prompt.endswith("Assistant:"):
            prompt += "\nAssistant:"

        # Get options
        options = request.options or {}
        max_tokens = options.get("num_predict", 512)

        logger.info(f"Ollama chat for {len(request.messages)} messages")

        start_time = time.time()
        generated_text = call_triton(prompt, max_tokens)
        duration_ns = int((time.time() - start_time) * 1e9)

        return OllamaChatResponse(
            model=request.model or MODEL_NAME,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            message=OllamaChatMessage(role="assistant", content=generated_text),
            done=True,
            total_duration=duration_ns,
            eval_count=len(generated_text.split())
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ollama chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
