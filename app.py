import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import pytz  # Importing pytz for timezone management
import plotly.express as px  # Importing Plotly for the interactive graph

# MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['morning_routine']  # Updated database name
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

# Title and description
st.title("Morning Routine Tracker")
st.markdown("""
    ## Welcome to Your Morning Routine Tracker!
    This tool helps you log your morning routine, track the items you pick up, and measure how long it takes you to complete them.
    Select whether you woke up with the alarm, then proceed to pick the items one by one.
""")

# Tab 1: Ask if you woke up with the alarm (checkbox for YES and NO)
st.markdown("### Step 1: Did you wake up with the alarm?")
st.write("Please select **YES** or **NO** to start the session:")

# Create checkboxes for "YES" and "NO" side by side (front and back)
col1, col2 = st.columns([1, 1])  # Two columns with equal width

with col1:
    wake_up_alarm_yes = st.checkbox("YES", key="yes_checkbox", label_visibility="visible")
    
with col2:
    wake_up_alarm_no = st.checkbox("NO", key="no_checkbox", label_visibility="visible")

# Regardless of YES or NO, register the start time
if wake_up_alarm_yes or wake_up_alarm_no:
    if st.session_state['session_start_time'] is None:
        st.session_state['session_start_time'] = datetime.now(colombia_tz)
        st.write(f"Session started at: {st.session_state['session_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Disable the checkboxes after the selection to avoid re-triggering
    st.checkbox("YES", value=False, disabled=True, key="yes_checkbox_disabled")  # Add unique key here
    st.checkbox("NO", value=False, disabled=True, key="no_checkbox_disabled")  # Add unique key here

# Tab 2: Item selection with checkboxes
st.subheader("### Step 2: Select the items you took:")
st.write("Now, please select the items you took. They will be logged with their start time.")

# Show the current item to be selected
if st.session_state['current_item'] < len(items):
    current_item = items[st.session_state['current_item']]
    if st.checkbox(current_item, key=current_item):
        current_time = datetime.now(colombia_tz)
        st.session_state['data'] = st.session_state['data'].append({"item": current_item, "start_time": current_time, "end_time": None}, ignore_index=True)
        st.write(f"{current_item} selected at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Move to the next item
        st.session_state['current_item'] += 1

# Register the end time (when the last item is selected)
if st.session_state['current_item'] == len(items):  # When all items have been selected
    end_time = datetime.now(colombia_tz)
    st.session_state['data']['end_time'] = end_time
    st.write(f"Session ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save to MongoDB
    save_data_to_mongo(st.session_state['data'])

    # Calculate total duration
    duration = (end_time - st.session_state['session_start_time']).seconds
    st.write(f"Total duration: {duration} seconds")

# Display the log in the second tab
st.subheader("### Item Selection Log")
st.write(st.session_state['data'])

# Graph: Number of sessions per day and duration per session
# If there is data, show the graph
if not st.session_state['data'].empty:
    # Convert to pandas DataFrame for graphs
    session_times = pd.to_datetime(st.session_state['data']['start_time'])
    session_days = session_times.dt.date
    session_durations = (pd.to_datetime(st.session_state['data']['end_time']) - session_times).dt.total_seconds()

    # Show the sessions per day graph using Plotly
    daily_sessions = session_days.value_counts().sort_index()
    fig_sessions = px.bar(x=daily_sessions.index.astype(str), y=daily_sessions.values, labels={'x': 'Date', 'y': 'Number of Sessions'},
                          title="Sessions per Day")

    # Show the session duration per day graph using Plotly
    fig_duration = px.bar(x=session_days.astype(str), y=session_durations, labels={'x': 'Date', 'y': 'Duration (seconds)'},
                          title="Session Duration per Day")

    st.plotly_chart(fig_sessions)
    st.plotly_chart(fig_duration)

# Function to save data to MongoDB
def save_data_to_mongo(data):
    for index, row in data.iterrows():
        collection.insert_one(row.to_dict())
