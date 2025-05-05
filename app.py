import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# MongoDB connection
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client.shower_tracker
collection = db.sessions

# Timezone
local_tz = pytz.timezone("America/Bogota")

# App layout
st.set_page_config(page_title="Morning Routine Tracker", layout="wide")
st.title("🌅 Morning Routine Tracker")

# Session state for tracking progress
if 'session_start' not in st.session_state:
    st.session_state.session_start = None
if 'items_checked' not in st.session_state:
    st.session_state.items_checked = []
if 'next_index' not in st.session_state:
    st.session_state.next_index = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Routine items
routine_items = [
    "Small chair", "Construction bucket", "Window cleaning cloths", "Rolled-up bag",
    "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb",
    "Shaving razor", "Soaps"
]

# Start session if not started
if st.session_state.session_start is None:
    st.session_state.session_start = datetime.now(local_tz)
    st.session_state.items_checked = []
    st.session_state.next_index = 0
    st.session_state.submitted = False

# Checkbox: Did you wake up with the alarm?
wake_alarm = st.checkbox("✅ I woke up with the alarm", value=False, key="alarm_check")

# Show next item in the list
if st.session_state.next_index < len(routine_items):
    current_item = routine_items[st.session_state.next_index]
    if st.checkbox(f"{current_item}", key=f"item_{st.session_state.next_index}"):
        st.session_state.items_checked.append(current_item)
        st.session_state.next_index += 1

# End of session
elif not st.session_state.submitted:
    session_end = datetime.now(local_tz)
    duration = (session_end - st.session_state.session_start).total_seconds()
    session_data = {
        "wake_up_with_alarm": wake_alarm,
        "items_checked": st.session_state.items_checked,
        "session_start_time": st.session_state.session_start,
        "session_end_time": session_end,
        "session_duration_sec": duration
    }
    collection.insert_one(session_data)
    st.success("✅ Session saved!")
    st.session_state.submitted = True

# Tabs
view_tab, plot_tab = st.tabs(["📋 Table", "📈 Charts"])

# View tab
with view_tab:
    data = [doc for doc in collection.find() if 'session_start_time' in doc]
    if data:
        df = pd.DataFrame(data)
        df['session_start_time'] = pd.to_datetime(df['session_start_time'])
        df['session_end_time'] = pd.to_datetime(df['session_end_time'])
        df['session_date'] = df['session_start_time'].dt.date
        df['duration_min'] = df['session_duration_sec'] / 60
        st.dataframe(df[['session_date', 'wake_up_with_alarm', 'duration_min', 'items_checked']], use_container_width=True)
    else:
        st.info("No session data available yet.")

# Plot tab
with plot_tab:
    if data:
        df_grouped = df.groupby('session_date').agg({
            'session_duration_sec': 'sum',
            '_id': 'count'
        }).rename(columns={'_id': 'sessions'})
        df_grouped['duration_min'] = df_grouped['session_duration_sec'] / 60

        fig, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(x=df_grouped.index, y=df_grouped['sessions'], ax=ax1, color='skyblue')
        ax1.set_ylabel("Sessions")
        ax1.set_xlabel("Date")
        ax1.set_title("Number of Sessions per Day")
        st.pyplot(fig)

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.lineplot(x=df_grouped.index, y=df_grouped['duration_min'], marker='o', ax=ax2, color='green')
        ax2.set_ylabel("Total Time (minutes)")
        ax2.set_xlabel("Date")
        ax2.set_title("Total Session Duration per Day")
        st.pyplot(fig2)
    else:
        st.info("No data for plotting.")
