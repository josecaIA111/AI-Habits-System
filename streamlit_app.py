import streamlit as st
import datetime
import json
import pandas as pd
import requests

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="AI Habit System", layout="wide")

# -------------------------
# 🎨 DISEÑO PRO
# -------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
h1 { text-align: center; font-size: 42px; }
.card {
    background: #111827;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 15px;
}
.metric {
    background: #020617;
    padding: 25px;
    border-radius: 14px;
    text-align: center;
}
textarea {
    background-color: #020617 !important;
    color: white !important;
}
button {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# API KEY
# -------------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY")

# -------------------------
# HISTORIAL
# -------------------------
HISTORY_FILE = "habitos_log.json"

def obtener_historial():
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def guardar_log(fecha, datos):
    logs = obtener_historial()
    logs[fecha] = datos
    with open(HISTORY_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def calcular_racha():
    data = obtener_historial()
    fechas = sorted(data.keys(), reverse=True)
    racha = 0
    for fecha in fechas:
        if data[fecha].get("productividad_nivel", 0) >= 7:
            racha += 1
        else:
            break
    return racha

# -------------------------
# IA (REST API)
# -------------------------
def analizar(diario):

    prompt = f"""
Eres un coach de alto rendimiento.

Analiza el día:

{diario}

Devuelve JSON:

{{
 "productividad_nivel": número 1-10,
 "error_principal": directo,
 "accion_obligatoria_manana": concreta,
 "objetivo_manana": claro,
 "analisis_semanal": patrones,
 "identidad_actual": comportamiento actual,
 "regla_clave": regla simple
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, json=payload)

    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except:
        return {
            "productividad_nivel": 5,
            "error_principal": "Error interpretando respuesta",
            "accion_obligatoria_manana": "Reintentar",
            "objetivo_manana": "Ser consistente",
            "analisis_semanal": "",
            "identidad_actual": "",
            "regla_clave": ""
        }

# -------------------------
# UI
# -------------------------
st.title("🧠 AI Habit System")
st.write("Analiza tu día. Mejora tu disciplina.")

diario = st.text_area("Describe tu día")

if st.button("Analizar"):

    if diario:
        resultado = analizar(diario)
        fecha = datetime.date.today().isoformat()
        guardar_log(fecha, resultado)

        score = resultado.get("productividad_nivel", 0)
        racha = calcular_racha()

        col1, col2 = st.columns(2)
        col1.metric("Score", score)
        col2.metric("Racha", racha)

        st.write(resultado)

# -------------------------
# EXTRA
# -------------------------
if st.checkbox("Ver historial"):
    st.json(obtener_historial())
