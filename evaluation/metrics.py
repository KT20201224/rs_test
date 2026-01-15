import json
import re
from typing import List, Dict, Any, Optional

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text, handling markdown blocks."""
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try finding markdown code blocks
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
            
    # Try finding first { and last }
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        pass
        
    return None

def calculate_persona_generation_metrics(input_data: Dict, response_text: str) -> Dict[str, float]:
    metrics = {
        "json_validity": 0.0,
        "field_completeness": 0.0,
        "value_accuracy": 0.0, # Check if critical fields like gender/age preserved
        "inference_quality": 0.5, # Placeholder, hard to auto-eval without ground truth or another LLM
        "schema_compliance": 0.0
    }
    
    data = extract_json(response_text)
    if data:
        metrics["json_validity"] = 1.0
        
        required_fields = ["reasoning", "name", "gender", "age_group", "allergies", "preferred_food_categories", "preferred_ingredients", "description"]
        present_fields = [f for f in required_fields if f in data]
        metrics["field_completeness"] = len(present_fields) / len(required_fields)
        
        # Schema compliance - check types
        valid_types = True
        if "allergies" in data and not isinstance(data["allergies"], list): valid_types = False
        metrics["schema_compliance"] = 1.0 if valid_types and metrics["field_completeness"] == 1.0 else 0.0
        
        # Value Accuracy check (simple check of name preservation)
        if input_data.get("name") == data.get("name"):
            metrics["value_accuracy"] = 1.0
        
        # Inference checklist: if input had no allergies, output should usually match or be empty list
        if not input_data.get("allergies") and not data.get("allergies"):
            pass # Good
            
    return metrics

def calculate_consistency_metrics(responses: List[str]) -> Dict[str, float]:
    """Check consistency across multiple runs (simple string/json similarity)"""
    if not responses: return {"consistency": 0.0}
    if len(responses) == 1: return {"consistency": 1.0}
    
    # Extract key values for comparison (hash of core fields)
    hashes = []
    for r in responses:
        data = extract_json(r)
        if not data: 
            hashes.append("error")
            continue
        # Compare core fields only
        core_data = {k: data.get(k) for k in ["name", "allergies", "preferred_food_categories"]}
        hashes.append(str(core_data))
        
    unique_hashes = set(hashes)
    consistency_score = 1.0 / len(unique_hashes) if unique_hashes else 0.0
    return {"consistency": consistency_score}

def calculate_cot_quality(reasoning: str) -> float:
    """Evaluate Chain-of-Thought quality based on length and keywords"""
    if not reasoning: return 0.0
    score = 0.5 # Base score for having reasoning
    
    # Length check
    if len(reasoning) > 50: score += 0.2
    
    # Logic keywords
    keywords = ["because", "therefore", "since", "implies", "constraint", "preference", "user", "allergy"]
    if any(k in reasoning.lower() for k in keywords):
        score += 0.3
        
    return min(1.0, score)

def calculate_persona_rating_metrics(case: Dict, response_text: str) -> Dict[str, float]:
    metrics = {
        "rating_validity": 0.0,
        "rating_appropriateness": 0.0,
        "reasoning_quality": 0.0,
        "allergy_safety": 1.0, # Start excessive, penalize if needed
        "budget_awareness": 0.0
    }
    
    data = extract_json(response_text)
    if not data:
        return metrics
        
    rating = data.get("score")
    if rating is not None and isinstance(rating, (int, float)) and 0 <= rating <= 10:
        metrics["rating_validity"] = 1.0
    
    # Appropriateness
    expected_type = case["type"]
    score = float(rating) if rating is not None else -1
    
    if expected_type == "positive" and score >= 7:
        metrics["rating_appropriateness"] = 1.0
    elif expected_type == "negative" and score <= 5:
        metrics["rating_appropriateness"] = 1.0
    elif expected_type == "critical":
        # Critical cases should have very low score usually, or explicit warning
        if score <= 3:
            metrics["rating_appropriateness"] = 1.0
            
    # Allergy Safety logic for Rating
    # If case is critical allergy type, reasoning must mention allergy or score must be low
    if expected_type == "critical":
        reason = data.get("reason", "").lower()
        if "allergy" in reason or "allergic" in reason or "unsafe" in reason or score < 2:
            metrics["allergy_safety"] = 1.0
        else:
            metrics["allergy_safety"] = 0.0 # Failed to identify danger
            
    # Reasoning quality - length + logic heuristic
    reason = data.get("reason", "").lower()
    if len(reason) > 20: 
        # Check for logical connectors indicating reasoning
        if any(keyword in reason for keyword in ["because", "since", "due to", "preference", "budget", "allergy", "match", "mismatch", "때문에", "이유", "고려", "선호"]):
            metrics["reasoning_quality"] = 1.0
        else:
            metrics["reasoning_quality"] = 0.5
    else:
        metrics["reasoning_quality"] = 0.0
        
    return metrics

def calculate_menu_recommend_metrics(case: Dict, response_text: str) -> Dict[str, float]:
    metrics = {
        "coverage": 0.0,
        "safety": 1.0,
        "diversity": 0.5,
        "practicality": 0.0,
        "explanation_quality": 0.0
    }
    
    data = extract_json(response_text)
    if not data:
        metrics["safety"] = 0.0
        return metrics
        
    # Safety Check
    # Check if recommended menu intersects with restaurant allergens that match user allergies
    # Simplified: We know restaurant allergens and user allergies. 
    # The menu logic is complex without knowing exactly which menu item contains what allergen in the prompt output structure 
    # unless the LLM output says "this is safe".
    # We will approximate: if the restaurant HAS an allergen, and a user HAS that allergy, 
    # the LLM should explicitly NOT recommend items containing it? Or just warn?
    # The prompt asked for "NO allergens for allergic members".
    # This is hard to check perfectly without breaking down restaurant menu components.
    # We'll check reasoning for safety keywords if high risk.
    
    explanation = data.get("explanation", "").lower()
    menu_items = data.get("menu_items", [])
    
    if menu_items:
        metrics["coverage"] = 1.0 # Assumed coverage if items generated
        
    # Check budget practicality
    total_price = data.get("total_price_estimate", 0)
    budget = case["event"]["budget_per_person"] * case["event"]["num_participants"]
    if total_price > 0 and total_price <= budget * 1.1: # 10% buffer
        metrics["practicality"] = 1.0
        
    # Explanation Quality with logic check
    explanation = data.get("explanation", "").lower()
    if len(explanation) > 30:
        if any(keyword in explanation for keyword in ["selected", "balance", "everyone", "budget", "option", "choice", "group", "선택", "고려", "모두", "예산", "메뉴"]):
            metrics["explanation_quality"] = 1.0
        else:
            metrics["explanation_quality"] = 0.5
    else:
         metrics["explanation_quality"] = 0.0
        
    # Safety Check refinement
    # If any user in group has allergy present in restaurant, check if explanation mentions care/avoidance
    restaurant_allergens = set(case["restaurant"].get("allergens", []))
    group_allergies = set()
    for p in case["group"]:
        group_allergies.update(p.get("allergies", []))
        
    risk_allergens = restaurant_allergens.intersection(group_allergies)
    if risk_allergens:
        # High risk
        if "allergy" in explanation or "safe" in explanation or "exclude" in explanation or "remove" in explanation:
             metrics["safety"] = 1.0
        else:
             metrics["safety"] = 0.5 # Suspicious
    
    return metrics
