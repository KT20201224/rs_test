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
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding first { and last }
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        pass

    return None


def calculate_persona_generation_metrics(
    input_data: Dict, response_text: str
) -> Dict[str, float]:
    metrics = {
        "json_validity": 0.0,
        "field_completeness": 0.0,
        "value_accuracy": 0.0,  # Check if critical fields like gender/age preserved
        "inference_quality": 0.5,  # Placeholder, hard to auto-eval without ground truth or another LLM
        "schema_compliance": 0.0,
    }

    data = extract_json(response_text)
    if data:
        metrics["json_validity"] = 1.0

        required_fields = [
            "reasoning",
            "name",
            "gender",
            "age_group",
            "allergies",
            "preferred_food_categories",
            "preferred_ingredients",
            "description",
        ]
        present_fields = [f for f in required_fields if f in data]
        metrics["field_completeness"] = len(present_fields) / len(required_fields)

        # Schema compliance - check types
        valid_types = True
        if "allergies" in data and not isinstance(data["allergies"], list):
            valid_types = False
        metrics["schema_compliance"] = (
            1.0 if valid_types and metrics["field_completeness"] == 1.0 else 0.0
        )

        # Value Accuracy check (simple check of name preservation)
        if input_data.get("name") == data.get("name"):
            metrics["value_accuracy"] = 1.0

        # Inference checklist: if input had no allergies, output should usually match or be empty list
        if not input_data.get("allergies") and not data.get("allergies"):
            pass  # Good

    return metrics


def calculate_consistency_metrics(responses: List[str]) -> Dict[str, float]:
    """Check consistency across multiple runs (simple string/json similarity)"""
    if not responses:
        return {"consistency": 0.0}
    if len(responses) == 1:
        return {"consistency": 1.0}

    # Extract key values for comparison (hash of core fields)
    hashes = []
    for r in responses:
        data = extract_json(r)
        if not data:
            hashes.append("error")
            continue
        # Compare core fields only
        core_data = {
            k: data.get(k) for k in ["name", "allergies", "preferred_food_categories"]
        }
        hashes.append(str(core_data))

    unique_hashes = set(hashes)
    consistency_score = 1.0 / len(unique_hashes) if unique_hashes else 0.0
    return {"consistency": consistency_score}


def calculate_cot_quality(reasoning: str) -> float:
    """Evaluate Chain-of-Thought quality based on length and keywords"""
    if not reasoning:
        return 0.0
    score = 0.5  # Base score for having reasoning

    # Length check
    if len(reasoning) > 50:
        score += 0.2

    # Logic keywords
    keywords = [
        "because",
        "therefore",
        "since",
        "implies",
        "constraint",
        "preference",
        "user",
        "allergy",
    ]
    if any(k in reasoning.lower() for k in keywords):
        score += 0.3

    return min(1.0, score)
