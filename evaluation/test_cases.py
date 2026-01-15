import json

# Task 1: Persona Generation Inputs
PERSONA_GEN_CASES = [
    # Easy
    {
        "id": "pg_easy_1", "difficulty": "easy",
        "input": {"name": "Kim Chulsoo", "gender": "남성", "age_group": "30대", "allergies": [], "preferred_food_categories": ["한식", "일식"], "preferred_ingredients": ["육류", "채소"]}
    },
    {
        "id": "pg_easy_2", "difficulty": "easy",
        "input": {"name": "Lee Younghee", "gender": "여성", "age_group": "20대", "allergies": ["복숭아"], "preferred_food_categories": ["양식"], "preferred_ingredients": ["해산물"]}
    },
    {
        "id": "pg_easy_3", "difficulty": "easy",
        "input": {"name": "Park Minsoo", "gender": "남성", "age_group": "40대", "allergies": [], "preferred_food_categories": ["중식"], "preferred_ingredients": ["육류"]}
    },
    # Medium (Implicit)
    {
        "id": "pg_med_1", "difficulty": "medium",
        "input": {"name": "Fitness Junkie", "gender": "여성", "age_group": "20대", "allergies": [], "preferred_food_categories": ["세계음식"], "preferred_ingredients": ["가금류", "채소"], "note": "Trying to gain muscle, avoids fried food"}
    },
    {
        "id": "pg_med_2", "difficulty": "medium",
        "input": {"name": "Vegetarian Fan", "gender": "기타", "age_group": "30대", "allergies": [], "preferred_food_categories": ["한식"], "preferred_ingredients": ["채소", "곡물/면", "유제품"], "note": "No meat at all"}
    },
    {
        "id": "pg_med_3", "difficulty": "medium",
        "input": {"name": "Spicy Lover", "gender": "남성", "age_group": "50대", "allergies": [], "preferred_food_categories": ["한식", "중식"], "preferred_ingredients": ["해산물"], "note": "Loves extremely spicy food"}
    },
    {
        "id": "pg_med_4", "difficulty": "medium",
        "input": {"name": "Light Eater", "gender": "여성", "age_group": "60대 이상", "allergies": [], "preferred_food_categories": ["일식"], "preferred_ingredients": ["채소", "해산물"], "note": "Small portions only"}
    },
    # Hard (Complex/Medical)
    {
        "id": "pg_hard_1", "difficulty": "hard",
        "input": {"name": "Multiple Allergies", "gender": "남성", "age_group": "20대", "allergies": ["새우", "게", "조개류", "땅콩"], "preferred_food_categories": ["한식", "양식"], "preferred_ingredients": ["육류"]}
    },
    {
        "id": "pg_hard_2", "difficulty": "hard",
        "input": {"name": "Keto Dieter", "gender": "여성", "age_group": "30대", "allergies": ["밀"], "preferred_food_categories": ["양식", "세계음식"], "preferred_ingredients": ["육류", "채소", "유제품"], "note": "Strict Keto, no carbs"}
    },
    {
        "id": "pg_hard_3", "difficulty": "hard",
        "input": {"name": "Elderly Care", "gender": "남성", "age_group": "60대 이상", "allergies": ["우유", "대두"], "preferred_food_categories": ["한식"], "preferred_ingredients": ["채소", "곡물/면"], "note": "Low salt, soft texture needed"}
    }
]

# Task 2: Persona Rating Inputs
# Format: {"persona": {...}, "restaurant": {...}, "expected_type": "positive/negative/critical"}

# Sample Common Objects
R_KOREAN_MEAT = {
    "name": "Hanwoo Sarang", 
    "category": "한식", 
    "menu": [{"name": "Galbi", "price": 45000}, {"name": "Bulgogi", "price": 25000}, {"name": "Bibimbap", "price": 12000}], 
    "allergens": ["대두", "참깨", "소고기"], 
    "max_capacity": 50
}
R_SEAFOOD_BUFFET = {
    "name": "Ocean Feast", 
    "category": "양식", 
    "menu": [{"name": "Sushi", "price": 30000}, {"name": "Crab Boil", "price": 60000}, {"name": "Shrimp Pasta", "price": 22000}], 
    "allergens": ["새우", "게", "조개류", "밀", "우유"], 
    "max_capacity": 100
}
R_VEGAN_CAFE = {
    "name": "Green Peace", 
    "category": "세계음식", 
    "menu": [{"name": "Salad", "price": 11000}, {"name": "Tofu Steak", "price": 15000}, {"name": "Smoothie", "price": 8000}], 
    "allergens": ["대두", "호두", "토마토"], 
    "max_capacity": 20
}

