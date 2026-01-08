# CPU-only Triton Server for K8s fallback (AMD/Intel CPUs)
# Uses ONNX Runtime CPU execution provider - no GPU dependencies

FROM nvcr.io/nvidia/tritonserver:23.10-py3

# Install Python dependencies for the embedding model
# Using CPU-only onnxruntime (lighter, no CUDA dependencies)
RUN pip3 install --no-cache-dir \
    transformers==4.35.2 \
    onnxruntime==1.17.1 \
    sentencepiece==0.1.99 \
    numpy

# Models are mounted via hostPath volume - NOT baked into image
# Mount point: /models (from /home/maxjeffwell/ai-models on VPS)

# Expose Triton ports
EXPOSE 8000 8001 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/v2/health/ready || exit 1

# Run Triton with CPU-optimized settings
CMD ["tritonserver", "--model-repository=/models", "--log-verbose=1"]
