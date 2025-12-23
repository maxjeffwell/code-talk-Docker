"""
TinyLlama Model for Triton Python Backend
Copy this file to: models/tinyllama/1/model.py

This Python backend handles text generation using the TinyLlama model
with HuggingFace Transformers.
"""

import json
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    """Triton Python backend for TinyLlama text generation"""

    def initialize(self, args):
        """Load the model and tokenizer"""
        self.logger = pb_utils.Logger

        # Get model parameters from config
        model_config = json.loads(args['model_config'])
        params = model_config.get('parameters', {})
        model_name = params.get('model_name', {}).get('string_value', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0')

        self.logger.log_info(f"Loading model: {model_name}")

        # Detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.log_info(f"Using device: {self.device}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model with appropriate dtype
        if self.device == "cuda":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32
            )
            self.model.to(self.device)

        # Set to inference mode (disable dropout, etc.)
        self.model.train(False)
        self.logger.log_info(f"Model loaded successfully on {self.device}")

    def execute(self, requests):
        """Process inference requests"""
        responses = []

        for request in requests:
            try:
                # Get input tensors
                text_input = pb_utils.get_input_tensor_by_name(request, "text_input")
                max_tokens_tensor = pb_utils.get_input_tensor_by_name(request, "max_tokens")

                # Decode input text
                prompt = text_input.as_numpy()[0][0]
                if isinstance(prompt, bytes):
                    prompt = prompt.decode('utf-8')

                # Get max tokens (default 200)
                max_new_tokens = 200
                if max_tokens_tensor is not None:
                    max_new_tokens = int(max_tokens_tensor.as_numpy()[0][0])

                # Tokenize
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=2048
                ).to(self.device)

                # Generate
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9,
                        top_k=50,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )

                # Decode output
                generated_text = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=True
                )

                # Remove the input prompt from output if echoed
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()

                # Create output tensor
                output_tensor = pb_utils.Tensor(
                    "text_output",
                    np.array([[generated_text]], dtype=object)
                )

                response = pb_utils.InferenceResponse(output_tensors=[output_tensor])
                responses.append(response)

            except Exception as e:
                self.logger.log_error(f"Error processing request: {str(e)}")
                error = pb_utils.TritonError(f"Generation failed: {str(e)}")
                responses.append(pb_utils.InferenceResponse(error=error))

        return responses

    def finalize(self):
        """Cleanup when model is unloaded"""
        self.logger.log_info("Model finalized")
        del self.model
        del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