P_MEAT_LOVER = {"name": "Meat Lover", "allergies": [], "preferred_food_categories": ["한식"], "preferred_ingredients": ["육류"]}
P_SEAFOOD_ALLERGY = {"name": "Allergic User", "allergies": ["새우", "게"], "preferred_food_categories": ["한식"], "preferred_ingredients": ["육류"]}
P_BUDGET_SAVER = {"name": "Student", "allergies": [], "preferred_food_categories": ["분식"], "preferred_ingredients": ["곡물/면"]} # implied low budget

PERSONA_RATING_CASES = [
    # Positive Match (5)
    {"id": "pr_pos_1", "type": "positive", "persona": P_MEAT_LOVER, "restaurant": R_KOREAN_MEAT},
    {"id": "pr_pos_2", "type": "positive", "persona": {"name": "Seafood Fan", "allergies": [], "preferred_food_categories": ["양식", "일식"], "preferred_ingredients": ["해산물"]}, "restaurant": R_SEAFOOD_BUFFET},
    {"id": "pr_pos_3", "type": "positive", "persona": {"name": "Vegan", "allergies": [], "preferred_food_categories": ["세계음식"], "preferred_ingredients": ["채소"]}, "restaurant": R_VEGAN_CAFE},
    {"id": "pr_pos_4", "type": "positive", "persona": {"name": "General", "allergies": [], "preferred_food_categories": ["한식"], "preferred_ingredients": ["육류"]}, "restaurant": {"name": "Samgyupsal House", "category": "한식", "menu": [{"name": "Pork Belly", "price": 15000}], "allergens": ["돼지고기"], "max_capacity": 40}},
    {"id": "pr_pos_5", "type": "positive", "persona": {"name": "Noodle Lover", "allergies": [], "preferred_food_categories": ["중식"], "preferred_ingredients": ["곡물/면"]}, "restaurant": {"name": "Dragon Wok", "category": "중식", "menu": [{"name": "Jajangmyeon", "price": 8000}], "allergens": ["밀", "대두", "돼지고기"], "max_capacity": 30}},

    # Negative Match (5)
    {"id": "pr_neg_1", "type": "negative", "persona": P_MEAT_LOVER, "restaurant": R_VEGAN_CAFE},
    {"id": "pr_neg_2", "type": "negative", "persona": {"name": "Hater of Raw", "allergies": [], "preferred_food_categories": ["한식"], "preferred_ingredients": ["육류"], "note": "Hates raw fish"}, "restaurant": {"name": "Sushi World", "category": "일식", "menu": [{"name": "Sashimi", "price": 40000}], "allergens": ["생선"], "max_capacity": 10}},
    {"id": "pr_neg_3", "type": "negative", "persona": {"name": "Spicy Hater", "allergies": [], "preferred_food_categories": ["일식"], "preferred_ingredients": ["채소"]}, "restaurant": {"name": "Red Pepper", "category": "한식", "menu": [{"name": "Spicy Chicken", "price": 20000}], "allergens": ["닭고기", "고추"], "max_capacity": 20}},
    {"id": "pr_neg_4", "type": "negative", "persona": {"name": "Fine Dining Seeker", "allergies": [], "preferred_food_categories": ["양식"], "preferred_ingredients": ["기타"]}, "restaurant": {"name": "Quick Burger", "category": "양식", "menu": [{"name": "Burger", "price": 6000}], "allergens": ["밀"], "max_capacity": 100}}, # Mismatch vibe
    {"id": "pr_neg_5", "type": "negative", "persona": {"name": "Large Group Rep", "allergies": [], "preferred_food_categories": ["한식"], "preferred_ingredients": ["육류"]}, "restaurant": {"name": "Tiny Hole", "category": "한식", "menu": [{"name": "Rice", "price": 1000}], "allergens": [], "max_capacity": 4}}, # Capacity issue if context known (users don't have group size here but maybe implied or just preference mismatch) - Actually persona rating usually is 1:1. I'll rely on category preference mismatch here for now.
    
    # Critical Safety (5)
    {"id": "pr_crit_1", "type": "critical", "persona": P_SEAFOOD_ALLERGY, "restaurant": R_SEAFOOD_BUFFET},
    {"id": "pr_crit_2", "type": "critical", "persona": {"name": "Nut Allergy", "allergies": ["땅콩", "호두"], "preferred_food_categories": ["양식"], "preferred_ingredients": ["유제품"]}, "restaurant": {"name": "Nutty Desserts", "category": "양식", "menu": [{"name": "Peanut Butter Cake", "price": 7000}], "allergens": ["땅콩", "밀", "우유"], "max_capacity": 20}},
    {"id": "pr_crit_3", "type": "critical", "persona": {"name": "Gluten Free", "allergies": ["밀"], "preferred_food_categories": ["한식"], "preferred_ingredients": ["곡물/면"]}, "restaurant": {"name": "Noodle Factory", "category": "한식", "menu": [{"name": "Kalguksu", "price": 9000}], "allergens": ["밀", "조개류"], "max_capacity": 50}},
    {"id": "pr_crit_4", "type": "critical", "persona": {"name": "Dairy Allergy", "allergies": ["우유"], "preferred_food_categories": ["양식"], "preferred_ingredients": ["채소"]}, "restaurant": {"name": "Cheese House", "category": "양식", "menu": [{"name": "Pizza", "price": 18000}, {"name": "Fondue", "price": 25000}], "allergens": ["우유", "밀"], "max_capacity": 60}},
    {"id": "pr_crit_5", "type": "critical", "persona": {"name": "Shellfish Allergy", "allergies": ["조개류", "전복"], "preferred_food_categories": ["한식"], "preferred_ingredients": ["해산물"]}, "restaurant": {"name": "Clam Roast", "category": "한식", "menu": [{"name": "Grilled Clams", "price": 35000}], "allergens": ["조개류"], "max_capacity": 80}},
]

