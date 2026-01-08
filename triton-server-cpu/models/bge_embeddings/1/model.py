"""
BGE Embeddings Model for Triton Python Backend (CPU-only)

Loads the ONNX-exported bge-base-en-v1.5 model and provides
sentence embeddings via Triton's Python backend.

Optimized for CPU inference on AMD/Intel processors.

Input: text strings
Output: 768-dim normalized embeddings
"""

import os
import json
import numpy as np
from pathlib import Path

import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    """Triton Python backend for BGE embeddings (CPU-only)"""

    def initialize(self, args):
        """Load ONNX model and tokenizer"""
        self.logger = pb_utils.Logger

        # Get model directory
        model_config = json.loads(args['model_config'])
        model_dir = Path(args['model_repository'])
        version = args['model_version']
        model_path = model_dir / version

        self.logger.log_info(f"Loading BGE embeddings (CPU) from {model_path}")

        # Import dependencies
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
        except ImportError as e:
            self.logger.log_error(f"Missing dependency: {e}")
            raise

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.logger.log_info("Tokenizer loaded")

        # CPU-only session options for optimal performance
        sess_options = ort.SessionOptions()

        # Use all available CPU cores for parallelism
        sess_options.intra_op_num_threads = 0  # 0 = use all cores
        sess_options.inter_op_num_threads = 0  # 0 = use all cores

        # Enable graph optimizations
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Memory optimization
        sess_options.enable_mem_pattern = True
        sess_options.enable_cpu_mem_arena = True

        self.logger.log_info("ONNX session options configured for CPU")

        # Load ONNX model with CPU execution provider only
        onnx_path = model_path / "model.onnx"
        self.session = ort.InferenceSession(
            str(onnx_path),
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        self.logger.log_info(f"ONNX model loaded (CPU): {onnx_path}")

        # Get model info
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]
        self.logger.log_info(f"Model inputs: {self.input_names}")
        self.logger.log_info(f"Model outputs: {self.output_names}")

    def execute(self, requests):
        """Process embedding requests"""
        responses = []

        for request in requests:
            try:
                # Get input text
                text_tensor = pb_utils.get_input_tensor_by_name(request, "text")
                texts = text_tensor.as_numpy()

                # Decode byte strings to text
                decoded_texts = []
                for text in texts.flatten():
                    if isinstance(text, bytes):
                        decoded_texts.append(text.decode('utf-8'))
                    else:
                        decoded_texts.append(str(text))

                # Tokenize
                inputs = self.tokenizer(
                    decoded_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="np"
                )

                # Prepare ONNX inputs
                onnx_inputs = {
                    "input_ids": inputs["input_ids"].astype(np.int64),
                    "attention_mask": inputs["attention_mask"].astype(np.int64)
                }

                # Run inference
                outputs = self.session.run(None, onnx_inputs)

                # Get sentence embeddings (already pooled by the model)
                if 'sentence_embedding' in self.output_names:
                    idx = self.output_names.index('sentence_embedding')
                    embeddings = outputs[idx]
                else:
                    # Fallback: use token embeddings with mean pooling
                    token_embeddings = outputs[0]
                    attention_mask = inputs["attention_mask"]
                    mask_expanded = np.expand_dims(attention_mask, -1)
                    sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
                    sum_mask = np.clip(mask_expanded.sum(axis=1), 1e-9, None)
                    embeddings = sum_embeddings / sum_mask

                # Normalize embeddings (BGE uses L2 normalization)
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                embeddings = embeddings / np.clip(norms, 1e-9, None)

                # Create output tensor
                output_tensor = pb_utils.Tensor(
                    "embeddings",
                    embeddings.astype(np.float32)
                )

                response = pb_utils.InferenceResponse(output_tensors=[output_tensor])
                responses.append(response)

            except Exception as e:
                self.logger.log_error(f"Error processing request: {str(e)}")
                error = pb_utils.TritonError(f"Embedding failed: {str(e)}")
                responses.append(pb_utils.InferenceResponse(error=error))

        return responses

    def finalize(self):
        """Cleanup"""
        self.logger.log_info("BGE embeddings model (CPU) finalized")
        del self.session
        del self.tokenizer
