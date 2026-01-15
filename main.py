import sys
import os
import argparse
from typing import List

# Ensure we can import the package modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restaurant_llm_evaluation.config import API_MODELS, LOCAL_MODELS, OPENAI_API_KEY, GOOGLE_API_KEY
from restaurant_llm_evaluation.models import UnifiedLLMInterface, OpenAIModel, GeminiModel, LocalHuggingFaceModel
from restaurant_llm_evaluation.evaluation.evaluators import Evaluator
from restaurant_llm_evaluation.utils.cost_tracker import CostTracker
from restaurant_llm_evaluation.utils.report_generator import ReportGenerator

def load_models(model_names: List[str]) -> List[UnifiedLLMInterface]:
    models = []
    
    # Check "all" keyword
    if "all" in model_names:
        target_models = list(API_MODELS.keys()) + list(LOCAL_MODELS.keys())
    else:
        target_models = model_names
        
    print(f"Initializing models: {target_models}")
    
    for name in target_models:
        # Check API models
        if name in API_MODELS.values() or name in API_MODELS.keys():
            # Resolve short name to full ID if needed
            full_name = API_MODELS.get(name, name)
            
            if "gpt" in full_name:
                if not OPENAI_API_KEY:
                    print(f"Skipping {name}: OPENAI_API_KEY not found.")
                    continue
                models.append(OpenAIModel(full_name))

            elif "gemini" in full_name:
                if not GOOGLE_API_KEY:
                    print(f"Skipping {name}: GOOGLE_API_KEY not found.")
                    continue
                models.append(GeminiModel(full_name))
        
        # Check Local models
        elif name in LOCAL_MODELS.values() or name in LOCAL_MODELS.keys():
            full_name = LOCAL_MODELS.get(name, name)
            # For local execution, we might skip if not requested or environment issues
            # But here we try to load.
            models.append(LocalHuggingFaceModel(full_name))
        else:
            print(f"Unknown model: {name}")
            
    return models

def main():
    parser = argparse.ArgumentParser(description="Restaurant LLM Internal Evaluation System")
    parser.add_argument("--models", nargs="+", required=True, help="List of models to evaluate (e.g., gpt-4o-mini or 'all')")
    parser.add_argument("--tasks", nargs="+", default="all", help="Tasks to evaluate (default: all)")
    parser.add_argument("--output", default="restaurant_llm_evaluation/results", help="Output directory")
    
    args = parser.parse_args()
    
    # Setup Output
    os.makedirs(args.output, exist_ok=True)
    
    # Identify target models first (without loading)
    target_model_names = []
    if "all" in args.models:
        target_model_names = list(API_MODELS.keys()) + list(LOCAL_MODELS.keys())
    else:
        target_model_names = args.models

    print(f"Target models to evaluate: {target_model_names}")

    # Initialize Tracker
    tracker = CostTracker()
    all_results = []
    
    import gc
    import torch

    for name in target_model_names:
        print(f"\n[{name}] Initializing & Loading...")
        
        current_model = None
        
        # 1. Load Single Model
        try:
            # API Models
            if name in API_MODELS.keys() or name in API_MODELS.values():
                full_name = API_MODELS.get(name, name)
                if "gpt" in full_name:
                    if not OPENAI_API_KEY:
                         print(f"Skipping {name}: OPENAI_API_KEY Missing")
                         continue
                    current_model = OpenAIModel(full_name)
                elif "gemini" in full_name:
                    if not GOOGLE_API_KEY:
                        print(f"Skipping {name}: GOOGLE_API_KEY Missing")
                        continue
                    current_model = GeminiModel(full_name)
            
            # Local Models
            elif name in LOCAL_MODELS.keys() or name in LOCAL_MODELS.values():
                full_name = LOCAL_MODELS.get(name, name)
                current_model = LocalHuggingFaceModel(full_name)
            
            else:
                print(f"Unknown model config: {name}")
                continue
                
        except Exception as e:
            print(f"Error loading model {name}: {e}")
            continue

        if not current_model:
            continue

        # 2. Evaluate Single Model
        try:
            # Create a temporary evaluator for just this model
            evaluator = Evaluator([current_model], tracker)
            run_results = evaluator.run_all()
            all_results.extend(run_results)
        except Exception as e:
            print(f"Error evaluating model {name}: {e}")
        
        # 3. Unload & Clean Memory
        print(f"[{name}] Unloading...")
        del current_model
        del evaluator
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if torch.backends.mps.is_available():
            try:
                torch.mps.empty_cache()
            except AttributeError:
                pass # Some older torch versions might not accept this

    # Report
    reporter = ReportGenerator(args.output)
    reporter.generate_report(all_results, tracker.get_summary())
    
if __name__ == "__main__":
    main()
