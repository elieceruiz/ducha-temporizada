import streamlit as st
from datetime import datetime
import pytz
from pymongo import MongoClient

# Timezone for Colombia
tz = pytz.timezone("America/Bogota")

# MongoDB Atlas connection
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["shower_tracker"]
collection = db["alarm_clock"]

st.set_page_config(page_title="Alarm Response Tracker", layout="centered")
st.title("Did you get up with the alarm?")

# Session state to prevent double submission
if "response_logged" not in st.session_state:
    st.session_state.response_logged = None

col1, col2 = st.columns(2)

# YES button
with col1:
    if st.session_state.response_logged is None:
        if st.button("✅ YES"):
            current_time = datetime.now(tz)
            record = {
                "Activity": "Alarm Clock",
                "Response": "YES",
                "Time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": "Confirmed"
            }
            collection.insert_one(record)
            st.session_state.response_logged = "YES"
            st.success("Saved: ✅ You got up with the alarm.")

# NO button
with col2:
    if st.session_state.response_logged is None:
        if st.button("❌ NO"):
            current_time = datetime.now(tz)
            record = {
                "Activity": "Alarm Clock",
                "Response": "NO",
                "Time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": "Confirmed"
            }
            collection.insert_one(record)
            st.session_state.response_logged = "NO"
            st.warning("Saved: ❌ You did not get up with the alarm.")

# Show response if already submitted
if st.session_state.response_logged:
    st.info(f"You already logged your response: {st.session_state.response_logged}")
