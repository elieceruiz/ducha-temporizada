import streamlit as st
from datetime import datetime
import pytz
from pymongo import MongoClient

# Time zone for Colombia
tz = pytz.timezone("America/Bogota")

# MongoDB Atlas connection
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["shower_tracker"]
coleccion = db["sessions"]

st.set_page_config(page_title="Shower Tracker", layout="centered")
st.title("Did you get up with your alarm?")

# Session state to track if we've already recorded the alarm response
if "alarm_recorded" not in st.session_state:
    st.session_state.alarm_recorded = False

# Collect alarm response (YES or NO)
col1, col2 = st.columns(2)

with col1:
    if not st.session_state.alarm_recorded:
        if st.button("✅ YES, I got up with the alarm"):
            hora_actual = datetime.now(tz)
            registro = {
                "Alarm_Response": "YES",
                "Alarm_Time": hora_actual.strftime("%Y-%m-%d %H:%M:%S"),
                "Actions": {},
                "Time_Recorded": hora_actual.strftime("%Y-%m-%d %H:%M:%S")
            }
            coleccion.insert_one(registro)
            st.session_state.alarm_recorded = True
            st.success("You got up with the alarm, your session is recorded.")

with col2:
    if not st.session_state.alarm_recorded:
        if st.button("❌ NO, I did not get up with the alarm"):
            hora_actual = datetime.now(tz)
            registro = {
                "Alarm_Response": "NO",
                "Alarm_Time": hora_actual.strftime("%Y-%m-%d %H:%M:%S"),
                "Actions": {},
                "Time_Recorded": hora_actual.strftime("%Y-%m-%d %H:%M:%S")
            }
            coleccion.insert_one(registro)
            st.session_state.alarm_recorded = True
            st.warning("You did not get up with the alarm, your session is recorded.")

# Display checkboxes for the items
st.subheader("Please check the items you've used:")

actions = [
    "Small chair/bench",
    "Construction bucket",
    "Cloths for cleaning windows",
    "Rolled-up bag",
    "Soaps",
    "Shampoo",
    "Conditioner",
    "Hair collecting sponge",
    "Glass cleaner",
    "Comb",
    "Shaving razor"
]

# Initialize actions in session state if not already done
if "actions_checked" not in st.session_state:
    st.session_state.actions_checked = {}

# Process the actions
for action in actions:
    checked = st.checkbox(action, key=action)
    
    if checked:
        # Store time when the item is checked
        if action not in st.session_state.actions_checked:
            st.session_state.actions_checked[action] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            # Update MongoDB with the current time for the checked item
            coleccion.update_one(
                {"Alarm_Response": {"$in": ["YES", "NO"]}},
                {"$set": {f"Actions.{action}": st.session_state.actions_checked[action]}}
            )
            st.success(f"Time recorded for: {action}")

# Display the recorded actions and times
if st.session_state.actions_checked:
    st.subheader("Actions and Times Recorded:")
    for action, time in st.session_state.actions_checked.items():
        st.write(f"{action}: {time}")
