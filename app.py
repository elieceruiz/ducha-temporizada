import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from pymongo import MongoClient
import time

# MongoDB Atlas URI
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["shower_tracker"]
alarm_collection = db["alarm"]
sessions_collection = db["sessions"]

# Items list
items = [
    "Small chair", "Construction bucket", "Window cleaning cloths", "Rolled-up bag", 
    "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", 
    "Shaving razor", "Soaps"
]

# Create session tracking if not exists
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.items_checked = []
    st.session_state.time_elapsed = 0

# Time zone setup
timezone = pytz.timezone("America/Bogota")

# Wake-up checkbox
wake_up_with_alarm = st.checkbox("Did you wake up with the alarm?")

# Record time logic
if wake_up_with_alarm:
    if st.session_state.start_time is None:
        st.session_state.start_time = datetime.now(timezone)
        st.session_state.items_checked = []
        st.session_state.time_elapsed = 0

# Display item checkboxes
st.write("Select the items you have used:")
for item in items:
    if st.checkbox(item, key=item):
        st.session_state.items_checked.append(item)

# Calculate time elapsed
if st.session_state.start_time:
    st.session_state.end_time = datetime.now(timezone)
    st.session_state.time_elapsed = (st.session_state.end_time - st.session_state.start_time).total_seconds() / 60  # in minutes

# Display elapsed time
st.write(f"Time elapsed: {st.session_state.time_elapsed:.2f} minutes")

# Save the data to MongoDB when done
if st.button("Submit"):
    session_data = {
        "start_time": st.session_state.start_time,
        "end_time": st.session_state.end_time,
        "time_elapsed": st.session_state.time_elapsed,
        "items_checked": st.session_state.items_checked,
        "wake_up_with_alarm": wake_up_with_alarm,
        "date": datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
    }
    sessions_collection.insert_one(session_data)
    st.success("Session data saved!")

# Reset button
if st.button("Reset"):
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.items_checked = []
    st.session_state.time_elapsed = 0
    st.experimental_rerun()
