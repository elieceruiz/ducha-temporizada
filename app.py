import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pytz
import pandas as pd

# MongoDB connection
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client.shower_tracker
collection = db.sessions

# Timezone
local_tz = pytz.timezone("America/Bogota")

# App layout
st.set_page_config(page_title="Morning Routine Tracker", layout="wide")
st.title("Morning Routine Tracker")

# Session state
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now(local_tz)
    st.session_state.items_checked = []
    st.session_state.next_index = 0
    st.session_state.events = []
    st.session_state.session_saved = False

# Routine items
routine_items = [
    "Small chair", "Construction bucket", "Window cleaning cloths", "Rolled-up bag",
    "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb",
    "Shaving razor", "Soaps"
]

# Step 1: Wake-up checkbox
if 'wake_checked' not in st.session_state:
    st.session_state.wake_checked = False

if not st.session_state.wake_checked:
    woke_up = st.checkbox("Did you wake up with the alarm?")
    if woke_up:
        st.session_state.wake_checked = True
        st.session_state.events.append({
            "event": "wake_up_with_alarm",
            "value": True,
            "timestamp": datetime.now(local_tz)
        })
else:
    if st.session_state.next_index < len(routine_items):
        current_item = routine_items[st.session_state.next_index]
        if st.button(f"Done: {current_item}"):
            st.session_state.items_checked.append(current_item)
            st.session_state.events.append({
                "event": current_item,
                "timestamp": datetime.now(local_tz)
            })
            st.session_state.next_index += 1
    else:
        if not st.session_state.session_saved:
            session_end = datetime.now(local_tz)
            session_data = {
                "wake_up_with_alarm": True,
                "session_start_time": st.session_state.session_start,
                "session_end_time": session_end,
                "items_checked": st.session_state.items_checked,
                "events": st.session_state.events
            }
            collection.insert_one(session_data)
            st.session_state.session_saved = True
            st.success("Session saved.")

# Tabs
view_tab = st.tabs(["Table"])[0]

with view_tab:
    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        df['session_start_time'] = pd.to_datetime(df['session_start_time'])
        df['session_end_time'] = pd.to_datetime(df['session_end_time'])
        df['session_date'] = df['session_start_time'].dt.date
        df['duration_min'] = (df['session_end_time'] - df['session_start_time']).dt.total_seconds() / 60
        st.dataframe(df[['session_date', 'wake_up_with_alarm', 'duration_min', 'items_checked']], use_container_width=True)
    else:
        st.info("No session data available yet.")
