"""
Llama 3.2 3B Instruct Model for Triton Python Backend

Uses llama-cpp-python for efficient GGUF model inference on GPU.
Supports conversational/chat completion with configurable parameters.

Input: prompt (string), optional: max_tokens, temperature, top_p
Output: response (string)
"""

import os
import json
import numpy as np
from pathlib import Path

import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    """Triton Python backend for Llama 3.2 3B inference"""

    def initialize(self, args):
        """Load the GGUF model with llama-cpp-python"""
        self.logger = pb_utils.Logger

        # Parse model config
        model_config = json.loads(args['model_config'])
        model_dir = Path(args['model_repository'])
        version = args['model_version']
        model_path = model_dir / version

        # Get parameters from config (parameters is a dict in Triton)
        params = model_config.get('parameters', {})

        # Extract string values from parameter dict structure
        def get_param(key, default):
            if key in params and 'string_value' in params[key]:
                return params[key]['string_value']
            return default

        model_file = get_param('model_path', 'Llama-3.2-3B-Instruct-Q4_K_M.gguf')
        n_gpu_layers = int(get_param('n_gpu_layers', '-1'))
        n_ctx = int(get_param('n_ctx', '4096'))

        full_model_path = model_path / model_file
        self.logger.log_info(f"Loading Llama model from {full_model_path}")

        # Import llama-cpp-python
        try:
            from llama_cpp import Llama
        except ImportError as e:
            self.logger.log_error(f"llama-cpp-python not installed: {e}")
            raise

        # Load model with GPU acceleration
        self.model = Llama(
            model_path=str(full_model_path),
            n_gpu_layers=n_gpu_layers,  # -1 = all layers on GPU
            n_ctx=n_ctx,
            n_batch=512,
            verbose=True,
        )

        self.logger.log_info(f"Llama model loaded successfully with {n_gpu_layers} GPU layers")

        # Default generation parameters
        self.default_max_tokens = 512
        self.default_temperature = 0.7
        self.default_top_p = 0.9

    def execute(self, requests):
        """Process inference requests"""
        responses = []

        for request in requests:
            try:
                # Get prompt (required)
                prompt_tensor = pb_utils.get_input_tensor_by_name(request, "text_input")
                prompt = prompt_tensor.as_numpy()[0][0]
                if isinstance(prompt, bytes):
                    prompt = prompt.decode('utf-8')

                # Get optional parameters
                max_tokens = self._get_optional_param(request, "max_tokens", self.default_max_tokens)
                temperature = self._get_optional_param(request, "temperature", self.default_temperature)
                top_p = self._get_optional_param(request, "top_p", self.default_top_p)

                self.logger.log_info(f"Generating response for prompt ({len(prompt)} chars)")

                # Format as chat message for instruct model
                messages = [
                    {"role": "user", "content": prompt}
                ]

                # Generate response using chat completion
                response = self.model.create_chat_completion(
                    messages=messages,
                    max_tokens=int(max_tokens),
                    temperature=float(temperature),
                    top_p=float(top_p),
                    stop=["<|eot_id|>", "<|end_of_text|>"],
                )

                # Extract generated text
                generated_text = response['choices'][0]['message']['content']

                self.logger.log_info(f"Generated {len(generated_text)} chars")

                # Create output tensor
                output_tensor = pb_utils.Tensor(
                    "text_output",
                    np.array([[generated_text]], dtype=object)
                )

                inference_response = pb_utils.InferenceResponse(
                    output_tensors=[output_tensor]
                )
                responses.append(inference_response)

            except Exception as e:
                self.logger.log_error(f"Error during inference: {str(e)}")
                error_response = pb_utils.InferenceResponse(
                    output_tensors=[],
                    error=pb_utils.TritonError(str(e))
                )
                responses.append(error_response)

        return responses

    def _get_optional_param(self, request, name, default):
        """Get optional parameter from request or use default"""
        tensor = pb_utils.get_input_tensor_by_name(request, name)
        if tensor is not None:
            value = tensor.as_numpy()[0][0]
            return value
        return default

    def finalize(self):
        """Clean up resources"""
        self.logger.log_info("Finalizing Llama model")
        if hasattr(self, 'model'):
            del self.model
