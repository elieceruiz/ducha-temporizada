import streamlit as st
import pymongo
from datetime import datetime
import pytz

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["routines"]

# Timezone Colombia
tz = pytz.timezone("America/Bogota")

# Routine items
routine_items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", "Rolled-up bag",
    "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", "Shaving razor"
]

st.set_page_config(page_title="Morning Routine Tracker", layout="centered")

# Tabs
tab1, tab2 = st.tabs(["☀️ Morning Routine", "📊 Records"])

with tab1:
    st.title("🧼 Morning Routine Tracker")

    if "started" not in st.session_state:
        st.session_state.started = False
        st.session_state.responses = {}
        st.session_state.index = 0
        st.session_state.start_time = None
        st.session_state.alarm_response = None

    if not st.session_state.started:
        st.write("Did you wake up with the alarm?")
        col1, col2 = st.columns(2)
        with col1:
            yes_check = st.checkbox("YES", key="yes_alarm")
        with col2:
            no_check = st.checkbox("NO", key="no_alarm")

        if yes_check:
            st.session_state.alarm_response = "YES"
            st.session_state.start_time = datetime.now(tz)
            st.session_state.started = True
            st.session_state.responses["Woke up with alarm"] = "YES"
        elif no_check:
            st.session_state.alarm_response = "NO"
            st.session_state.start_time = datetime.now(tz)
            st.session_state.started = True
            st.session_state.responses["Woke up with alarm"] = "NO"

        # Uncheck the other if one is selected
        if yes_check and st.session_state.get("no_alarm"):
            st.session_state["no_alarm"] = False
        if no_check and st.session_state.get("yes_alarm"):
            st.session_state["yes_alarm"] = False

    else:
        if st.session_state.index < len(routine_items):
            current_item = routine_items[st.session_state.index]
            if st.checkbox(f"{current_item}", key=f"item_{st.session_state.index}"):
                st.session_state.responses[current_item] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.index += 1
                st.experimental_rerun()
        else:
            end_time = datetime.now(tz)
            st.session_state.responses["Start hour"] = st.session_state.start_time.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.responses["End hour"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
            total_minutes = round((end_time - st.session_state.start_time).total_seconds() / 60, 2)
            st.session_state.responses["Total time (minutes)"] = total_minutes

            # Save to MongoDB
            collection.insert_one(st.session_state.responses)
            st.success("✅ Routine saved successfully!")

            # Reset session
            st.session_state.started = False
            st.session_state.responses = {}
            st.session_state.index = 0
            st.session_state.start_time = None
            st.session_state.alarm_response = None
            st.session_state.yes_alarm = False
            st.session_state.no_alarm = False

with tab2:
    st.title("📋 Recorded Routines")
    records = list(collection.find())
    if records:
        for i, record in enumerate(records, start=1):
            st.markdown(f"### Routine {i}")
            st.write({k: v for k, v in record.items() if k != "_id"})
    else:
        st.info("No routines recorded yet.")
