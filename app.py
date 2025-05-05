import streamlit as st
from datetime import datetime
import pymongo
import pytz
import pandas as pd

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["routines"]

# Timezone
tz = pytz.timezone("America/Bogota")

# App UI
st.set_page_config(page_title="Morning Routine", layout="centered")

tab1, tab2 = st.tabs(["☀️ Morning Routine", "📊 Records"])

# ------------------- TAB 1: Main Routine Tracker ----------------------
with tab1:
    st.header("🧼 Morning Routine Tracker")
    st.subheader("Did you wake up with the alarm?")

    routine_items = [
        "Small chair/bench", "Construction bucket", "Cloths for cleaning windows",
        "Rolled-up bag", "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge",
        "Glass cleaner", "Comb", "Shaving razor"
    ]

    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "timestamps" not in st.session_state:
        st.session_state.timestamps = {}
    if "woke_up" not in st.session_state:
        st.session_state.woke_up = None

    if st.session_state.woke_up is None:
        col1, col2 = st.columns(2)
        with col1:
            if st.checkbox("YES", key="yes_alarm"):
                st.session_state.woke_up = "YES"
                st.session_state.start_time = datetime.now(tz)
                st.rerun()
        with col2:
            if st.checkbox("NO", key="no_alarm"):
                st.session_state.woke_up = "NO"
                st.session_state.start_time = datetime.now(tz)
                st.rerun()
    else:
        st.markdown(f"**Woke up with alarm?** `{st.session_state.woke_up}`")
        st.markdown(f"**Start time:** `{st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S')}`")

        if st.session_state.current_index < len(routine_items):
            item = routine_items[st.session_state.current_index]
            if st.checkbox(item, key=item):
                st.session_state.timestamps[item] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.current_index += 1
                st.rerun()
        else:
            end_time = datetime.now(tz)
            total_time = round((end_time - st.session_state.start_time).total_seconds() / 60, 2)

            result = {
                "Woke up with alarm": st.session_state.woke_up,
                "Start hour": st.session_state.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "End hour": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Total time (minutes)": total_time,
            }
            result.update(st.session_state.timestamps)
            collection.insert_one(result)

            st.success("Routine saved successfully!")

            # Asegurarse de que todos los valores en "Value" sean cadenas para evitar el error
            result_str = {key: str(value) for key, value in result.items()}
            st.write(pd.DataFrame.from_dict(result_str, orient='index', columns=["Value"]))

            # Reset session state
            for key in ["start_time", "current_index", "timestamps", "woke_up", "yes_alarm", "no_alarm"]:
                st.session_state.pop(key, None)

# ---------------------- TAB 2: View Records --------------------------
with tab2:
    st.header("📊 Previous Records")
    records = list(collection.find())

    if records:
        for record in records:
            record.pop("_id", None)  # remove MongoDB id field
        df = pd.DataFrame(records)
        
        # Asegurarse de que todos los valores sean cadenas para evitar el error con Arrow
        df = df.applymap(str)
        
        df.index = [f"Record {i+1}" for i in range(len(df))]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found yet.")
