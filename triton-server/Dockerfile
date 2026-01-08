# GPU Triton Server with Python backend for embeddings and LLM inference
# Supports: BGE embeddings (ONNX), Llama 3.2 3B (llama-cpp-python)

FROM nvcr.io/nvidia/tritonserver:23.10-py3

# Install PyTorch with CUDA 12.1 support
RUN pip install --no-cache-dir \
    torch==2.1.1+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# Install transformers and related packages
RUN pip install --no-cache-dir \
    transformers==4.35.2 \
    accelerate==0.24.1 \
    sentencepiece==0.1.99 \
    safetensors==0.4.1

# Install ONNX Runtime GPU
RUN pip install --no-cache-dir \
    onnxruntime-gpu==1.17.1 \
    --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/

# Install llama-cpp-python with CUDA support for LLM inference
# CMAKE_ARGS enables CUDA acceleration
ENV CMAKE_ARGS="-DGGML_CUDA=on"
ENV FORCE_CMAKE=1
RUN pip install --no-cache-dir llama-cpp-python==0.2.90

# Install additional utilities
RUN pip install --no-cache-dir \
    numpy \
    huggingface_hub

# Models are mounted via volume - NOT baked into image
# Mount point: /models

# Expose Triton ports (configurable via command)
EXPOSE 8000 8001 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/v2/health/ready || exit 1

# Default command (can be overridden in docker-compose)
CMD ["tritonserver", "--model-repository=/models", "--log-verbose=1"]
