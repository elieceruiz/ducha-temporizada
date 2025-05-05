import streamlit as st
from datetime import datetime
import pytz
from pymongo import MongoClient
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Tab for viewing records and chart
tab1, tab2 = st.tabs(["View Records", "View Chart"])

# View Records Tab
with tab1:
    st.header("Recorded Responses")
    # Fetch data from MongoDB
    records = collection.find()
    df = pd.DataFrame(records)
    # Drop MongoDB-specific columns
    df = df.drop(columns=["_id"])
    
    # Show the records in a table
    st.dataframe(df)

# View Chart Tab
with tab2:
    st.header("Responses Chart")
    # Fetch data from MongoDB
    records = collection.find()
    df = pd.DataFrame(records)
    # Drop MongoDB-specific columns
    df = df.drop(columns=["_id"])
    
    # Count the answers
    answer_counts = df["Answer"].value_counts()
    
    # Plot a bar chart
    fig, ax = plt.subplots()
    sns.barplot(x=answer_counts.index, y=answer_counts.values, ax=ax)
    ax.set_title("Number of YES and NO Responses")
    ax.set_xlabel("Response")
    ax.set_ylabel("Count")
    st.pyplot(fig)
