import streamlit as st
import pandas as pd
from datetime import datetime
import pymongo

# Conexión a MongoDB Atlas
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["routines"]

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
            "Woke up with alarm": log["Woke up with alarm"],
            "Start hour": log["Start hour"],
            "Item": log["Small chair/bench"],  # Muestra un ítem de ejemplo
            "End hour": log["End hour"],
            "Total time": log["Total time (minutes)"]
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

# Initialize a dictionary to store the start and end times for each item
item_times = {}

# Display checkboxes for each item
for item in items:
    if st.checkbox(item, key=item):
        if item not in item_times:
            item_times[item] = {"start": datetime.now()}
        st.session_state[item] = item_times[item]["start"]  # Record start time as the current time

# When all items are selected, calculate end times and total times
if len(item_times) == len(items):
    # Record the session start time
    start_time = datetime.now()
    end_times = []
    total_times = []
    
    # Calculate the end times and total times for each item
    for item, times in item_times.items():
        end_time = datetime.now()  # Placeholder, update with the actual end time
        times["end"] = end_time
        end_times.append(end_time)
        total_time = (end_time - times["start"]).total_seconds() / 60  # Convert to minutes
        total_times.append(total_time)
    
    # Save the log to MongoDB in the "routines" collection
    collection.insert_one({
        "Woke up with alarm": st.session_state["woke_up_text"],
        "Start hour": start_time,
        "End hour": end_times,
        "Total time (minutes)": total_times,
        **{item: times["end"].strftime("%Y-%m-%d %H:%M:%S") for item, times in item_times.items()}  # Store end time for each item
    })
    
    st.write("Session complete. Your routine has been logged.")
