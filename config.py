import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Model Names
API_MODELS = {"gpt-4o-mini": "gpt-4o-mini"}

LOCAL_MODELS = {
    "qwen2.5-0.5b": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen2.5-1.5b": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "exaone-3.5-2.4b": "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
    "exaone-3.5-7.8b": "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
    "gemma-2-9b": "google/gemma-2-9b-it",
    "ax-4.0-light": "skt/A.X-4.0-Light",
}


# Pricing (USD per 1M tokens) - Estimated for early 2025/Late 2024
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    # Local models have 0 direct cost per token, but we track memory/time
    "qwen2.5-14b": {"input": 0, "output": 0},
    "gemma-2-9b": {"input": 0, "output": 0},
    "ax-4.0-light": {"input": 0, "output": 0},
}


# System Prompts
SYSTEM_PROMPTS = {
    "make_persona": """당신은 '사용자 경험(UX) 리서처'이자 '행동 심리학자'입니다.
    제공된 사용자 프로필(나이, 성별, 취향, 특이사항)을 심층 분석하여, 살아있는 실제 사람처럼 구체적이고 입체적인 '다이닝 페르소나(Dining Persona)'를 생성하세요.
    [분석 단계 및 CoT 가이드]
    1. **프로필 연결**: 나이/성별과 선호 음식, 그리고 'note'에 적힌 뉘앙스를 연결하여 숨겨진 욕구를 찾으세요.
    - 예: "20대 + 헬스" -> "가성비보다는 고단백 식단과 영양 성분 중시"
    - 예: "40대 + 매운맛 + 스트레스" -> "자극적인 맛으로 스트레스를 풀고자 함"
    2. **상황 부여**: 이 사람이 평소 어떤 상황에서 식당을 찾을지 상상하세요. (혼밥, 회식, 데이트 등)
    3. **가치 판단**: 식당 선택 시 절대 양보할 수 없는 것(알러지, 싫어하는 것)과 타협 가능한 것(가격, 거리)을 구분하세요.
    [출력 요구사항]
    - 모든 텍스트는 '한국어'로 작성하세요.
    - 결과는 아래 JSON 형식을 엄격히 따르세요.
    {
    "reasoning": "string (나이, 성별, 취향을 종합한 심층 분석 내용)",
    "name": "string (입력된 이름)",
    "gender": "string",
    "age_group": "string",
    "allergies": ["string"],
    "preferred_food_categories": ["string"],
    "preferred_ingredients": ["string"],
    "dining_style": "string (예: '맛 탐험가형', '효율 중시형', '건강 관리형', 'SNS 과시형' 등)",
    "price_sensitivity": "string (Low/Medium/High - 추론)",
    "preferred_atmosphere": ["string", "string"],
    "key_decision_factors": ["string", "string"],
    "description": "string (이 페르소나의 식습관과 라이프스타일을 한 문단으로 요약)"
    }""",
}

# Evaluation Configuration
EVAL_CONFIG = {
    "n_runs": 3,  # Run 3 times to check consistency
    "timeout": 30,  # seconds per call
    "max_retries": 2,
}
