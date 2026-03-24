# frontend/app.py
"""
Sistema de Triage — Frontend Streamlit
Punto de entrada. Página principal = Dashboard.

Ejecución:
    streamlit run app.py
"""
import sys
import os

# Paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "components"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../shared"))

import streamlit as st

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Triage — Sala de Urgencias",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_helpers import inject_css
import api_client as api

inject_css()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1rem 0 1.5rem;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem;">
                <div style="background:#ff2d55;border-radius:8px;width:36px;height:36px;
                            display:flex;align-items:center;justify-content:center;font-size:18px;">
                    H
                </div>
                <div>
                    <div style="font-family:monospace;font-size:0.85rem;color:#e8eaf0;font-weight:600;">
                        HGU URGENCIAS
                    </div>
                    <div style="font-family:monospace;font-size:0.68rem;color:#6b7394;">
                        Sistema de Triage v2.4
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Estado del backend
    if api.backend_disponible():
        st.success("Backend conectado", icon=None)
    else:
        st.error("Backend no disponible")
        st.caption("Inicia el backend: `uvicorn main:app --port 8000`")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-family:monospace;font-size:0.68rem;color:#6b7394;">
        <b style="color:#e8eaf0;">NAVEGACIÓN</b><br><br>
        Usa el menú de páginas de arriba para navegar entre secciones.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        """
        <div style="font-family:monospace;font-size:0.65rem;color:#6b7394;line-height:1.6;">
        <b style="color:#5ac8fa;">STACK TECNOLÓGICO</b><br>
        Frontend: Streamlit<br>
        Backend: FastAPI + Uvicorn<br>
        ORM: SQLAlchemy<br>
        DB: SQLite / PostgreSQL<br>
        Validación: Pydantic v2
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── PÁGINA PRINCIPAL (BIENVENIDA / DASHBOARD RÁPIDO) ─────────────────────────
st.markdown(
    """
    <h1 style="font-family:'DM Sans',sans-serif;font-size:2.8rem;font-weight:700;
               color:#fff;line-height:1.1;margin-bottom:0.3rem;">
        Sistema de <span style="color:#ff2d55;">Triage</span><br>
        Sala de Urgencias
    </h1>
    <p style="font-family:monospace;font-size:0.82rem;color:#6b7394;margin-bottom:2rem;">
        // HOSPITAL GENERAL UNIVERSITARIO · MÓDULO DE GESTIÓN DE URGENCIAS
    </p>
    """,
    unsafe_allow_html=True,
)

# Accesos rápidos
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """<div style="background:#111520;border:1px solid #1e2535;border-top:2px solid #ff2d55;
                       border-radius:12px;padding:1.2rem;cursor:pointer;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">DB</div>
            <div style="font-weight:600;color:#e8eaf0;margin-bottom:0.3rem;">Dashboard</div>
            <div style="font-size:0.78rem;color:#6b7394;">Estadísticas en tiempo real</div>
        </div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """<div style="background:#111520;border:1px solid #1e2535;border-top:2px solid #ff6b2b;
                       border-radius:12px;padding:1.2rem;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">AD</div>
            <div style="font-weight:600;color:#e8eaf0;margin-bottom:0.3rem;">Admisión</div>
            <div style="font-size:0.78rem;color:#6b7394;">Registrar nuevo paciente</div>
        </div>""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """<div style="background:#111520;border:1px solid #1e2535;border-top:2px solid #ffd60a;
                       border-radius:12px;padding:1.2rem;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">CT</div>
            <div style="font-weight:600;color:#e8eaf0;margin-bottom:0.3rem;">Cola Triage</div>
            <div style="font-size:0.78rem;color:#6b7394;">Gestión de pacientes activos</div>
        </div>""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """<div style="background:#111520;border:1px solid #1e2535;border-top:2px solid #30d158;
                       border-radius:12px;padding:1.2rem;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">RC</div>
            <div style="font-weight:600;color:#e8eaf0;margin-bottom:0.3rem;">Recursos</div>
            <div style="font-size:0.78rem;color:#6b7394;">Camas, personal y equipos</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.info("Navega usando el menú lateral izquierdo para acceder a cada módulo.")
