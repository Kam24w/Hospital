# frontend/pages/1_Dashboard.py
"""
Página 1: Dashboard — Estadísticas en tiempo real.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../components"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

import api_client as api
from ui_helpers import inject_css, metrica_color, tabla_pacientes
from constants import PRIORIDAD_CONFIG, ESTADO_COLOR

st.set_page_config(page_title="Dashboard — Triage", page_icon="D", layout="wide")
inject_css()

# ── AUTO-REFRESCO ─────────────────────────────────────────────────────────────
if st.sidebar.button("Actualizar datos"):
    st.rerun()

refresco = st.sidebar.selectbox("Auto-actualizar cada:", ["Desactivado", "30s", "60s", "2min"])
if refresco != "Desactivado":
    secs = {"30s": 30, "60s": 60, "2min": 120}[refresco]
    st.markdown(f'<meta http-equiv="refresh" content="{secs}">', unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:1.5rem;">
        <div>
            <h2 style="color:#fff;margin:0;font-size:1.8rem;">Dashboard</h2>
            <p style="color:#6b7394;font-family:monospace;font-size:0.75rem;margin:0;">
                Última actualización: {datetime.now().strftime('%H:%M:%S')}
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── CARGAR DATOS ──────────────────────────────────────────────────────────────
stats = api.obtener_stats()
pacientes = api.obtener_pacientes()
eventos = api.obtener_eventos(limit=15)

if stats is None:
    st.error("No se puede conectar al backend. Verifica que esté en ejecución.")
    st.code("cd backend && uvicorn main:app --reload --port 8000")
    st.stop()

# ── MÉTRICAS PRINCIPALES ──────────────────────────────────────────────────────
pp = stats.get("por_prioridad", {})
cols = st.columns(5)

metricas = [
    ("P1 · Críticos",    str(pp.get("P1", 0)), "#ff2d55",  "Atención inmediata"),
    ("P2 · Emergencia",  str(pp.get("P2", 0)), "#ff6b2b",  "≤ 15 minutos"),
    ("P3 · Urgente",     str(pp.get("P3", 0)), "#ffd60a",  "≤ 30 minutos"),
    ("P4 · Espera",      str(pp.get("P4", 0)), "#30d158",  "≤ 60 minutos"),
    ("Tiempo Promedio",  f"{stats.get('tiempo_espera_promedio_min', 0):.0f}m", "#0a84ff", "min / espera"),
]

for col, (label, val, color, sub) in zip(cols, metricas):
    with col:
        metrica_color(label, val, color, sub)

st.markdown("<br>", unsafe_allow_html=True)

# ── ALERTAS ACTIVAS ───────────────────────────────────────────────────────────
alertas = stats.get("alertas", [])
if alertas:
    st.markdown("### Alertas Activas")
    for alerta in alertas:
        st.error(alerta)
    st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICOS ─────────────────────────────────────────────────────────────────
col_izq, col_der = st.columns([1, 1])

with col_izq:
    st.markdown("#### Distribución por Prioridad")
    por_p = pp
    labels = list(por_p.keys())
    values = list(por_p.values())
    colors = [PRIORIDAD_CONFIG[l]["color"] for l in labels if l in PRIORIDAD_CONFIG]

    fig_donut = go.Figure(go.Pie(
        labels=[f"{l} · {PRIORIDAD_CONFIG[l]['label']}" for l in labels if l in PRIORIDAD_CONFIG],
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0a0d12", width=2)),
        textinfo="label+value",
        textfont=dict(size=11, color="white"),
    ))
    fig_donut.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0"),
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_der:
    st.markdown("#### Distribución por Estado")
    por_e = stats.get("por_estado", {})
    if por_e:
        df_estado = pd.DataFrame(list(por_e.items()), columns=["Estado", "Cantidad"])
        df_estado["Color"] = df_estado["Estado"].map(ESTADO_COLOR)
        fig_bar = go.Figure(go.Bar(
            x=df_estado["Estado"].str.replace("_", " ").str.upper(),
            y=df_estado["Cantidad"],
            marker=dict(
                color=df_estado["Color"].tolist(),
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=df_estado["Cantidad"],
            textposition="outside",
            textfont=dict(color="white", size=12),
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf0"),
            height=300,
            margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(gridcolor="#1e2535", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="#1e2535"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ── ÁREAS ────────────────────────────────────────────────────────────────────
por_area = stats.get("por_area", {})
if por_area:
    st.markdown("#### Ocupación por Área")
    df_area = pd.DataFrame(list(por_area.items()), columns=["Área", "Pacientes"])
    df_area = df_area.sort_values("Pacientes", ascending=True)
    fig_h = go.Figure(go.Bar(
        x=df_area["Pacientes"], y=df_area["Área"],
        orientation="h",
        marker=dict(color="#0a84ff", opacity=0.85),
        text=df_area["Pacientes"], textposition="outside",
        textfont=dict(color="white"),
    ))
    fig_h.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0"),
        height=max(200, len(por_area) * 40),
        margin=dict(t=10, b=10, l=10, r=50),
        xaxis=dict(gridcolor="#1e2535"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_h, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── COLA DE PACIENTES ─────────────────────────────────────────────────────────
st.markdown("#### Cola Actual de Pacientes")
tabla_pacientes(pacientes)

st.markdown("<br>", unsafe_allow_html=True)

# ── REGISTRO DE ACTIVIDAD ─────────────────────────────────────────────────────
st.markdown("#### Registro de Actividad Reciente")
tipo_color = {
    "admision":     "#30d158",
    "cambio_estado": "#ffd60a",
    "alta":         "#5ac8fa",
    "recurso":      "#0a84ff",
    "alerta":       "#ff2d55",
}

for ev in eventos:
    ts = ev.get("timestamp", "")[:16].replace("T", " ")
    tipo = ev.get("tipo", "")
    color = tipo_color.get(tipo, "#6b7394")
    desc = ev.get("descripcion", "")
    st.markdown(
        f"""<div style="display:flex;gap:12px;padding:0.5rem 0;
                        border-bottom:1px solid #1e2535;align-items:center;">
            <span style="font-family:monospace;font-size:0.68rem;color:#6b7394;min-width:100px;">{ts}</span>
            <div style="width:7px;height:7px;border-radius:50%;background:{color};flex-shrink:0;"></div>
            <span style="font-size:0.82rem;color:#a0aabb;">{desc}</span>
        </div>""",
        unsafe_allow_html=True,
    )
