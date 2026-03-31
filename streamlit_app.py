import streamlit as st
import google.generativeai as genai
import datetime
import json
import pandas as pd

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="AI Habit System", layout="centered")

# -------------------------
# 🎨 ESTILO RESPONSIVE (ARREGLADO)
# -------------------------
st.markdown("""
<style>

/* FONDO */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0e1117, #111827);
    color: white;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #0e1117;
}

/* TARJETAS (SIN ANIMACIONES QUE ROMPEN MÓVIL) */
.card {
    background: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
}

/* MÉTRICAS */
.metric {
    text-align: center;
    padding: 10px;
    border-radius: 10px;
    background: #1c1f26;
    font-size: 16px;
}

/* TEXTO */
h1, h2, h3, h4, h5, h6, p, span, div {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# 🔐 API
# -------------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

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
# CONSECUENCIAS
# -------------------------
def evaluar_consecuencia(score, media, racha, modo):
    if modo == "Suave":
        return "info", "Sigue mejorando poco a poco."
    elif modo == "Estándar":
        if score < media:
            return "warning", "Estás por debajo de tu media."
        else:
            return "info", "Mantén el foco."
    else:
        if score < 5:
            return "error", "CASTIGO: elimina distracciones mañana."
        elif score >= 8:
            return "success", "RECOMPENSA: 1h de ocio."
        else:
            return "warning", "Podrías hacerlo mejor."

# -------------------------
# IA
# -------------------------
def analizar(diario):
    historial = obtener_historial()

    prompt = f"""
Analiza este día y devuelve JSON:

HISTORIAL:
{historial}

HOY:
{diario}

{{
 "productividad_nivel": número 1-10,
 "error_principal": texto,
 "accion_obligatoria_manana": texto,
 "objetivo_manana": texto,
 "analisis_semanal": texto,
 "identidad_actual": texto,
 "regla_clave": texto
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

modo = st.selectbox("🎛️ Modo", ["Suave", "Estándar", "Hardcore"])

diario = st.text_area("✍️ Describe tu día")

if st.button("🚀 Analizar"):

    if diario:
        resultado = analizar(diario)
        fecha = datetime.date.today().isoformat()
        guardar_log(fecha, resultado)

        score = resultado.get("productividad_nivel", 0)
        racha = calcular_racha()
        media = media_ultimos_dias()

        tipo, mensaje = evaluar_consecuencia(score, media, racha, modo)

        # MÉTRICAS (SOLO 2 COLUMNAS → MOBILE SAFE)
        col1, col2 = st.columns(2)
        col1.markdown(f'<div class="metric">🔥 Score<br><b>{score}</b></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric">⚡ Racha<br><b>{racha}</b></div>', unsafe_allow_html=True)

        st.divider()

        # TARJETAS
        st.markdown(f'<div class="card">⚠️ <b>Error:</b><br>{resultado.get("error_principal")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">📜 <b>Regla:</b><br>{resultado.get("regla_clave")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">✅ <b>Acción:</b><br>{resultado.get("accion_obligatoria_manana")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">🎯 <b>Objetivo:</b><br>{resultado.get("objetivo_manana")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">🧬 <b>Identidad:</b><br>{resultado.get("identidad_actual")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">📉 <b>Evaluación semanal:</b><br>{resultado.get("analisis_semanal")}</div>', unsafe_allow_html=True)

        # CONSECUENCIA
        if tipo == "error":
            st.error(mensaje)
        elif tipo == "warning":
            st.warning(mensaje)
        elif tipo == "success":
            st.success(mensaje)
        else:
            st.info(mensaje)

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
