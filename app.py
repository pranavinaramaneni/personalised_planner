import streamlit as st
import generator
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="AI Workout & Diet Planner", layout="wide")

st.title("🏋️ Personalized Workout & Diet Planner with AI")
st.markdown("""
Welcome!  
Just fill in your details below, and this AI tool will generate a customized **workout** and **diet plan**  
based on your body, goals, and food preferences — all instantly, no login needed!
""")

with st.form("user_input_form"):
    st.subheader("Enter Your Details 👇")


    name = st.text_input("Enter Your Name", "")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=15, max_value=100, value=22)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    with col2:
        height = st.number_input("Height (cm)", min_value=120, max_value=230, value=170)
        sex = st.selectbox("Sex", ["male", "female"])
    with col3:
        goal = st.selectbox("Fitness Goal", ["lose", "maintain", "gain"])
        activity = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "active"])


    diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian"])


    cuisine = st.multiselect(
        "Cuisine Preference (optional)",
        ["SouthIndian", "NorthIndian", "Chinese", "Continental"]
    )

    all_exercises = ["Push-ups", "Squats", "Plank", "Lunges", "Burpees", "Jumping Jacks"]
    all_equipment = ["none", "dumbbell", "barbell", "kettlebell", "resistance band", "jump rope"]

    equipment = st.multiselect("Available Equipment", all_equipment)
    exercises = st.multiselect("Select Preferred Exercises (optional)", all_exercises)


    submitted = st.form_submit_button("✨ Generate My Personalized Plan")

if submitted:
    if not name:
        st.error("Please enter your name!")
    else:
        activity_factor = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725
        }[activity]

        user = {
            "name": name,
            "age": age,
            "sex": sex,
            "weight": weight,
            "height": height,
            "activity_factor": activity_factor,
            "goal": goal,
            "cuisine": cuisine,
            "equipment": equipment,
            "exercises": exercises,
            "diet_pref": diet_pref
        }

        
        plan = generator.generate_plan(user)

        
        st.success(f"✅ {name}, your personalized workout & diet plan is ready!")

        st.subheader(f"🎯 Daily Calorie Target: {plan['cal_target']} kcal")
        st.caption(f"BMR (Base Metabolic Rate): {plan['bmr']} kcal/day")

        st.markdown("---")
        st.header("🥗 Weekly Meal Plan")
        for day in plan["meals"]:
            st.markdown(f"### 📅 Day {day['day']}")
            meals = day["meals"]

        
            st.write("🍳 **Breakfast:**")
            for item in meals['breakfast']:
                st.write(f"- {item['name']} ({item['cal']} kcal)")

        
            st.write("🍛 **Lunch:**")
            for item in meals['lunch']:
                st.write(f"- {item['name']} ({item['cal']} kcal)")

        
            st.write("🍲 **Dinner:**")
            for item in meals['dinner']:
                st.write(f"- {item['name']} ({item['cal']} kcal)")

            st.write(f"🔥 **Total Calories:** {meals['total_cal']} kcal")
            st.divider()

        st.header("🏋️ Workout Plan")
        for ex in plan["workouts"]:
            st.write(f"- {ex['name']} ({ex['duration_min']} min) — {ex['difficulty']}")

        st.download_button("⬇️ Download Plan (JSON)",
                           generator.to_json(plan),
                           file_name="my_plan.json",
                           mime="application/json")

        
        first_breakfast = plan['meals'][0]['meals']['breakfast'][0]['name']
        first_dinner = plan['meals'][0]['meals']['dinner'][0]['name']

        explanation = (
            f"Hello {name}! Based on your details, your daily calorie target is {plan['cal_target']} calories. "
            f"You will follow {len(plan['workouts'])} workout sessions per week. "
            f"This plan includes healthy meals like {first_breakfast} for breakfast "
            f"and {first_dinner} for dinner. "
            f"Stay consistent, hydrated, and enjoy your fitness journey!"
        )

        tts = gTTS(explanation, lang='en', tld='co.in')
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)

        st.audio(tmp_file.name, format="audio/mp3")

        def cleanup():
            try:
                os.remove(tmp_file.name)
            except:
                pass

        st.button("🛑 Stop Voice", on_click=cleanup)
