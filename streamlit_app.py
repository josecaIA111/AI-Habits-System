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

/* TITULO */
h1 {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
}

/* SUBTITULO */
.subtitle {
    text-align: center;
    font-size: 18px;
    opacity: 0.7;
    margin-bottom: 20px;
}

/* TARJETAS */
.card {
    background: #111827;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
}

/* MÉTRICAS */
.metric {
    background: #020617;
    padding: 25px;
    border-radius: 14px;
    text-align: center;
    font-size: 18px;
}

/* BOTÓN */
button {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: white !important;
    border-radius: 12px !important;
    height: 45px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# API
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
# IA (MEJORADA)
# -------------------------
def analizar(diario, modo):

    tono = {
        "Suave": "amable y motivador",
        "Estándar": "directo y útil",
        "Disciplina avanzada": "duro, exigente y sin excusas"
    }

    prompt = f"""
Eres un coach de alto rendimiento, {tono[modo]}.

Responde SOLO en JSON válido.

Formato:

{{
 "productividad_nivel": 1-10,
 "error_principal": "texto claro",
 "accion_obligatoria_manana": "acción concreta",
 "objetivo_manana": "objetivo claro",
 "analisis_semanal": "patrones",
 "identidad_actual": "quién está siendo",
 "regla_clave": "regla simple"
}}

Día del usuario:
{diario}
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
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    except Exception as e:
        return {
            "productividad_nivel": 5,
            "error_principal": "No estás siendo consistente",
            "accion_obligatoria_manana": "Haz lo importante sin pensar",
            "objetivo_manana": "Cumplir sin excusas",
            "analisis_semanal": text if 'text' in locals() else "",
            "identidad_actual": "Alguien con potencial pero sin ejecutar",
            "regla_clave": "Primero ejecuta, luego piensa"
        }

# -------------------------
# UI
# -------------------------
st.title("🧠 AI Habit System")
st.markdown('<div class="subtitle">Disciplina diaria. Feedback real. Sin excusas.</div>', unsafe_allow_html=True)

modo = st.selectbox("🎛️ Modo de entrenamiento", ["Suave", "Estándar", "Disciplina avanzada"])

diario = st.text_area("✍️ Describe tu día")

if st.button("🚀 Analizar día"):

    if diario:
        resultado = analizar(diario, modo)
        fecha = datetime.date.today().isoformat()
        guardar_log(fecha, resultado)

        score = resultado.get("productividad_nivel", 0)
        racha = calcular_racha()

        col1, col2 = st.columns(2)
        col1.markdown(f'<div class="metric">🔥 Score<br><b>{score}</b></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric">⚡ Racha<br><b>{racha}</b></div>', unsafe_allow_html=True)

        st.divider()

        st.markdown(f'<div class="card">⚠️ <b>Error principal</b><br>{resultado.get("error_principal")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">📜 <b>Regla clave</b><br>{resultado.get("regla_clave")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">✅ <b>Acción obligatoria</b><br>{resultado.get("accion_obligatoria_manana")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">🎯 <b>Objetivo mañana</b><br>{resultado.get("objetivo_manana")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">🧬 <b>Identidad actual</b><br>{resultado.get("identidad_actual")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">📉 <b>Análisis</b><br>{resultado.get("analisis_semanal")}</div>', unsafe_allow_html=True)

# -------------------------
# PROGRESO
# -------------------------
if st.checkbox("📈 Ver progreso"):
    data = obtener_historial()
    if data:
        df = pd.DataFrame(data).T
        st.line_chart(df["productividad_nivel"])

if st.checkbox("📂 Ver historial"):
    st.json(obtener_historial())
