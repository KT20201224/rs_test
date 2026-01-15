import time
import os
from typing import Dict, Any
import openai


from .unified_interface import UnifiedLLMInterface, LLMResponse
from config import MODEL_PRICING

class APIModelBase(UnifiedLLMInterface):
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = MODEL_PRICING.get(self.model_name, {"input": 0, "output": 0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

class OpenAIModel(APIModelBase):
    def __init__(self, model_name: str, api_key: str = None):
        super().__init__(model_name)
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        start_time = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **kwargs
            )
            data = response
            content = data.choices[0].message.content
            # Usage may be None in some stream cases, but default is standard
            usage = data.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            cost = self.calculate_cost(input_tokens, output_tokens)
            
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model_name=self.model_name,
                input_tokens=0,
                output_tokens=0,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=str(e)
            )


class GeminiModel(APIModelBase):
    def __init__(self, model_name: str, api_key: str = None):
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        start_time = time.perf_counter()
        
        # Thinking Config (Gemini 3 feature)
        # Only add if model supports it (Gemini 3+)
        thinking_params = {}
        if "gemini-3" in self.model_name and "thinking_level" in kwargs:
             thinking_params = {
                 "thinking_config": {"include_thoughts": True} # Basic enablement
                 # Note: Detailed thinking_level param structure depends on exact API spec, 
                 # currently 'include_thoughts' is the standard flag for preview.
             }

        payload = {
            "contents": [{
                "parts": [{"text": user_prompt}]
            }],
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                **thinking_params
            }
        }
        
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                params=params, 
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract Text
            try:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                content = "" # blocked or empty
            
            # Extract Usage
            usage = data.get("usageMetadata", {})
            input_tokens = usage.get("promptTokenCount", 0)
            output_tokens = usage.get("candidatesTokenCount", 0)
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            cost = self.calculate_cost(input_tokens, output_tokens)
            
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost
            )
            
        except Exception as e:
             # Capture detailed error if available
             err_msg = str(e)
             if isinstance(e, requests.exceptions.HTTPError):
                 err_msg += f" | Response: {e.response.text}"
                 
             return LLMResponse(
                content="",
                model_name=self.model_name,
                input_tokens=0,
                output_tokens=0,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=err_msg
            )
