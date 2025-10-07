import random
import pandas as pd
import json

# -----------------------------------------
# Basic metabolic rate and calorie helpers
# -----------------------------------------

def bmr_mifflin(age, sex, weight_kg, height_cm):
    """Calculate BMR using Mifflin-St Jeor equation."""
    if sex.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def target_calories(bmr, activity_factor, goal):
    """Adjust calories based on activity and goal."""
    tdee = bmr * activity_factor
    if goal == "lose":
        return int(tdee - 300)
    elif goal == "gain":
        return int(tdee + 300)
    return int(tdee)


# -----------------------------------------
# Load datasets
# -----------------------------------------

def load_data():
    """Load recipe and exercise CSVs."""
    recipes = pd.read_csv("data/recipes.csv")
    exercises = pd.read_csv("data/exercises.csv")
    return recipes, exercises


# -----------------------------------------
# Meal generator
# -----------------------------------------

def choose_meals(cal_target, recipes, cuisine_pref, diet_pref):
    """
    Select breakfast, lunch, and dinner for a day.
    Filters by cuisine and diet (veg/non-veg) and includes all food items.
    """
    meals = {"breakfast": None, "lunch": None, "dinner": None}

    # Filter by cuisine
    if cuisine_pref:
        filtered = recipes[recipes["cuisine"].isin(cuisine_pref)]
        if filtered.empty:
            filtered = recipes
    else:
        filtered = recipes.copy()

    # Filter by diet
    if diet_pref == "Vegetarian":
        filtered = filtered[filtered["type_of_food"] == "veg"]
    else:
        # Include both veg and non-veg
        filtered = filtered

    # Separate by meal type
    breakfasts = filtered[filtered["type"] == "breakfast"]
    lunches = filtered[filtered["type"] == "lunch"]
    dinners = filtered[filtered["type"] == "dinner"]

    # Fallbacks if empty
    if breakfasts.empty:
        breakfasts = recipes[recipes["type"] == "breakfast"]
    if lunches.empty:
        lunches = recipes[recipes["type"] == "lunch"]
    if dinners.empty:
        dinners = recipes[recipes["type"] == "dinner"]

    # Select **all items** in each category for variety
    b = breakfasts.sample(min(len(breakfasts), 2)).to_dict("records")  # up to 2 options
    l = lunches.sample(min(len(lunches), 2)).to_dict("records")
    d = dinners.sample(min(len(dinners), 2)).to_dict("records")

    # Sum calories for total
    total_cal = sum(item["cal"] for item in b + l + d)

    # Store meals
    meals["breakfast"] = b
    meals["lunch"] = l
    meals["dinner"] = d
    meals["total_cal"] = int(total_cal)

    return meals


# -----------------------------------------
# Workout generator
# -----------------------------------------

def choose_workouts(exercises_df, available_equipment, selected_exercises):
    """
    Pick exercises based on selected exercises and available equipment.
    Includes multiple exercises if selected.
    """
    # Filter by equipment
    if "none" in available_equipment:
        filtered = exercises_df
    else:
        filtered = exercises_df[exercises_df["equipment_required"].isin(available_equipment + ["none"])]

    # Filter by selected exercises
    if selected_exercises:
        filtered = filtered[filtered["name"].isin(selected_exercises)]

    # Fallback
    if filtered.empty:
        filtered = exercises_df

    # Select up to 4 exercises randomly
    workouts = filtered.sample(min(4, len(filtered))).to_dict("records")
    return workouts


# -----------------------------------------
# Plan generator
# -----------------------------------------

def generate_plan(user):
    """Generate a complete weekly meal + workout plan with all features."""
    recipes, exercises_df = load_data()

    # Calculate calories
    bmr = bmr_mifflin(user["age"], user["sex"], user["weight"], user["height"])
    cal_target = target_calories(bmr, user["activity_factor"], user["goal"])

    # Weekly meal plan: 7 days
    week_plan = []
    for day in range(7):
        meals = choose_meals(cal_target, recipes, user["cuisine"], user["diet_pref"])
        week_plan.append({"day": day + 1, "meals": meals})

    # Workouts for the week
    workouts = choose_workouts(exercises_df, user["equipment"], user.get("exercises", []))

    # Combine plan
    plan = {
        "name": user.get("name", "User"),
        "bmr": int(bmr),
        "cal_target": int(cal_target),
        "meals": week_plan,
        "workouts": workouts
    }

    return plan


# -----------------------------------------
# Convert plan to JSON
# -----------------------------------------

def to_json(plan):
    return json.dumps(plan, indent=2)
