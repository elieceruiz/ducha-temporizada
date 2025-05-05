import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime
import pytz

# --- MongoDB connection ---
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_tracker"]
collection = db["routine_logs"]

# --- Timezone setting ---
tz = pytz.timezone("America/Bogota")

# --- Static item list ---
items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", "Rolled-up bag",
    "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", "Shaving razor"
]

# --- Initialize session state ---
if "routine_started" not in st.session_state:
    st.session_state.routine_started = False
    st.session_state.woke_up_with_alarm = None
    st.session_state.item_log = {}
    st.session_state.current_item = 0

# --- Header ---
st.title("🌅 Morning Routine Tracker")
st.write("Welcome! Track your routine step-by-step. Select whether you woke up with the alarm.")

# --- Step 1: Wake up confirmation ---
if not st.session_state.routine_started:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ YES", key="yes_button"):
            st.session_state.woke_up_with_alarm = "YES"
            st.session_state.routine_started = True
    with col2:
        if st.button("❌ NO", key="no_button"):
            st.session_state.woke_up_with_alarm = "NO"
            st.session_state.routine_started = True

# --- Step 2: Item logging ---
if st.session_state.routine_started:
    st.success(f"Woke up with the alarm: {st.session_state.woke_up_with_alarm}")

    if st.session_state.current_item < len(items):
        item = items[st.session_state.current_item]
        if st.button(f"✅ Took: {item}"):
            now = datetime.now(tz)
            st.session_state.item_log[item] = now.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.current_item += 1
    else:
        # All items logged: Save to MongoDB
        data = {
            "Woke up with the alarm": st.session_state.woke_up_with_alarm,
            "Start hour": list(st.session_state.item_log.values())[0],
        }
        for item in items:
            data[item] = st.session_state.item_log.get(item, "Not marked")
        data["End hour"] = list(st.session_state.item_log.values())[-1]

        # Calculate total time
        try:
            start = datetime.strptime(data["Start hour"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(data["End hour"], "%Y-%m-%d %H:%M:%S")
            total_time = end - start
            data["Total time"] = str(total_time)
        except Exception as e:
            data["Total time"] = "Error calculating"

        collection.insert_one(data)

        st.success("✅ Routine logged successfully!")

        df = pd.DataFrame([data])
        df_display = df.drop(columns=items)  # Optionally exclude detailed item times
        st.dataframe(df_display)

# --- Display previous records ---
st.markdown("---")
st.subheader("📜 Previous Sessions")
records = list(collection.find().sort("Start hour", -1))

if records:
    df_prev = pd.DataFrame(records)
    df_prev.drop(columns=["_id"], inplace=True)
    df_prev.reset_index(drop=True, inplace=True)
    df_prev.index += 1
    df_prev.index.name = "Session #"
    st.dataframe(df_prev)
else:
    st.info("No previous records found.")
