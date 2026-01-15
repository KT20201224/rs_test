import concurrent.futures
import json
import tqdm
from typing import List, Dict, Any
from .test_cases import PERSONA_GEN_CASES, PERSONA_RATING_CASES, MENU_REC_CASES
from .metrics import calculate_persona_generation_metrics, calculate_persona_rating_metrics, calculate_menu_recommend_metrics, calculate_consistency_metrics, calculate_cot_quality
from models.unified_interface import UnifiedLLMInterface
from utils.cost_tracker import CostTracker
from config import SYSTEM_PROMPTS

class Evaluator:
    def __init__(self, models: List[UnifiedLLMInterface], cost_tracker: CostTracker):
        self.models = models
        self.cost_tracker = cost_tracker
        self.results = []

    def evaluate_task(self, task_name: str, cases: List[Dict]):
        print(f"Starting evaluation for task: {task_name}")
        
        # Helper to process single case
        def process_case(model, case):
            if task_name == "make_persona":
                sys_prompt = SYSTEM_PROMPTS["make_persona"]
                user_prompt = f"User Data: {json.dumps(case['input'], ensure_ascii=False)}"
            elif task_name == "persona_rating":
                sys_prompt = SYSTEM_PROMPTS["persona_rating"]
                user_prompt = f"Persona: {json.dumps(case['persona'], ensure_ascii=False)}\nRestaurant: {json.dumps(case['restaurant'], ensure_ascii=False)}"
            elif task_name == "menu_recommend":
                sys_prompt = SYSTEM_PROMPTS["menu_recommend"]
                user_prompt = f"Group: {json.dumps(case['group'], ensure_ascii=False)}\nRestaurant: {json.dumps(case['restaurant'], ensure_ascii=False)}\nEvent: {json.dumps(case['event'], ensure_ascii=False)}"
            else:
                return None

            # Run Multiple Times if Configured
            from config import EVAL_CONFIG
            n_runs = EVAL_CONFIG.get("n_runs", 1)
            
            run_responses = []
            run_metrics_list = []
            
            for _ in range(n_runs):
                response = model.generate(sys_prompt, user_prompt, temperature=0.0)
                run_responses.append(response)
                
                # Log cost (each run costs money)
                self.cost_tracker.log_request(
                    model=model.model_name,
                    task=task_name,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    latency_ms=response.latency_ms,
                    cost=response.cost_usd,
                    success=response.error is None
                )
                
                if response.error:
                    run_metrics_list.append({})
                    continue

                # Single Run Metrics
                m = {}
                if task_name == "make_persona":
                    m = calculate_persona_generation_metrics(case['input'], response.content)
                    # Add CoT score
                    data = json.loads(response.content) if m.get("json_validity") else {}
                    m["cot_quality"] = calculate_cot_quality(data.get("reasoning", ""))
                elif task_name == "persona_rating":
                    m = calculate_persona_rating_metrics(case, response.content)
                elif task_name == "menu_recommend":
                    m = calculate_menu_recommend_metrics(case, response.content)
                
                run_metrics_list.append(m)

            # Aggregate Results
            # Pick the first valid response for display/base metrics
            first_valid_idx = next((i for i, r in enumerate(run_responses) if not r.error), 0)
            final_response = run_responses[first_valid_idx]
            avg_metrics = run_metrics_list[first_valid_idx] # Default to first run
            
            # Add Consistency Metric
            response_contents = [r.content for r in run_responses]
            consistency = calculate_consistency_metrics(response_contents)
            avg_metrics.update(consistency)
            
            return {
                "task": task_name,
                "case_id": case.get("id"),
                "model": model.model_name,
                "response": final_response.content,
                "metrics": avg_metrics,
                "success": final_response.error is None,
                "error": final_response.error,
                "run_count": n_runs
            }

        # Run in parallel per model? Or sequential per model, parallel per case?
        # Parallel per (model, case) combination
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_meta = {}
            for model in self.models:
                for case in cases:
                    future = executor.submit(process_case, model, case)
                    tasks.append(future)
            
            for future in tqdm.tqdm(concurrent.futures.as_completed(tasks), total=len(tasks), desc=f"Eval {task_name}"):
                result = future.result()
                if result:
                    self.results.append(result)
        
    def run_all(self):
        self.evaluate_task("make_persona", PERSONA_GEN_CASES)
        self.evaluate_task("persona_rating", PERSONA_RATING_CASES)
        self.evaluate_task("menu_recommend", MENU_REC_CASES)
        return self.results
