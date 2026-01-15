import time
import os
import requests
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



