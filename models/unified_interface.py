from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
import time

@dataclass
class LLMResponse:
    content: str
    model_name: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    error: Optional[str] = None
    cost_usd: float = 0.0
    gpu_memory_mb: float = 0.0

class UnifiedLLMInterface(ABC):
    """Abstract base class for all LLM wrappers."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        """Generate a response from the model."""
        pass
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model pricing."""
        # This can be overridden or use a lookup utility
        return 0.0
