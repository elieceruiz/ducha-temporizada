import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
import pymongo

# Zona horaria de Colombia
tz = pytz.timezone("America/Bogota")

# Conectar a MongoDB
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["routines"]

st.set_page_config(page_title="Morning Routine Tracker", layout="centered")
st.title("🌅 Morning Routine Tracker")

st.markdown("This app helps you track your morning routine by recording when you start each task.")

# Paso 1: ¿Te levantaste con la alarma?
st.subheader("Step 1: Did you wake up with the alarm?")

if "alarm_answered" not in st.session_state:
    st.session_state.alarm_answered = False
    st.session_state.woke_with_alarm = None

if not st.session_state.alarm_answered:
    col1, col2 = st.columns(2)
    with col1:
        alarm_yes = st.checkbox("YES", key="alarm_yes")
    with col2:
        alarm_no = st.checkbox("NO", key="alarm_no")

    if alarm_yes and not alarm_no:
        st.session_state.woke_with_alarm = "YES"
        st.session_state.alarm_answered = True
    elif alarm_no and not alarm_yes:
        st.session_state.woke_with_alarm = "NO"
        st.session_state.alarm_answered = True
    elif alarm_yes and alarm_no:
        st.warning("Please select only one option.")
else:
    st.info(f"You selected: **{st.session_state.woke_with_alarm}**")

# Paso 2: Selección de ítems
if st.session_state.alarm_answered:
    st.subheader("Step 2: Select the items you took")
    items = [
        "Small chair/bench", "Construction bucket", "Cloths for cleaning windows", "Rolled-up bag",
        "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge", "Glass cleaner", "Comb", "Shaving razor"
    ]

    if "item_logs" not in st.session_state:
        st.session_state.item_logs = {}
        st.session_state.start_time = datetime.now(tz)

    for item in items:
        if item not in st.session_state.item_logs:
            if st.checkbox(item, key=item):
                st.session_state.item_logs[item] = datetime.now(tz)

    # Si todos fueron seleccionados
    if len(st.session_state.item_logs) == len(items):
        st.success("✅ All items selected. Here's your routine log:")

        end_time = datetime.now(tz)
        total_time = end_time - st.session_state.start_time

        data = {
            "Woke up with alarm": st.session_state.woke_with_alarm,
            "Start hour": st.session_state.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "End hour": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Total time (minutes)": round(total_time.total_seconds() / 60, 2),
        }

        for item, timestamp in st.session_state.item_logs.items():
            data[item] = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        df = pd.DataFrame([data])
        st.dataframe(df)

        # Guardar en MongoDB
        collection.insert_one(data)
