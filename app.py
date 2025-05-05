import streamlit as st
from datetime import datetime
import pytz
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# MongoDB Atlas connection
mongo_uri = st.secrets["MONGO_URI"]  # Keep using your env variable
client = MongoClient(mongo_uri)
db = client["shower_tracker"]
collection = db["alarm"]

# Timezone
tz = pytz.timezone("America/Bogota")

# Streamlit layout
st.set_page_config(page_title="Shower Tracker", layout="centered")

# Tabs
tab1, tab2 = st.tabs(["📋 Record actions", "📊 View log & analysis"])

# TAB 1 – Record actions
with tab1:
    st.title("Did you get up with your alarm?")
    if "alarm_response" not in st.session_state:
        st.session_state.alarm_response = None

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.alarm_response is None:
            if st.button("✅ YES"):
                time_now = datetime.now(tz)
                doc = {"Index": 1, "Alarm": "YES", "Timestamp": time_now}
                collection.insert_one(doc)
                st.session_state.alarm_response = "YES"
                st.success("You confirmed: YES")

    with col2:
        if st.session_state.alarm_response is None:
            if st.button("❌ NO"):
                time_now = datetime.now(tz)
                doc = {"Index": 1, "Alarm": "NO", "Timestamp": time_now}
                collection.insert_one(doc)
                st.session_state.alarm_response = "NO"
                st.warning("You confirmed: NO")

    # Checkboxes for actions
    st.subheader("Shower Routine Items")
    actions = [
        "Small chair/bench", "Construction bucket", "Cloths for cleaning windows",
        "Rolled-up bag", "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge",
        "Glass cleaner", "Comb", "Shaving razor"
    ]

    for action in actions:
        if st.checkbox(action, key=action):
            time_now = datetime.now(tz)
            collection.update_one(
                {"Index": 1},
                {"$set": {action: time_now.strftime("%Y-%m-%d %H:%M:%S")}},
                upsert=True
            )

# TAB 2 – Data & Visualization
with tab2:
    st.title("Tracked Actions Overview")

    records = list(collection.find())
    if not records:
        st.info("No data found.")
    else:
        df = pd.DataFrame(records).drop(columns=["_id"])
        df.sort_values("Timestamp", inplace=True)
        st.subheader("Log Table")
        st.dataframe(df)

        # Heatmap (if time columns are available)
        st.subheader("Action Timeline (minutes after alarm)")
        if "Alarm" in df.columns:
            df_time = df.copy()
            base_time = pd.to_datetime(df_time["Timestamp"].min())
            time_deltas = []

            for col in actions:
                if col in df_time.columns:
                    df_time[col] = pd.to_datetime(df_time[col], errors="coerce")
                    delta = (df_time[col] - base_time).dt.total_seconds() / 60
                    time_deltas.append((col, delta.values[0] if not pd.isna(delta.values[0]) else None))

            plot_df = pd.DataFrame(time_deltas, columns=["Action", "Minutes After Alarm"]).dropna()
            fig, ax = plt.subplots()
            sns.barplot(data=plot_df, x="Minutes After Alarm", y="Action", ax=ax, palette="Blues_d")
            ax.set_title("Time Taken for Each Shower Item")
            st.pyplot(fig)
