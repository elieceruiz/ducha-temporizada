import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
import pymongo

# Timezone for Colombia
colombia_tz = pytz.timezone('America/Bogota')
now_colombia = lambda: datetime.now(colombia_tz)

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["sessions"]

# Items to carry
items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", "Rolled-up bag",
    "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", "Shaving razor"
]

st.title("Morning Routine Tracker")

# Session state
if 'item_states' not in st.session_state:
    st.session_state.item_states = {item: False for item in items}
if 'item_times' not in st.session_state:
    st.session_state.item_times = {}

# Wake-up question
if 'woke_up' not in st.session_state:
    st.session_state.woke_up = None
    st.subheader("Did you wake up with the alarm?")
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("YES", key="wakeup_yes"):
            st.session_state.woke_up = "YES"
    with col2:
        if st.checkbox("no", key="wakeup_no"):
            st.session_state.woke_up = "NO"

# If answered, show selected response
if st.session_state.woke_up:
    st.markdown(f"**You selected:** {st.session_state.woke_up}")
    st.markdown("### Step 2: Confirm the items you carried:")

    # Item checkboxes
    for item in items:
        if not st.session_state.item_states[item]:
            if st.checkbox(item, key=item):
                st.session_state.item_states[item] = True
                st.session_state.item_times[item] = now_colombia()

    # Check if all are selected
    if all(st.session_state.item_states.values()):
        # Prepare DataFrame
        start_time = min(st.session_state.item_times.values())
        end_time = max(st.session_state.item_times.values())
        total_duration = (end_time - start_time).total_seconds() / 60  # in minutes

        data = {
            "Woke up with alarm": st.session_state.woke_up,
            "Start hour": [start_time.strftime("%Y-%m-%d %H:%M:%S")],
            "End hour": [end_time.strftime("%Y-%m-%d %H:%M:%S")],
            "Total time (min)": [round(total_duration, 2)],
        }

        for item in items:
            data[item] = [st.session_state.item_times[item].strftime("%Y-%m-%d %H:%M:%S")]

        df = pd.DataFrame(data)

        st.markdown("## Routine Summary")
        st.dataframe(df)

        # Save to MongoDB
        collection.insert_one(df.to_dict(orient="records")[0])

        st.success("Routine data saved to MongoDB.")
