import streamlit as st
import pandas as pd
from datetime import datetime
import pymongo
import pytz

# Conexión a MongoDB Atlas
client = pymongo.MongoClient("mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["morning_routine"]
collection = db["routines"]

# Configuración de la zona horaria
colombia_tz = pytz.timezone('America/Bogota')  # Hora de Colombia

# Función para obtener los registros previos
def get_previous_logs():
    logs = collection.find().sort("start_time", pymongo.ASCENDING)
    return list(logs)

# Pestañas
tab1, tab2 = st.tabs(["Routine", "Previous Logs"])

# Pestaña 1: Routine
with tab1:
    # Step 1: Wake up with alarm question
    if "woke_up" not in st.session_state:
        st.session_state["woke_up"] = None

    woke_up_checkbox = st.checkbox("Did you wake up with the alarm?", key="woke_up")

    # Registra si se levantó con la alarma
    if woke_up_checkbox:
        st.session_state["woke_up_text"] = "YES"
    else:
        st.session_state["woke_up_text"] = "NO"

    if st.session_state.get("woke_up_text"):
        st.write(f"Your selection: {st.session_state['woke_up_text']}")

    # Step 2: Mostrar los ítems para seleccionar
    items = [
        "Small chair/bench", "Construction bucket", "Cloths for cleaning windows",
        "Rolled-up bag", "Soaps", "Shampoo", "Conditioner", "Hair collecting sponge",
        "Glass cleaner", "Comb", "Shaving razor"
    ]

    item_times = {}
    start_time = None

    # Mostrar los ítems en orden
    for item in items:
        if st.checkbox(item, key=item):
            # Si se marca el ítem, registrar la hora
            if not start_time:
                start_time = datetime.now(colombia_tz)  # Guardar la hora de inicio al marcar el primer ítem

            item_times[item] = datetime.now(colombia_tz)  # Guardar la hora de cada ítem seleccionado

    # Al finalizar la selección de ítems, calcular el total de tiempo
    if item_times:
        # La hora de finalización es la del último ítem seleccionado
        end_time = list(item_times.values())[-1]

        # Calcular el tiempo total en minutos
        total_time = (end_time - start_time).total_seconds() / 60

        # Registrar los datos en MongoDB
        collection.insert_one({
            "Woke up with alarm": st.session_state["woke_up_text"],
            "Start hour": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "End hour": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Total time (minutes)": total_time,
            **{item: item_times[item].strftime("%Y-%m-%d %H:%M:%S") for item in item_times}  # Guardar la hora de cada ítem
        })

        st.write(f"Total time: {total_time:.2f} minutes.")
        st.write("Session complete. Your routine has been logged.")

# Pestaña 2: Previous Logs
with tab2:
    # Mostrar los registros previos
    logs = get_previous_logs()
    if logs:
        st.write("Previous Logs:")
        log_data = []
        for log in logs:
            log_data.append({
                "Woke up with alarm": log["Woke up with alarm"],
                "Start hour": log["Start hour"],
                "End hour": log["End hour"],
                "Total time": log["Total time (minutes)"]
            })
        df_logs = pd.DataFrame(log_data)
        st.dataframe(df_logs)
    else:
        st.write("No previous logs found.")
