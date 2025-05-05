import streamlit as st
import pandas as pd
from datetime import datetime
import pymongo

# Conexión a MongoDB Atlas
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["log"]

# Configuración de la zona horaria
st.set_page_config(page_title="Morning Routine Tracker", page_icon=":alarm_clock:")

# Función para obtener los registros previos
def get_previous_logs():
    logs = collection.find().sort("start_time", pymongo.ASCENDING)
    return list(logs)

# Mostrar los registros previos
logs = get_previous_logs()
if logs:
    st.write("Previous Logs:")
    log_data = []
    for log in logs:
        log_data.append({
            "Woke up with alarm": log["woke_up_with_alarm"],
            "Start hour": log["start_time"],
            "Item": log["item"],
            "End hour": log["end_time"],
            "Total time": log["total_time"]
        })
    df_logs = pd.DataFrame(log_data)
    st.dataframe(df_logs)

# Step 1: Wake up with alarm question using checkboxes
if "woke_up" not in st.session_state:
    st.session_state["woke_up"] = None

# Checkbox to select if woke up with alarm
woke_up_checkbox = st.checkbox("Did you wake up with the alarm?", key="woke_up")

# Save the selection of YES or NO as text
if woke_up_checkbox:
    st.session_state["woke_up_text"] = "YES"
else:
    st.session_state["woke_up_text"] = "NO"

if st.session_state.get("woke_up_text"):
    st.write(f"Your selection: {st.session_state['woke_up_text']}")

# Step 2: Select the items you took using checkboxes
items = [
    "Small chair/bench", "Construction bucket", "Cloths for cleaning windows",
    "Rolled-up bag", "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge",
    "Glass cleaner", "Comb", "Shaving razor"
]

# Display checkboxes for each item
selected_items = []
for item in items:
    if st.checkbox(item, key=item):
        selected_items.append(item)
        st.session_state[item] = datetime.now()

# Once the last item is selected, the table with logs appears
if len(selected_items) == len(items):
    # Record the session start time
    start_time = datetime.now()
    end_times = []
    total_times = []
    
    # Calculate the end times and total times for each item
    for item in selected_items:
        end_time = datetime.now()  # Placeholder, update with the actual end time
        end_times.append(end_time)
        total_time = (end_time - st.session_state[item]).total_seconds()
        total_times.append(total_time)
    
    # Save the log to MongoDB
    collection.insert_one({
        "woke_up_with_alarm": st.session_state["woke_up_text"],
        "start_time": start_time,
        "item": selected_items,
        "end_time": end_times,
        "total_time": total_times
    })
    
    st.write("Session complete. Your routine has been logged.")
