import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from models import UnifiedLLMInterface, LLMResponse

class LocalHuggingFaceModel(UnifiedLLMInterface):
    def __init__(self, model_name_or_path: str, device: str = None):
        super().__init__(model_name_or_path)
        if device:
            self.device = device
        elif torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
            
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            print(f"Loading local model {self.model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Use float16 for CUDA and MPS to save memory/speed
            if self.device == "cuda" or self.device == "mps":
                dtype = torch.float16
            else:
                dtype = torch.float32
                
            # device_map="auto" works best with CUDA. For MPS/CPU we manually move.
            # Using low_cpu_mem_usage=True if available helps
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, 
                torch_dtype=dtype,
                low_cpu_mem_usage=True if self.device != "cpu" else False
            )
            self.model.to(self.device)
                
            print(f"Model {self.model_name} loaded.")
        except Exception as e:
            print(f"Failed to load model {self.model_name}: {e}")
            self.model = None

    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        if not self.model or not self.tokenizer:
            return LLMResponse("", self.model_name, 0, 0, 0, error="Model not loaded")

        start_time = time.perf_counter()
        
        # Simple chat formatting - might need chat template application if model supports it
        # For base models, this might just be concatenation. Inspecting model type is hard dynamically.
        # We will assume instruct models that support apply_chat_template or similar.
        full_prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                # Some tokenizers don't support system roles, fallback to appending if error?
                # For simplicity in this unified interface, we try to use the chat template.
                full_prompt_ids = self.tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True)
            except Exception:
                # Fallback manual string
                full_prompt_ids = self.tokenizer(full_prompt, return_tensors="pt").input_ids
        else:
             full_prompt_ids = self.tokenizer(full_prompt, return_tensors="pt").input_ids
             
        full_prompt_ids = full_prompt_ids.to(self.model.device)
        input_tokens_count = full_prompt_ids.shape[1]

        try:
            temperature = kwargs.get("temperature", 0.7)
            do_sample = temperature > 0
            
            gen_kwargs = {
                "max_new_tokens": kwargs.get("max_new_tokens", 512),
                "do_sample": do_sample
            }
            if do_sample:
                gen_kwargs["temperature"] = temperature
                
            outputs = self.model.generate(
                full_prompt_ids,
                **gen_kwargs
            )
            output_ids = outputs[0][input_tokens_count:]
            output_tokens_count = len(output_ids)
            content = self.tokenizer.decode(output_ids, skip_special_tokens=True)
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Memory tracking
            gpu_mem = 0
            if self.device == "cuda":
                gpu_mem = torch.cuda.max_memory_allocated() / (1024 * 1024) # MB
            
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                input_tokens=input_tokens_count,
                output_tokens=output_tokens_count,
                latency_ms=latency_ms,
                cost_usd=0.0,
                gpu_memory_mb=gpu_mem
            )
        except Exception as e:
            return LLMResponse(
                content="", 
                model_name=self.model_name,
                input_tokens=input_tokens_count,
                output_tokens=0,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=str(e)
            )

