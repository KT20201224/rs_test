# Restaurant LLM Evaluation System 🧪

이 프레임워크는 **LLM의 '사용자 페르소나 생성 능력'**을 정량적, 정성적으로 평가하기 위해 설계되었습니다. 단순한 데이터 생성을 넘어, LLM이 얼마나 **입체적이고 논리적인 사용자 프로필**을 만들어낼 수 있는지 검증합니다.

## 🎯 테스트 개요 (What We Test)

**Task: 다이닝 페르소나 생성 (Persona Generation)**
- **입력 (Input)**: 사용자의 기본 정보 (나이, 성별, 선호 음식, 특이사항/Note)
- **출력 (Output)**: 구조화된 JSON 프로필
  - **Reasoning**: 페르소나 도출을 위한 심층 추론 (Why & How)
  - **Dining Context**: 선호하는 식사 분위기, 가격 민감도, 의사결정 핵심 요인
  - **Description**: 사용자의 라이프스타일과 식습관을 반영한 구체적 묘사

---

## 📊 평가 지표 (Metrics)

이 시스템은 생성된 페르소나의 품질을 **4가지 핵심 차원**에서 평가합니다.

### 1. 추론 깊이 (CoT Depth Score)
- **의미**: 모델이 단순 정보 나열을 넘어, **"왜"** 그런 취향을 가졌는지 논리적으로 추론했는가?
- **평가 기준**:
  - 추론 과정(`reasoning`)의 길이 및 복잡성
  - 논리적 연결사("때문에", "따라서", "implies" 등) 사용 여부
  - 입력된 단편적 정보들(나이 + 특이사항)을 유기적으로 연결했는지 여부

### 2. 구체성 (Persona Specificity)
- **의미**: 생성된 페르소나가 **"살아있는 사람처럼"** 구체적이고 생생한가?
- **평가 기준**:
  - 설명(`description`)에 포함된 구체적 **상황 키워드** (예: "퇴근", "회식", "데이트", "스트레스 해소", "주말 브런치")
  - 상투적인 표현("맛있는 것을 좋아함") 대신 구체적 라이프스타일 묘사 여부

### 3. 안전성 및 일관성 (Safety & Consistency)
- **의미**: 모델이 **사실(Fact)**을 왜곡하거나 위험한 정보를 생성하지 않았는가?
- **평가 기준**:
  - **알러지 보존**: 입력된 알러지 정보가 출력에 그대로 유지되었는가? (누락 시 0점)
  - **모순 체크**: 알러지가 있는 식재료를 '선호 음식'에 포함시키는 환각(Hallucination) 여부 (발견 시 감점)

### 4. 구조적 건전성 (Structural Health)
- **JSON Validity**: JSON 포맷 파싱 성공 여부
- **Field Completeness**: 필수 스키마 필드 누락 여부

---

## 🚀 시작하기 (How to Run)

### 1. 환경 설정
`.env` 파일에 API 키를 설정합니다.
```bash
OPENAI_API_KEY=sk-...
```

### 2. 평가 실행
```bash
# OpenAI GPT-4o-mini 모델 평가
python main.py --models gpt-4o-mini

# 전체 모델 평가 (로컬 모델 포함)
python main.py --models all
```

### 3. 결과 확인
`results/` 디렉토리에 **Markdown 리포트**와 **Raw JSON** 파일이 생성됩니다.
- `report_YYYYMMDD_... .md`: 모델별 성능 비교표 및 비용 분석 요약

---

## 📂 프로젝트 구조
- `evaluation/`: 테스트 케이스 및 메트릭 로직 (지표 계산 알고리즘 포함)
- `models/`: 모델 인터페이스 (API / Local)
- `utils/`: 비용 추적 및 리포트 생성기
- `config.py`: 프롬프트 템플릿 및 설정값

---
*Created for user-centric AI service evaluation.*
