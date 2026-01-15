import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Model Names
API_MODELS = {
    "gpt-4o-mini": "gpt-4o-mini"
}

LOCAL_MODELS = {
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "gemma-2-9b": "google/gemma-2-9b-it",
    "ax-4.0-light": "skt/A.X-4.0-Light"
}



# Pricing (USD per 1M tokens) - Estimated for early 2025/Late 2024
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    # Local models have 0 direct cost per token, but we track memory/time
    "qwen2.5-14b": {"input": 0, "output": 0},
    "gemma-2-9b": {"input": 0, "output": 0},
    "ax-4.0-light": {"input": 0, "output": 0}
}


# System Prompts
SYSTEM_PROMPTS = {
    "make_persona": """당신은 데이터 분석 전문가입니다.
입력된 사용자 프로필을 바탕으로 구조화된 페르소나 JSON 객체를 생성하세요.
단계 1: 사용자 프로필을 분석하여 선호도와 잠재적인 제약 사항(알러지 등)을 추론하세요 (CoT).
단계 2: 최종 JSON을 생성하세요.

모든 텍스트 값은 '한국어'로 작성해야 합니다.
오직 유효한 JSON 형식으로만 출력하세요:
{
    "reasoning": "string (분석 과정)",
    "name": "string",
    "gender": "string",
    "age_group": "string",
    "allergies": ["string"],
    "preferred_food_categories": ["string"],
    "preferred_ingredients": ["string"],
    "description": "string (페르소나 요약 설명)"
}""",
    
    "persona_rating": """당신은 개인화된 맛집 추천 전문가입니다.
특정 식당이 사용자 페르소나와 얼마나 잘 맞는지 0점에서 10점 사이로 평가하세요.
음식 취향, 알러지(매우 중요), 예산을 고려하세요.
평가 점수에 대한 이유를 설명하세요.

모든 텍스트 값은 '한국어'로 작성해야 합니다.
출력 형식: {"score": float, "reason": "string (한국어)"}""",
    
    "menu_recommend": """당신은 전문 메뉴 플래너입니다.
참가자들의 프로필과 식당 메뉴를 바탕으로 단체 식사 메뉴를 제안하세요.
알러지가 있는 멤버를 위해 알러지 유발 재료가 없는지 반드시 확인하세요.
그룹의 선호도를 균형 있게 고려하세요.

모든 텍스트 값은 '한국어'로 작성해야 합니다.
출력 형식: {"menu_items": ["item1", "item2"], "total_price_estimate": int, "explanation": "string (한국어)"}"""
}

# Evaluation Configuration
EVAL_CONFIG = {
    "n_runs": 3,  # Run 3 times to check consistency
    "timeout": 30, # seconds per call
    "max_retries": 2
}
