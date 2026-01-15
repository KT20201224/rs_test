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
        
        # [CRITICAL Fix for GCP VM] Force remove automatic GCP credentials
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
        
        # New V1 SDK usage: from google import genai
        from google import genai
        
        # Initialize Client requesting v1beta API version explicitly to avoid Vertex Auth issues
        self.client = genai.Client(
            api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            http_options={'api_version': 'v1beta'}
        )

    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        start_time = time.perf_counter()
        try:
            # V1 SDK: client.models.generate_content
            from google.genai import types
            
            # Configure thinking parameters if needed (Gemini 3 feature)
            # Default to "low" for speed ("flash" optimization) unless specified
            thinking_config = None
            if "thinking_level" in kwargs:
                thinking_config = types.ThinkingConfig(thinking_level=kwargs["thinking_level"])
            
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=kwargs.get("temperature", 0.7),
                thinking_config=thinking_config
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            
            content = response.text
            
            # Usage tracking
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
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
