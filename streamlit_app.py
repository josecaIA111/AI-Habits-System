import streamlit as st
import datetime
import json
import requests

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="AI Habit System", layout="wide")

# -------------------------
# ESTILO PRO
# -------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
.card {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
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

# -------------------------
# IA
# -------------------------
def analizar(diario, objetivo, modo):

    tono = {
        "Suave": "amable y motivador",
        "Estándar": "directo y útil",
        "Disciplina avanzada": "duro, exigente y sin excusas"
    }

    prompt = f"""
Eres un coach de alto rendimiento {tono[modo]}.

Tu trabajo es analizar el día del usuario en función de SU OBJETIVO.

OBJETIVO DEL USUARIO:
{objetivo}

DÍA DEL USUARIO:
{diario}

REGLAS IMPORTANTES:
- PROHIBIDO dar consejos genéricos.
- TODO debe basarse en cosas concretas que el usuario ha escrito.
- Debes evaluar el día en función del objetivo del usuario.
- Si el usuario menciona acciones (entrenar, trabajar, dormir, comer, etc.), debes referirte a ellas directamente.
- Si el día es bueno y alineado con su objetivo, debes reconocerlo claramente.
- Si el día es malo o mejorable, debes señalar errores concretos.
- NO inventes fallos.
- NO critiques si no hay errores claros.
- Las recomendaciones deben ayudar directamente a su objetivo.
- Sé claro, específico y útil.

Responde en JSON válido con este formato:

{{
 "productividad_nivel": 1-10,
 "error_principal": "explica el error o 'ningún error relevante'",
 "accion_obligatoria_manana": "acción concreta basada en el día",
 "objetivo_manana": "objetivo claro y medible",
 "analisis_semanal": "patrones o 'aún no hay suficientes datos'",
 "identidad_actual": "definición basada en comportamiento real",
 "regla_clave": "regla práctica basada en su caso"
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=15)

        if response.status_code != 200:
            return {"error_principal": f"Error API: {response.text}"}

        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        return {
            "productividad_nivel": 5,
            "error_principal": f"Error: {e}",
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

objetivo = st.text_input("🎯 ¿Cuál es tu objetivo?")
modo = st.selectbox("⚡ Modo de análisis", ["Suave", "Estándar", "Disciplina avanzada"])
diario = st.text_area("✍️ Describe tu día")

if st.button("🚀 Analizar día"):

    with st.spinner("Analizando..."):

        if diario and objetivo:

            resultado = analizar(diario, objetivo, modo)
            fecha = datetime.date.today().isoformat()
            guardar_log(fecha, resultado)

            st.markdown(f'<div class="card">🔥 Score: {resultado.get("productividad_nivel")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">⚠️ Error: {resultado.get("error_principal")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">📜 Regla: {resultado.get("regla_clave")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">✅ Acción: {resultado.get("accion_obligatoria_manana")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">🎯 Objetivo: {resultado.get("objetivo_manana")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">🧬 Identidad: {resultado.get("identidad_actual")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">📉 Análisis: {resultado.get("analisis_semanal")}</div>', unsafe_allow_html=True)

# -------------------------
# HISTORIAL
# -------------------------
if st.checkbox("📂 Ver historial"):
    st.json(obtener_historial())
