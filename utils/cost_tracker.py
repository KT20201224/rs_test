from typing import Dict, List
import pandas as pd

class CostTracker:
    def __init__(self):
        self.logs = []
        
    def log_request(self, model: str, task: str, input_tokens: int, output_tokens: int, 
                   latency_ms: float, cost: float, success: bool, gpu_mem: float = 0.0, error: str = None):
        entry = {
            "model": model,
            "task": task,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "cost_usd": cost,
            "gpu_memory_mb": gpu_mem,
            "success": success,
            "error": error
        }
        self.logs.append(entry)
        
    def get_summary(self) -> pd.DataFrame:
        if not self.logs:
            return pd.DataFrame()
        return pd.DataFrame(self.logs)
        
    def get_total_cost(self) -> float:
        df = self.get_summary()
        if df.empty: return 0.0
        return df["cost_usd"].sum()
