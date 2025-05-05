import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['morning_routine']
collection = db['sessions']

st.title("Morning Routine Tracker")

# Items list
items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", "Rolled-up bag",
    "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge",
    "Glass cleaner", "Comb", "Shaving razor"
]

# Initialize session state
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'alarm_checked' not in st.session_state:
    st.session_state.alarm_checked = False
if 'item_times' not in st.session_state:
    st.session_state.item_times = {}
if 'table_displayed' not in st.session_state:
    st.session_state.table_displayed = False

# Step 1: Alarm checkbox
st.write("Step 1: Did you wake up with the alarm?")
alarm = st.checkbox("Woke up with the alarm")
if alarm and not st.session_state.alarm_checked:
    st.session_state.start_time = datetime.now()
    st.session_state.alarm_checked = True

# Step 2: Items checkboxes
st.write("Step 2: Select the items you took:")

all_checked = True
for item in items:
    if item not in st.session_state.item_times:
        st.session_state.item_times[item] = None
    checked = st.checkbox(item, key=item)
    if checked and st.session_state.item_times[item] is None:
        st.session_state.item_times[item] = datetime.now()
    if not checked:
        all_checked = False

# Step 3: Display table when all items are checked
if all_checked and not st.session_state.table_displayed:
    end_time = max(st.session_state.item_times.values())
    total_time = (end_time - st.session_state.start_time).total_seconds() if st.session_state.start_time else None

    data = {
        "Woke up with alarm": ["Yes" if alarm else "No"],
        "Start hour": [st.session_state.start_time.strftime("%Y-%m-%d %H:%M:%S") if st.session_state.start_time else "N/A"]
    }

    for item in items:
        timestamp = st.session_state.item_times[item]
        data[item] = [timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else ""]

    data["Finish hour"] = [end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else "N/A"]
    data["Total time (seconds)"] = [total_time if total_time else "N/A"]

    df = pd.DataFrame(data)

    # Save to MongoDB
    collection.insert_one(data)

    st.subheader("Routine Summary")
    st.dataframe(df)

    st.session_state.table_displayed = True
