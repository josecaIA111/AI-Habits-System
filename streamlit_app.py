import streamlit as st
import google.generativeai as genai
import datetime
import json
import pandas as pd

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="AI Habit System", layout="wide")

# -------------------------
# 🎨 DISEÑO PRO (VISUAL TOP)
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
    box-shadow: 0 0 15px rgba(0,0,0,0.4);
}

/* TEXTAREA */
textarea {
    background-color: #020617 !important;
    color: white !important;
    border-radius: 10px !important;
}

/* BOTÓN */
button {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: white !important;
    border-radius: 12px !important;
    height: 45px;
    font-size: 16px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# API
# -------------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# ✅ MODELO ARREGLADO
model = genai.GenerativeModel('gemini-1.5-flash-latest')

HISTORY_FILE = "habitos_log.json"

# -------------------------
# FUNCIONES
# -------------------------
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

def media_ultimos_dias(n=7):
    data = obtener_historial()
    valores = list(data.values())[-n:]
    if not valores:
        return 0
    scores = [v.get("productividad_nivel", 0) for v in valores]
    return sum(scores) / len(scores)

# -------------------------
# IA
# -------------------------
def analizar(diario):
    historial = obtener_historial()

    prompt = f"""
Eres un coach de alto rendimiento, directo y claro.

Analiza el día del usuario:

HISTORIAL:
{historial}

HOY:
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

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    return json.loads(response.text)

# -------------------------
# UI
# -------------------------
st.title("🧠 AI Habit System")
st.markdown('<div class="subtitle">Analiza tu día. Mejora tu disciplina. Construye consistencia.</div>', unsafe_allow_html=True)

modo = st.selectbox("🎛️ Modo", ["Suave", "Estándar", "Disciplina avanzada"])

diario = st.text_area("✍️ Describe tu día")

if st.button("🚀 Analizar día"):

    if diario:
        resultado = analizar(diario)
        fecha = datetime.date.today().isoformat()
        guardar_log(fecha, resultado)

        score = resultado.get("productividad_nivel", 0)
        racha = calcular_racha()

        col1, col2 = st.columns(2)
        col1.markdown(f'<div class="metric">🔥 Score<br><b>{score}</b></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric">⚡ Racha<br><b>{racha}</b></div>', unsafe_allow_html=True)

        st.divider()

        st.markdown(f'<div class="card">⚠️ <b>Error principal:</b><br>{resultado.get("error_principal")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">📜 <b>Regla clave:</b><br>{resultado.get("regla_clave")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">✅ <b>Acción obligatoria:</b><br>{resultado.get("accion_obligatoria_manana")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">🎯 <b>Objetivo:</b><br>{resultado.get("objetivo_manana")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">🧬 <b>Identidad actual:</b><br>{resultado.get("identidad_actual")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">📉 <b>Análisis:</b><br>{resultado.get("analisis_semanal")}</div>', unsafe_allow_html=True)

# -------------------------
# EXTRA
# -------------------------
if st.checkbox("📈 Ver progreso"):
    data = obtener_historial()
    if data:
        df = pd.DataFrame(data).T
        st.line_chart(df["productividad_nivel"])

if st.checkbox("📂 Ver historial"):
    st.json(obtener_historial())
