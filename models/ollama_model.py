import requests
import time
from typing import Dict, Any, Optional
from .unified_interface import UnifiedLLMInterface, LLMResponse

class OllamaModel(UnifiedLLMInterface):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        super().__init__(model_name)
        self.base_url = base_url
        self.api_url = f"{base_url}/api/chat"
        
    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        start_time = time.perf_counter()
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_new_tokens", 512),
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            content = data.get("message", {}).get("content", "")
            # Ollama returns token counts in response statistics
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                input_tokens=prompt_eval_count,
                output_tokens=eval_count,
                latency_ms=latency_ms,
                cost_usd=0.0, # Local execution is free
                gpu_memory_mb=0.0 # Hard to get from API, leaving as 0
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                model_name=self.model_name,
                input_tokens=0,
                output_tokens=0,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"Ollama Error: {str(e)}"
            )
