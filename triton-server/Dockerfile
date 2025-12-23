# Custom Triton Server with PyTorch + Transformers
# For running HuggingFace models like TinyLlama

FROM nvcr.io/nvidia/tritonserver:23.10-pyt-python-py3

# Install PyTorch with CUDA 12.1 (matches Triton 23.10)
RUN pip install --no-cache-dir \
    torch==2.1.1+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# Install HuggingFace ecosystem
RUN pip install --no-cache-dir \
    transformers==4.35.2 \
    accelerate==0.24.1 \
    sentencepiece==0.1.99 \
    safetensors==0.4.1
