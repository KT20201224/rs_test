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
        "value_accuracy": 0.0,
        "schema_compliance": 0.0,
        "cot_depth_score": 0.0,
        "persona_specificity": 0.0,
        "safety_consistency": 0.0,
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

        # Schema compliance
        valid_types = True
        if "allergies" in data and not isinstance(data["allergies"], list):
            valid_types = False
        metrics["schema_compliance"] = (
            1.0 if valid_types and metrics["field_completeness"] == 1.0 else 0.0
        )

        # 1. Attribute Consistency Check (Basic Value Accuracy)
        if input_data.get("name") == data.get("name"):
            metrics["value_accuracy"] = 1.0

        # 2. Safety/Consistency (Hallucination Check)
        input_allergies = set(input_data.get("allergies", []))
        output_allergies = set(data.get("allergies", []))

        # It's okay to add more (inference), but dropping explicit allergies is CRITICAL failure
        if input_allergies.issubset(output_allergies):
            metrics["safety_consistency"] = 1.0
        else:
            # Failed to preserve critical medical info
            metrics["safety_consistency"] = 0.0

        # Check if preferred foods contain allergy items (Rule-based simple check)
        preferences = " ".join(
            data.get("preferred_food_categories", [])
            + data.get("preferred_ingredients", [])
        )
        if any(allergen in preferences for allergen in output_allergies):
            metrics["safety_consistency"] = 0.5  # Contradiction in output

        # 3. Persona Specificity Score
        # Check description for specific keywords indicating depth
        desc = data.get("description", "")
        # Keywords: contexts, emotions, specifics
        detail_keywords = [
            "퇴근",
            "주말",
            "스트레스",
            "혼밥",
            "데이트",
            "회식",
            "다이어트",
            "건강",
            "가성비",
            "분위기",
            "조용한",
            "시끄러운",
        ]
        specificity_score = 0.0
        if len(desc) > 30:
            specificity_score += 0.4
        found_keywords = [k for k in detail_keywords if k in desc]
        specificity_score += min(0.6, len(found_keywords) * 0.2)
        metrics["persona_specificity"] = specificity_score

        # 4. Reasoniong Depth (CoT)
        reasoning = data.get("reasoning", "")
        logic_keywords = [
            "때문에",
            "위해",
            "하므로",
            "따라서",
            "추론",
            "생각",
            "고려",
            "based on",
            "implies",
        ]
        cot_score = 0.0
        if len(reasoning) > 50:
            cot_score += 0.3
        if any(k in reasoning for k in logic_keywords):
            cot_score += 0.4
        # Bonus for linking two facts
        if len(reasoning) > 100:
            cot_score += 0.3
        metrics["cot_depth_score"] = min(1.0, cot_score)

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
