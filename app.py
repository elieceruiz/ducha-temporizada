import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import plotly.express as px
import pymongo

# MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['morning_routine']
collection = db['sessions']

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=["item", "start_time", "end_time"])

if 'session_start_time' not in st.session_state:
    st.session_state['session_start_time'] = None

if 'current_item' not in st.session_state:
    st.session_state['current_item'] = 0

# Define Colombia timezone using pytz
colombia_tz = pytz.timezone('America/Bogota')

# List of items
items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", "Rolled-up bag",
    "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", "Shaving razor"
]

# Title and Introduction
st.title("Morning Routine Tracker")
st.write("Welcome to Your Morning Routine Tracker!")
st.write("This tool helps you log your morning routine, track the items you pick up, and measure how long it takes you to complete them. Select whether you woke up with the alarm, then proceed to pick the items one by one.")

# Step 1: Ask if you woke up with the alarm (YES/NO options)
st.header("Step 1: Did you wake up with the alarm?")
st.write("Please select YES or NO to start the session:")

# Ask the question first and only allow one option at a time
if 'wake_up_selected' not in st.session_state:
    wake_up_alarm_yes = st.checkbox("YES")
    wake_up_alarm_no = st.checkbox("NO")

    if wake_up_alarm_yes or wake_up_alarm_no:
        st.session_state['wake_up_selected'] = True
        st.session_state['session_start_time'] = datetime.now(colombia_tz)
        st.write(f"Session started at: {st.session_state['session_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        # Disable both checkboxes to avoid re-selection
        st.checkbox("YES", value=False, disabled=True)
        st.checkbox("NO", value=False, disabled=True)

# Step 2: Select the items you took (Checkboxes appear one by one)
if 'wake_up_selected' in st.session_state:
    st.header("Step 2: Select the items you took:")
    st.write("Now, please select the items you took. They will be logged with their start time.")

    # Show the current item to be selected
    if st.session_state['current_item'] < len(items):
        current_item = items[st.session_state['current_item']]
        if st.checkbox(current_item, key=current_item):
            current_time = datetime.now(colombia_tz)
            st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([{"item": current_item, "start_time": current_time, "end_time": None}])], ignore_index=True)
            st.write(f"{current_item} selected at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Move to the next item
            st.session_state['current_item'] += 1

    # Once all items are selected, register the end time and show the log
    if st.session_state['current_item'] == len(items):
        end_time = datetime.now(colombia_tz)
        st.session_state['data']['end_time'] = end_time
        st.write(f"Session ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save to MongoDB
        save_data_to_mongo(st.session_state['data'])

        # Calculate total duration
        duration = (end_time - st.session_state['session_start_time']).seconds
        st.write(f"Total duration: {duration} seconds")

    # Display the log of items selected
    st.subheader("Item Selection Log")
    st.write(st.session_state['data'])

# Graph: Sessions per day and duration per session
if not st.session_state['data'].empty:
    # Convert to pandas DataFrame for graphs
    session_times = pd.to_datetime(st.session_state['data']['start_time'])
    session_days = session_times.dt.date
    session_durations = (pd.to_datetime(st.session_state['data']['end_time']) - session_times).dt.total_seconds()

    # Plot sessions per day graph
    daily_sessions = session_days.value_counts().sort_index()
    fig_sessions = px.bar(x=daily_sessions.index.astype(str), y=daily_sessions.values, labels={'x': 'Date', 'y': 'Number of Sessions'},
                          title="Sessions per Day")

    # Plot session duration per day graph
    fig_duration = px.bar(x=session_days.astype(str), y=session_durations, labels={'x': 'Date', 'y': 'Duration (seconds)'},
                          title="Session Duration per Day")

    st.plotly_chart(fig_sessions)
    st.plotly_chart(fig_duration)

# Function to save data to MongoDB
def save_data_to_mongo(data):
    for index, row in data.iterrows():
        collection.insert_one(row.to_dict())
