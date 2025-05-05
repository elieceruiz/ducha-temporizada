import streamlit as st
import pymongo
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from bson import ObjectId

# MongoDB Atlas URI
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB Atlas
client = pymongo.MongoClient(mongo_uri)
db = client['shower_tracker']
collection = db['alarm']

# Timezone settings for local time
timezone = pytz.timezone('America/Bogota')

# Helper function to save data
def save_to_mongo(data):
    collection.insert_one(data)

# Streamlit UI
st.title("Shower Tracker")

# Alarm check
alarm = st.radio("Did you wake up with your alarm?", ["YES", "NO"])

if alarm == "YES":
    alarm_time = datetime.now(timezone)
    st.write(f"Alarm time: {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    alarm_time = None

# Tracking items
tracked_items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", 
    "Rolled-up bag", "Shampoo", "Conditioner", "Hair collecting sponge", 
    "Glass cleaner", "Comb", "Shaving razor", "Soaps"
]

# Save times for items selected
item_times = {}

for item in tracked_items:
    if st.checkbox(item):
        item_times[item] = datetime.now(timezone)
        st.write(f"Time for {item}: {item_times[item].strftime('%Y-%m-%d %H:%M:%S')}")

# Save button
if st.button("Save all data"):
    data = {
        "alarm": alarm,
        "alarm_time": alarm_time,
        "items": item_times
    }
    save_to_mongo(data)
    st.success("Data saved to MongoDB!")

# Data display - show table and analysis
st.subheader("Records")

# Fetch data from MongoDB
records = list(collection.find())

# Convert to DataFrame
df = pd.DataFrame(records)

# Clean up DataFrame for display
if not df.empty:
    df['alarm_time'] = pd.to_datetime(df['alarm_time'], errors='coerce')
    df['items'] = df['items'].apply(lambda x: ', '.join(x.keys()) if isinstance(x, dict) else "")

    # Display the table of records
    st.write(df)

    # Analysis: Count of daily executions and total time from alarm to last check
    df['date'] = df['alarm_time'].dt.date
    daily_counts = df.groupby('date').size()
    total_time = df['alarm_time'].apply(lambda x: (datetime.now(timezone) - x).total_seconds())

    st.subheader("Daily Execution Analysis")

    # Plot daily counts of executions
    plt.figure(figsize=(10, 6))
    sns.countplot(x='date', data=df)
    plt.xticks(rotation=45)
    plt.title("Daily Executions")
    st.pyplot(plt)

    # Plot total time from alarm to last check
    plt.figure(figsize=(10, 6))
    sns.histplot(total_time, bins=10, kde=True)
    plt.title("Time from Alarm to Last Check")
    st.pyplot(plt)

else:
    st.write("No records available.")
