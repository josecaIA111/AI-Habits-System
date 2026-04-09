"""
AI Habit System — Versión Élite
================================
Stack:   Streamlit + Supabase (Auth + DB) + Gemini 2.0 Flash
Autor:   Generado con criterio de ingeniería senior
Versión: 3.0.0
"""

import streamlit as st
import datetime
import json
import requests
import html
import logging
import re
from typing import Optional
from supabase import create_client, Client
from gotrue.errors import AuthApiError

# ══════════════════════════════════════════════════
# 1. CONFIGURACIÓN GLOBAL
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Habit System",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)
logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MAX_CHARS     = 2000
HISTORIAL_IA  = 7    # días de historial que ve la IA
HISTORIAL_UI  = 30   # días que se muestran en el historial visual
MEDIA_LIMITE  = 30   # registros para calcular la media

# ══════════════════════════════════════════════════
# 2. ESTILOS
# ══════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: #060910;
    color: #e2e8f0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0a0f1a !important;
    border-right: 1px solid #1a2235;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif; }

h1, h2, h3 { font-family: 'Space Mono', monospace; letter-spacing: -0.5px; }

/* ── CARDS ── */
.card {
    background: linear-gradient(135deg, #0f1829 0%, #0d1520 100%);
    border: 1px solid #1e2d45;
    padding: 18px 20px;
    border-radius: 14px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.card:hover { border-color: #2d4a6e; }
.card-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.5px; color: #64748b; margin-bottom: 4px; }
.card-value { font-size: 1rem; color: #e2e8f0; line-height: 1.5; }

.card-green  { border-left: 3px solid #22c55e; }
.card-yellow { border-left: 3px solid #f59e0b; }
.card-red    { border-left: 3px solid #ef4444; }
.card-blue   { border-left: 3px solid #3b82f6; }
.card-purple { border-left: 3px solid #a855f7; }

/* ── SCORE BADGE ── */
.score-badge {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1;
}
.score-high   { color: #22c55e; }
.score-mid    { color: #f59e0b; }
.score-low    { color: #ef4444; }

/* ── STREAK ── */
.streak-box {
    background: linear-gradient(135deg, #1a1000, #0f1800);
    border: 1px solid #f59e0b33;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    margin-bottom: 8px;
}
.streak-num {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #f59e0b;
}

/* ── AUTH ── */
.auth-wrapper {
    max-width: 420px;
    margin: 4rem auto;
}
.auth-header {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.auth-sub {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* ── HISTORIAL ITEM ── */
.hist-item {
    background: #0f1829;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.88rem;
}
.hist-fecha { color: #94a3b8; font-family: 'Space Mono', monospace; font-size: 0.78rem; }
.hist-score { font-family: 'Space Mono', monospace; font-weight: 700; }

/* ── IDENTIDAD ── */
.identidad-badge {
    background: #1e1035;
    border: 1px solid #a855f733;
    border-radius: 99px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #c084fc;
    display: inline-block;
    margin-top: 4px;
}

/* ── DIVIDER ── */
hr { border-color: #1e2d45 !important; }

/* ── BOTONES ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px #2563eb44;
}

/* ── INPUTS ── */
.stTextInput > div > input,
.stTextArea > div > textarea,
.stSelectbox > div > div {
    background: #0f1829 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > input:focus,
.stTextArea > div > textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px #2563eb22 !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #2563eb !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0a0f1a;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748b !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: #1e2d45 !important;
    color: #e2e8f0 !important;
}

/* ── MÉTRICAS ── */
[data-testid="stMetric"] {
    background: #0f1829;
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 14px !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-family: 'Space Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# 3. SECRETS Y CLIENTE SUPABASE
# ══════════════════════════════════════════════════
def _get_secret(key: str) -> Optional[str]:
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return None

GOOGLE_API_KEY   = _get_secret("GOOGLE_API_KEY")
SUPABASE_URL     = _get_secret("SUPABASE_URL")
SUPABASE_API_KEY = _get_secret("SUPABASE_API_KEY")

missing = [k for k, v in {
    "GOOGLE_API_KEY":   GOOGLE_API_KEY,
    "SUPABASE_URL":     SUPABASE_URL,
    "SUPABASE_API_KEY": SUPABASE_API_KEY,
}.items() if not v]

if missing:
    st.error(f"⚠️ Secrets faltantes: **{', '.join(missing)}**  \nConfigúralos en Streamlit Cloud → Settings → Secrets.")
    st.stop()

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_API_KEY)

supabase: Client = get_supabase()

# ══════════════════════════════════════════════════
# 4. CAPA DE AUTENTICACIÓN
# ══════════════════════════════════════════════════
def _auth_error_msg(raw: str) -> str:
    r = raw.lower()
    if "invalid login"        in r: return "❌ Email o contraseña incorrectos."
    if "email not confirmed"  in r: return "📧 Confirma tu email antes de entrar."
    if "already registered"   in r: return "⚠️ Este email ya tiene una cuenta."
    if "password"             in r: return "⚠️ La contraseña debe tener al menos 6 caracteres."
    if "rate limit"           in r: return "⏳ Demasiados intentos. Espera unos minutos."
    return f"Error de autenticación: {raw}"


def auth_login(email: str, password: str) -> tuple[bool, str]:
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            st.session_state.update({
                "user_id": res.user.id,
                "email":   res.user.email,
                "nombre":  (res.user.user_metadata or {}).get("nombre", email.split("@")[0]),
            })
            return True, "Sesión iniciada."
        return False, "No se pudo iniciar sesión."
    except AuthApiError as e:
        return False, _auth_error_msg(str(e))
    except Exception as e:
        logger.error("auth_login: %s", e)
        return False, "Error inesperado. Inténtalo de nuevo."


def auth_register(email: str, password: str, nombre: str) -> tuple[bool, str]:
    try:
        res = supabase.auth.sign_up({
            "email":    email,
            "password": password,
            "options":  {"data": {"nombre": nombre}},
        })
        if res.user:
            return True, "✅ Cuenta creada. Revisa tu email para confirmarla."
        return False, "No se pudo crear la cuenta."
    except AuthApiError as e:
        return False, _auth_error_msg(str(e))
    except Exception as e:
        logger.error("auth_register: %s", e)
        return False, "Error inesperado al registrarse."


def auth_reset_password(email: str) -> tuple[bool, str]:
    try:
        supabase.auth.reset_password_email(email)
        return True, "📧 Email de recuperación enviado."
    except AuthApiError as e:
        return False, _auth_error_msg(str(e))
    except Exception as e:
        logger.error("auth_reset: %s", e)
        return False, "Error al enviar el email."


def auth_logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.clear()


def is_logged_in() -> bool:
    return "user_id" in st.session_state

# ══════════════════════════════════════════════════
# 5. CAPA DE DATOS
# ══════════════════════════════════════════════════
def guardar_log(payload: dict) -> bool:
    try:
        supabase.table("habitos_log").insert(payload).execute()
        return True
    except Exception as e:
        logger.error("guardar_log: %s", e)
        return False


def obtener_historial_ia(usuario_id: str) -> list:
    """Historial compacto para contexto de la IA."""
    try:
        res = (
            supabase.table("habitos_log")
            .select("fecha, productividad_nivel, error_principal, objetivo")
            .eq("usuario_id", usuario_id)
            .order("fecha", desc=True)
            .limit(HISTORIAL_IA)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error("obtener_historial_ia: %s", e)
        return []


def obtener_historial_ui(usuario_id: str) -> list:
    """Historial completo para la vista de usuario."""
    try:
        res = (
            supabase.table("habitos_log")
            .select("fecha, productividad_nivel, error_principal, objetivo, modo, accion_manana, regla_clave, created_at")
            .eq("usuario_id", usuario_id)
            .order("fecha", desc=True)
            .limit(HISTORIAL_UI)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error("obtener_historial_ui: %s", e)
        return []


def obtener_media(usuario_id: str) -> Optional[float]:
    try:
        res = (
            supabase.table("habitos_log")
            .select("productividad_nivel")
            .eq("usuario_id", usuario_id)
            .order("fecha", desc=True)
            .limit(MEDIA_LIMITE)
            .execute()
        )
        niveles = [x["productividad_nivel"] for x in (res.data or []) if x.get("productividad_nivel") is not None]
        return round(sum(niveles) / len(niveles), 1) if niveles else None
    except Exception as e:
        logger.error("obtener_media: %s", e)
        return None


def calcular_racha(historial: list) -> int:
    """Calcula la racha de días consecutivos desde el historial ya cargado."""
    try:
        fechas = sorted(
            {datetime.date.fromisoformat(x["fecha"]) for x in historial if x.get("fecha")},
            reverse=True,
        )
        if not fechas:
            return 0
        hoy = datetime.date.today()
        if fechas[0] < hoy - datetime.timedelta(days=1):
            return 0
        racha = 0
        for i, f in enumerate(fechas):
            if f == fechas[0] - datetime.timedelta(days=i):
                racha += 1
            else:
                break
        return racha
    except Exception as e:
        logger.error("calcular_racha: %s", e)
        return 0


def calcular_identidad(media: Optional[float]) -> str:
    if media is None: return "🌱 Iniciando camino"
    if media >= 8:    return "⚡ Identidad Disciplinada"
    if media >= 5:    return "🔄 En Transformación"
    return "🔍 Buscando Consistencia"


def ya_analizo_hoy(historial: list) -> bool:
    """Devuelve True si el usuario ya tiene un registro de hoy."""
    hoy = datetime.date.today().isoformat()
    return any(x.get("fecha") == hoy for x in historial)


@st.cache_data(ttl=300)
def cargar_estado_usuario(usuario_id: str) -> dict:
    """
    Carga centralizada del estado del usuario.
    Cacheada 5 min. Se invalida explícitamente tras guardar un nuevo log.
    """
    historial_ia  = obtener_historial_ia(usuario_id)
    historial_ui  = obtener_historial_ui(usuario_id)
    media         = obtener_media(usuario_id)
    racha         = calcular_racha(historial_ui)
    identidad     = calcular_identidad(media)
    analizo_hoy   = ya_analizo_hoy(historial_ui)

    return {
        "historial_ia":  historial_ia,
        "historial_ui":  historial_ui,
        "media":         media,
        "racha":         racha,
        "identidad":     identidad,
        "analizo_hoy":   analizo_hoy,
    }

# ══════════════════════════════════════════════════
# 6. MOTOR DE IA
# ══════════════════════════════════════════════════
_TONO = {
    "Suave":               "amable, empático y motivador. Celebra los logros, sugiere mejoras con cariño.",
    "Estándar":            "directo, claro y útil. Equilibrado entre reconocimiento y exigencia.",
    "Disciplina avanzada": "duro, sin excusas y extremadamente exigente. Trata al usuario como un atleta de élite.",
}


def analizar_con_ia(
    diario:    str,
    objetivo:  str,
    modo:      str,
    historial: list,
    racha:     int,
    identidad: str,
) -> dict:
    historial_txt = "\n".join(
        f"  • {h['fecha']}: {h.get('productividad_nivel','?')}/10 — {h.get('error_principal','—')}"
        for h in historial
    ) or "  • Sin historial previo."

    prompt = f"""Eres un coach de alto rendimiento personal. Tu tono: {_TONO.get(modo, _TONO['Estándar'])}

═══ PERFIL DEL USUARIO ═══
Objetivo principal : {objetivo}
Identidad actual   : {identidad}
Racha activa       : {racha} día(s) consecutivo(s)

═══ HISTORIAL RECIENTE ═══
{historial_txt}

═══ ENTRADA DE HOY ═══
{diario}

═══ INSTRUCCIONES ═══
1. Analiza el día EXCLUSIVAMENTE basándote en lo que el usuario ha escrito.
2. Si la racha es alta (≥5), prioriza protegerla en tus recomendaciones.
3. Si la identidad es baja, incrementa la exigencia.
4. NUNCA inventes fallos. Si el día fue bueno, dilo con claridad.
5. La acción de mañana debe ser específica, medible y alcanzable.
6. El análisis de patrones debe basarse en el historial real, no en suposiciones.

Responde ÚNICAMENTE en JSON válido con este esquema exacto:
{{
  "productividad_nivel":         <entero 1-10>,
  "resumen_dia":                 "<1 frase que capture la esencia del día>",
  "error_principal":             "<error concreto o 'Sin errores relevantes hoy'>",
  "logro_principal":             "<logro real del día o 'Sin logros destacados'>",
  "accion_obligatoria_manana":   "<acción específica y medible para mañana>",
  "regla_clave":                 "<principio práctico derivado de este día>",
  "patron_detectado":            "<patrón del historial o 'Insuficientes datos'>",
  "mensaje_coach":               "<mensaje directo y personalizado al usuario>"
}}"""

    url = (
        "https://generativelanguage.googleapis.com/v1/models/"
        f"gemini-1.5-flash-002:generateContent?key={GOOGLE_API_KEY}"
    )

    try:
        r = requests.post(
            url,
            json={
                "contents":        [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
            },
            timeout=25,
        )

        if r.status_code != 200:
            logger.error("Gemini HTTP %s", r.status_code)
            return {"error": f"Error de API ({r.status_code}). Revisa tu clave o cuota de Gemini."}

        data       = r.json()
        candidates = data.get("candidates")
        if not candidates:
            return {"error": "La IA no devolvió candidatos. Inténtalo de nuevo."}

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return {"error": "Respuesta vacía de la IA."}

        parsed = json.loads(parts[0].get("text", "{}"))

        nivel = parsed.get("productividad_nivel")
        if not isinstance(nivel, (int, float)) or not (1 <= nivel <= 10):
            parsed["productividad_nivel"] = 5

        return parsed

    except json.JSONDecodeError:
        return {"error": "La IA devolvió un formato inesperado. Inténtalo de nuevo."}
    except requests.exceptions.Timeout:
        return {"error": "Tiempo de espera agotado (25s). Inténtalo de nuevo."}
    except requests.exceptions.RequestException as e:
        logger.error("analizar_con_ia request: %s", e)
        return {"error": "Error de conexión con la IA."}
    except Exception as e:
        logger.error("analizar_con_ia: %s", e)
        return {"error": "Error inesperado al analizar."}

# ══════════════════════════════════════════════════
# 7. COMPONENTES DE UI
# ══════════════════════════════════════════════════
def _e(v) -> str:
    """Escapa HTML y devuelve '—' si está vacío."""
    return html.escape(str(v)) if v else "—"


def render_card(label: str, value, color: str = "blue", emoji: str = ""):
    color_map = {"green": "card-green", "yellow": "card-yellow",
                 "red": "card-red", "blue": "card-blue", "purple": "card-purple"}
    cls = f"card {color_map.get(color, 'card-blue')}"
    st.markdown(
        f'<div class="{cls}">'
        f'<div class="card-label">{emoji} {label}</div>'
        f'<div class="card-value">{_e(value)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_score(score: int):
    cls = "score-high" if score >= 8 else "score-mid" if score >= 5 else "score-low"
    st.markdown(
        f'<div class="card" style="text-align:center;padding:24px">'
        f'<div class="card-label">SCORE DEL DÍA</div>'
        f'<div class="score-badge {cls}">{score}<span style="font-size:1.5rem">/10</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_historial(registros: list):
    if not registros:
        st.info("Aún no hay registros. ¡Analiza tu primer día!")
        return

    for r in registros:
        nivel = r.get("productividad_nivel")
        fecha = r.get("fecha", "—")
        color = "#22c55e" if (isinstance(nivel, int) and nivel >= 8) else \
                "#f59e0b" if (isinstance(nivel, int) and nivel >= 5) else "#ef4444"
        objetivo_txt = _e(r.get("objetivo", ""))
        error_txt    = _e(r.get("error_principal", ""))
        st.markdown(
            f'<div class="hist-item">'
            f'<div>'
            f'<div class="hist-fecha">📅 {_e(fecha)}</div>'
            f'<div style="color:#94a3b8;font-size:0.82rem;margin-top:2px">🎯 {objetivo_txt}</div>'
            f'<div style="color:#64748b;font-size:0.78rem;margin-top:2px">⚠️ {error_txt}</div>'
            f'</div>'
            f'<div class="hist-score" style="color:{color}">{nivel}/10</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_sidebar(estado: dict):
    with st.sidebar:
        nombre    = _e(st.session_state.get("nombre", "Usuario"))
        email     = _e(st.session_state.get("email", ""))
        racha     = estado["racha"]
        media     = estado["media"]
        identidad = estado["identidad"]

        st.markdown(f"### 👤 {nombre}")
        st.caption(email)
        st.markdown("---")

        # Racha destacada
        st.markdown(
            f'<div class="streak-box">'
            f'<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;color:#92400e;margin-bottom:4px">🔥 Racha activa</div>'
            f'<div class="streak-num">{racha}</div>'
            f'<div style="font-size:0.78rem;color:#92400e">días consecutivos</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Media", f"{media}/10" if media else "N/A")
        with col2:
            total = len(estado["historial_ui"])
            st.metric("📅 Días", total)

        st.markdown(
            f'<div class="identidad-badge">{_e(identidad)}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        if "obj_input" not in st.session_state:
            st.session_state["obj_input"] = "Ser mi mejor versión"

        objetivo = st.text_input(
            "🎯 Objetivo",
            value=st.session_state["obj_input"],
            max_chars=200,
            help="Define tu norte. Sé específico.",
        )
        st.session_state["obj_input"] = objetivo

        modo = st.selectbox(
            "⚡ Tono del coach",
            ["Suave", "Estándar", "Disciplina avanzada"],
            index=1,
        )

        st.markdown("---")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            auth_logout()
            st.rerun()

        return objetivo, modo

# ══════════════════════════════════════════════════
# 8. PANTALLA DE AUTENTICACIÓN
# ══════════════════════════════════════════════════
def render_auth():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-header">🧠 AI Habit System</div>'
        '<div class="auth-sub">Coach de hábitos personal con inteligencia artificial</div>',
        unsafe_allow_html=True,
    )

    tab_login, tab_register, tab_reset = st.tabs(["🔑 Entrar", "✨ Registrarse", "🔓 Recuperar"])

    # ── LOGIN ──
    with tab_login:
        with st.form("f_login"):
            email    = st.text_input("Email",      placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Iniciar sesión", use_container_width=True, type="primary")
        if submit:
            if not email or not password:
                st.warning("Completa todos los campos.")
            else:
                with st.spinner("Verificando..."):
                    ok, msg = auth_login(email.strip(), password)
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

    # ── REGISTRO ──
    with tab_register:
        with st.form("f_register"):
            nombre   = st.text_input("Nombre",              placeholder="Tu nombre")
            email_r  = st.text_input("Email",               placeholder="tu@email.com")
            pass_r   = st.text_input("Contraseña",          type="password", placeholder="Mín. 6 caracteres")
            confirm  = st.text_input("Confirmar contraseña",type="password", placeholder="Repite la contraseña")
            submit_r = st.form_submit_button("Crear cuenta", use_container_width=True, type="primary")
        if submit_r:
            if not all([nombre, email_r, pass_r, confirm]):
                st.warning("Completa todos los campos.")
            elif pass_r != confirm:
                st.error("❌ Las contraseñas no coinciden.")
            elif len(pass_r) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres.")
            else:
                with st.spinner("Creando cuenta..."):
                    ok, msg = auth_register(email_r.strip(), pass_r, nombre.strip())
                (st.success if ok else st.error)(msg)

    # ── RESET ──
    with tab_reset:
        with st.form("f_reset"):
            email_rr = st.text_input("Tu email", placeholder="tu@email.com")
            submit_rr = st.form_submit_button("Enviar recuperación", use_container_width=True, type="primary")
        if submit_rr:
            if not email_rr:
                st.warning("Introduce tu email.")
            else:
                with st.spinner("Enviando..."):
                    ok, msg = auth_reset_password(email_rr.strip())
                (st.success if ok else st.error)(msg)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# 9. APP PRINCIPAL
# ══════════════════════════════════════════════════
def render_app():
    user_id = st.session_state["user_id"]

    # Cargar estado (cacheado por usuario)
    estado = cargar_estado_usuario(user_id)

    # Sidebar — retorna objetivo y modo
    objetivo, modo = render_sidebar(estado)

    # ── HEADER ──
    nombre = _e(st.session_state.get("nombre", ""))
    st.markdown(f"# 🧠 AI Habit System")
    st.markdown(f"Hola, **{nombre}**. Es hora de auditar tu día.")

    if estado["analizo_hoy"]:
        st.info("✅ Ya registraste el análisis de hoy. Puedes registrar otro si lo necesitas.")

    st.markdown("---")

    # ── TABS ──
    tab_analisis, tab_historial = st.tabs(["📝 Análisis del día", "📂 Historial"])

    # ── TAB 1: ANÁLISIS ──
    with tab_analisis:
        _, col_fecha = st.columns([3, 1])
        with col_fecha:
            fecha_sel = st.date_input("Fecha", datetime.date.today(), max_value=datetime.date.today())

        diario = st.text_area(
            "¿Qué ha pasado hoy? Sé honesto y específico.",
            height=160,
            max_chars=MAX_CHARS,
            placeholder="Dormí 7h, trabajé 5h en el proyecto X, entrené 45min. Pero perdí 1h en redes sociales antes de dormir...",
        )
        chars_left = MAX_CHARS - len(diario)
        st.caption(f"{chars_left} caracteres restantes")

        if st.button("🚀 Analizar día", use_container_width=True, type="primary"):
            if not diario.strip():
                st.warning("⚠️ El diario no puede estar vacío.")
            elif not objetivo.strip():
                st.warning("⚠️ Define tu objetivo en el panel lateral.")
            else:
                with st.spinner("Analizando con IA..."):
                    resultado = analizar_con_ia(
                        diario, objetivo, modo,
                        estado["historial_ia"],
                        estado["racha"],
                        estado["identidad"],
                    )

                if "error" in resultado:
                    st.error(_e(resultado["error"]))
                else:
                    # Guardar en BD
                    guardado = guardar_log({
                        "fecha":               fecha_sel.isoformat(),
                        "usuario_id":          user_id,
                        "objetivo":            objetivo,
                        "modo":                modo,
                        "productividad_nivel": resultado.get("productividad_nivel"),
                        "error_principal":     resultado.get("error_principal", ""),
                        "accion_manana":       resultado.get("accion_obligatoria_manana", ""),
                        "regla_clave":         resultado.get("regla_clave", ""),
                    })
                    if not guardado:
                        st.warning("⚠️ Análisis listo, pero hubo un error al guardarlo.")

                    # Invalidar caché de este usuario
                    cargar_estado_usuario.clear()

                    # ── RESULTADOS ──
                    st.markdown("---")
                    st.markdown("### 📊 Resultado")

                    score = resultado.get("productividad_nivel", 5)
                    col_score, col_resumen = st.columns([1, 2])

                    with col_score:
                        render_score(score)
                        if score >= 8:
                            st.success("🔥 ¡Día excelente!")
                            st.balloons()
                        elif score >= 5:
                            st.warning("⚠️ Día mejorable.")
                        else:
                            st.error("🚨 Día crítico. Mañana hay que cumplir.")

                    with col_resumen:
                        render_card("Resumen del día",      resultado.get("resumen_dia"),                  "blue",   "📌")
                        render_card("Mensaje del coach",    resultado.get("mensaje_coach"),                "purple", "🎙️")

                    st.markdown("#### Detalles")
                    c1, c2 = st.columns(2)
                    with c1:
                        render_card("Error principal",      resultado.get("error_principal"),              "red",    "⚠️")
                        render_card("Logro principal",      resultado.get("logro_principal"),              "green",  "✅")
                    with c2:
                        render_card("Acción mañana",        resultado.get("accion_obligatoria_manana"),    "yellow", "⚡")
                        render_card("Regla clave",          resultado.get("regla_clave"),                  "blue",   "📜")

                    render_card("Patrón detectado",         resultado.get("patron_detectado"),             "purple", "🔍")

    # ── TAB 2: HISTORIAL ──
    with tab_historial:
        registros = estado["historial_ui"]
        st.markdown(f"**{len(registros)} registros** (últimos {HISTORIAL_UI} días)")
        st.markdown("---")
        render_historial(registros)

        if registros:
            with st.expander("🔎 Ver JSON completo"):
                st.json(registros)

# ══════════════════════════════════════════════════
# 10. ENTRY POINT
# ══════════════════════════════════════════════════
if is_logged_in():
    render_app()
else:
    render_auth()
