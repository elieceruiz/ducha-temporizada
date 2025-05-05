import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import pytz
import matplotlib.pyplot as plt

# MongoDB connection
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(mongo_uri)
db = client.get_database("shower_tracker")
sessions_collection = db.sessions

# Item list
items = ["Small chair", "Construction bucket", "Window cleaning cloths", "Rolled-up bag", 
         "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", 
         "Shaving razor", "Soaps"]

# Register session in MongoDB
def log_session_to_mongo(start_time, end_time, item_times):
    session_data = {
        "session_start_time": start_time,
        "session_end_time": end_time,
        "session_duration": (end_time - start_time).total_seconds(),
        "items": item_times
    }
    sessions_collection.insert_one(session_data)

# Main app
def main():
    st.set_page_config(page_title="Wake Routine Tracker", layout="wide")
    st.title("⏰ Wake Routine Tracker")

    tab1, tab2 = st.tabs(["📋 Record Session", "📊 View Data"])

    with tab1:
        st.subheader("Did you wake up with the alarm?")
        woke_up_yes = st.checkbox("YES")
        woke_up_no = st.checkbox("NO")

        if woke_up_yes and woke_up_no:
            st.warning("Please select only one: YES or NO.")
            st.stop()

        if woke_up_yes or woke_up_no:
            session_start = datetime.now(pytz.timezone("America/Bogota"))
            st.success("Session started. Now check each item as you go.")

            item_times = {}
            for i, item in enumerate(items):
                label = f"{i + 1}. {item}"
                if i == 0 or items[i - 1] in item_times:
                    if st.checkbox(label, key=item):
                        item_times[item] = datetime.now(pytz.timezone("America/Bogota"))
                        st.info(f"✔️ Marked at {item_times[item].strftime('%H:%M:%S')}")

            if len(item_times) == len(items):
                session_end = datetime.now(pytz.timezone("America/Bogota"))
                log_session_to_mongo(session_start, session_end, item_times)
                duration_min = (session_end - session_start).total_seconds() / 60
                st.success(f"✅ Session complete. Total time: {duration_min:.2f} minutes.")

    with tab2:
        st.subheader("📊 Session Summary and Chart")

        data = list(sessions_collection.find())
        if not data:
            st.info("No sessions found.")
            return

        df = pd.DataFrame(data)
        df['session_start_time'] = pd.to_datetime(df['session_start_time'])
        df['session_end_time'] = pd.to_datetime(df['session_end_time'])
        df['session_duration_min'] = df['session_duration'] / 60

        st.write("### Table of Sessions")
        st.dataframe(df[["session_start_time", "session_end_time", "session_duration_min"]])

        st.write("### Duration per Session (minutes)")
        plt.figure(figsize=(10, 5))
        plt.bar(df.index + 1, df['session_duration_min'], color='teal')
        plt.xlabel("Session Number")
        plt.ylabel("Duration (minutes)")
        plt.title("Total Time per Wake Routine Session")
        st.pyplot(plt)

if __name__ == "__main__":
    main()