# Task 3: Menu Recommendation Inputs
# Format: {"group": [...], "restaurant": {...}, "event_details": {...}}

MENU_REC_CASES = [
    # Small Group (3)
    {"id": "mr_small_1", "group": [P_MEAT_LOVER, P_BUDGET_SAVER], "restaurant": R_KOREAN_MEAT, "event": {"budget_per_person": 30000, "num_participants": 2}},
    {"id": "mr_small_2", "group": [P_MEAT_LOVER, P_SEAFOOD_ALLERGY], "restaurant": R_KOREAN_MEAT, "event": {"budget_per_person": 50000, "num_participants": 2}},
    {"id": "mr_small_3", "group": [{"name": "A", "allergies": [], "preferred_ingredients": ["채소"]}, {"name": "B", "allergies": [], "preferred_ingredients": ["채소"]}], "restaurant": R_VEGAN_CAFE, "event": {"budget_per_person": 20000, "num_participants": 2}},
    
    # Medium Group (4)
    {"id": "mr_med_1", "group": [P_MEAT_LOVER, P_BUDGET_SAVER, P_SEAFOOD_ALLERGY, {"name": "Guest", "allergies": [], "preferred_ingredients": ["채소"]}], "restaurant": R_KOREAN_MEAT, "event": {"budget_per_person": 40000, "num_participants": 4}},
    {"id": "mr_med_2", "group": [P_MEAT_LOVER]*5, "restaurant": R_KOREAN_MEAT, "event": {"budget_per_person": 100000, "num_participants": 5}},
    {"id": "mr_med_3", "group": [P_SEAFOOD_ALLERGY, P_BUDGET_SAVER, {"name": "C", "allergies": ["밀"], "preferred_ingredients": ["육류"]}, {"name": "D", "allergies": [], "preferred_ingredients": ["채소"]}], "restaurant": {"name": "Family Restaurant", "category": "양식", "menu": [{"name": "Steak", "price": 35000}, {"name": "Salad", "price": 12000}, {"name": "Pasta", "price": 16000}, {"name": "Risotto", "price": 17000}], "allergens": ["밀", "우유", "소고기"], "max_capacity": 100}, "event": {"budget_per_person": 30000, "num_participants": 4}},
    {"id": "mr_med_4", "group": [{"name": f"P{i}", "allergies": [], "preferred_ingredients": ["육류"]} for i in range(6)], "restaurant": R_KOREAN_MEAT, "event": {"budget_per_person": 25000, "num_participants": 6}}, # Budget constraint tight
    
    # Large Group (3)
    {"id": "mr_large_1", "group": [P_MEAT_LOVER]*10, "restaurant": R_KOREAN_MEAT, "event": {"budget_per_person": 50000, "num_participants": 10}},
    {"id": "mr_large_2", "group": [P_MEAT_LOVER]*5 + [P_SEAFOOD_ALLERGY]*5, "restaurant": R_SEAFOOD_BUFFET, "event": {"budget_per_person": 80000, "num_participants": 10}}, # Risky choice for allergy
    {"id": "mr_large_3", "group": [{"name": f"U{i}", "allergies": ["복숭아"] if i%2==0 else [], "preferred_ingredients": ["채소"]} for i in range(12)], "restaurant": R_VEGAN_CAFE, "event": {"budget_per_person": 15000, "num_participants": 12}} # Capacity fine (20), Allergies fine usually
]
