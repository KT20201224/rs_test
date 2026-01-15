import json

# Task 1: Persona Generation Inputs
PERSONA_GEN_CASES = [
    # Easy
    {
        "id": "pg_easy_1",
        "difficulty": "easy",
        "input": {
            "name": "Kim Chulsoo",
            "gender": "남성",
            "age_group": "30대",
            "allergies": [],
            "preferred_food_categories": ["한식", "일식"],
            "preferred_ingredients": ["육류", "채소"],
        },
    },
    {
        "id": "pg_easy_2",
        "difficulty": "easy",
        "input": {
            "name": "Lee Younghee",
            "gender": "여성",
            "age_group": "20대",
            "allergies": ["복숭아"],
            "preferred_food_categories": ["양식"],
            "preferred_ingredients": ["해산물"],
        },
    },
    {
        "id": "pg_easy_3",
        "difficulty": "easy",
        "input": {
            "name": "Park Minsoo",
            "gender": "남성",
            "age_group": "40대",
            "allergies": [],
            "preferred_food_categories": ["중식"],
            "preferred_ingredients": ["육류"],
        },
    },
    # Medium (Implicit)
    {
        "id": "pg_med_1",
        "difficulty": "medium",
        "input": {
            "name": "Fitness Junkie",
            "gender": "여성",
            "age_group": "20대",
            "allergies": [],
            "preferred_food_categories": ["세계음식"],
            "preferred_ingredients": ["가금류", "채소"],
            "note": "Trying to gain muscle, avoids fried food",
        },
    },
    {
        "id": "pg_med_2",
        "difficulty": "medium",
        "input": {
            "name": "Vegetarian Fan",
            "gender": "기타",
            "age_group": "30대",
            "allergies": [],
            "preferred_food_categories": ["한식"],
            "preferred_ingredients": ["채소", "곡물/면", "유제품"],
            "note": "No meat at all",
        },
    },
    {
        "id": "pg_med_3",
        "difficulty": "medium",
        "input": {
            "name": "Spicy Lover",
            "gender": "남성",
            "age_group": "50대",
            "allergies": [],
            "preferred_food_categories": ["한식", "중식"],
            "preferred_ingredients": ["해산물"],
            "note": "Loves extremely spicy food",
        },
    },
    {
        "id": "pg_med_4",
        "difficulty": "medium",
        "input": {
            "name": "Light Eater",
            "gender": "여성",
            "age_group": "60대 이상",
            "allergies": [],
            "preferred_food_categories": ["일식"],
            "preferred_ingredients": ["채소", "해산물"],
            "note": "Small portions only",
        },
    },
    # Hard (Complex/Medical)
    {
        "id": "pg_hard_1",
        "difficulty": "hard",
        "input": {
            "name": "Multiple Allergies",
            "gender": "남성",
            "age_group": "20대",
            "allergies": ["새우", "게", "조개류", "땅콩"],
            "preferred_food_categories": ["한식", "양식"],
            "preferred_ingredients": ["육류"],
        },
    },
    {
        "id": "pg_hard_2",
        "difficulty": "hard",
        "input": {
            "name": "Keto Dieter",
            "gender": "여성",
            "age_group": "30대",
            "allergies": ["밀"],
            "preferred_food_categories": ["양식", "세계음식"],
            "preferred_ingredients": ["육류", "채소", "유제품"],
            "note": "Strict Keto, no carbs",
        },
    },
    {
        "id": "pg_hard_3",
        "difficulty": "hard",
        "input": {
            "name": "Elderly Care",
            "gender": "남성",
            "age_group": "60대 이상",
            "allergies": ["우유", "대두"],
            "preferred_food_categories": ["한식"],
            "preferred_ingredients": ["채소", "곡물/면"],
            "note": "Low salt, soft texture needed",
        },
    },
]
