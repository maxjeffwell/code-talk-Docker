#!/usr/bin/env python3
"""
Export BGE embedding model to ONNX format for Triton Inference Server.

This script exports BAAI/bge-base-en-v1.5 to ONNX with optimizations
for both GPU and CPU inference.
"""

import os
import sys
import torch
import numpy as np
from pathlib import Path

# Check for required packages
try:
    from transformers import AutoTokenizer, AutoModel
    from optimum.onnxruntime import ORTModelForFeatureExtraction
    from optimum.exporters.onnx import main_export
except ImportError as e:
    print(f"Missing package: {e}")
    print("\nInstall required packages:")
    print("pip install transformers optimum[onnxruntime-gpu] onnx onnxruntime-gpu sentence-transformers")
    sys.exit(1)

MODEL_NAME = "BAAI/bge-base-en-v1.5"
OUTPUT_DIR = Path(__file__).parent / "bge_embeddings" / "1"

def export_model():
    """Export BGE model to ONNX format"""
    print(f"Exporting {MODEL_NAME} to ONNX...")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Export using optimum (handles all the complexity)
    # Force CPU export - ONNX model works on any device after export
    main_export(
        model_name_or_path=MODEL_NAME,
        output=OUTPUT_DIR,
        task="feature-extraction",
        opset=14,  # Lower opset for broader compatibility
        device="cpu",  # Export on CPU (result works on GPU)
        fp16=False,  # Keep FP32 for compatibility
    )

    print(f"\nModel exported to: {OUTPUT_DIR}")

    # Rename model.onnx to follow Triton convention
    model_file = OUTPUT_DIR / "model.onnx"
    if model_file.exists():
        print(f"Model file: {model_file}")
        print(f"Model size: {model_file.stat().st_size / 1024 / 1024:.1f} MB")


def test_exported_model():
    """Test the exported ONNX model"""
    import onnxruntime as ort

    print("\nTesting exported model...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Create ONNX session (use CPU for testing to avoid CUDA issues)
    model_path = OUTPUT_DIR / "model.onnx"
    providers = ['CPUExecutionProvider']  # Test on CPU, Triton will use GPU
    session = ort.InferenceSession(str(model_path), providers=providers)

    # Test input
    test_texts = [
        "What is machine learning?",
        "How to cook pasta",
        "The weather is nice today"
    ]

    # Tokenize
    inputs = tokenizer(
        test_texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="np"
    )

    # Run inference
    outputs = session.run(
        None,
        {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
            "token_type_ids": inputs.get("token_type_ids", np.zeros_like(inputs["input_ids"]))
        }
    )

    # Get embeddings (mean pooling over token embeddings)
    token_embeddings = outputs[0]  # [batch, seq_len, hidden_size]
    attention_mask = inputs["attention_mask"]

    # Mean pooling
    input_mask_expanded = np.expand_dims(attention_mask, -1)
    sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    embeddings = sum_embeddings / sum_mask

    # Normalize (BGE uses normalized embeddings)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    print(f"Output shape: {embeddings.shape}")
    print(f"Embedding dim: {embeddings.shape[1]}")

    # Test similarity
    print("\nSimilarity test:")
    for i, text in enumerate(test_texts):
        print(f"  [{i}] {text[:50]}...")

    # Compute cosine similarities
    sims = np.dot(embeddings, embeddings.T)
    print(f"\nCosine similarity matrix:")
    print(sims.round(3))

    print("\n✓ Export successful!")
    return True


if __name__ == "__main__":
    export_model()
    test_exported_model()
