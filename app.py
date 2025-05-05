import streamlit as st
from datetime import datetime
import pytz
from pymongo import MongoClient
import os

# Colombia timezone
tz = pytz.timezone("America/Bogota")

# MongoDB Atlas connection using environment variable
mongo_uri = os.environ.get("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["shower_tracker"]
collection = db["alarm"]

# Page configuration
st.set_page_config(page_title="Wake-up Tracker", layout="centered")
st.title("Did you get up with your alarm?")

# Session state to prevent multiple answers
if "response_recorded" not in st.session_state:
    st.session_state.response_recorded = None

col1, col2 = st.columns(2)

# "YES" button
with col1:
    if st.session_state.response_recorded is None:
        if st.button("✅ YES"):
            current_time = datetime.now(tz)
            record = {
                "Activity": "Alarm",
                "Answer": "YES",
                "Time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": "Confirmed"
            }
            collection.insert_one(record)
            st.session_state.response_recorded = "YES"
            st.success("Recorded: ✅ You got up with the alarm.")

# "NO" button
with col2:
    if st.session_state.response_recorded is None:
        if st.button("❌ NO"):
            current_time = datetime.now(tz)
            record = {
                "Activity": "Alarm",
                "Answer": "NO",
                "Time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": "Confirmed"
            }
            collection.insert_one(record)
            st.session_state.response_recorded = "NO"
            st.warning("Recorded: ❌ You didn't get up with the alarm.")

# Show response if already recorded
if st.session_state.response_recorded:
    st.info(f"You've already answered: {st.session_state.response_recorded}")
