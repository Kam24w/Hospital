# frontend/pages/4_Recursos.py
"""
Página 4: Gestión de Recursos hospitalarios.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../components"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

import streamlit as st
import plotly.graph_objects as go

import api_client as api
from ui_helpers import inject_css

st.set_page_config(page_title="Recursos — Triage", page_icon="R", layout="wide")
inject_css()

st.markdown(
    """
    <h2 style="color:#fff;margin-bottom:0.3rem;">Recursos Hospitalarios</h2>
    <p style="color:#6b7394;font-family:monospace;font-size:0.75rem;margin-bottom:1.5rem;">
        Monitoreo y actualización de disponibilidad de recursos en tiempo real
    </p>
    """,
    unsafe_allow_html=True,
)

recursos = api.obtener_recursos()

if not recursos:
    st.error("No se pueden cargar los recursos. Verifica la conexión con el backend.")
    st.stop()

# ── MÉTRICAS RESUMEN ──────────────────────────────────────────────────────────
tipos = {}
for r in recursos:
    t = r["tipo"]
    if t not in tipos:
        tipos[t] = {"total": 0, "disponibles": 0}
    tipos[t]["total"]       += r["total"]
    tipos[t]["disponibles"] += r["disponibles"]

tipo_emoji = {"cama": "CAMA", "personal": "PERSONAL", "sala": "SALA", "equipo": "EQUIPO"}

cols = st.columns(len(tipos))
for col, (tipo, data) in zip(cols, tipos.items()):
    disp = data["disponibles"]
    total = data["total"]
    pct_libre = (disp / total * 100) if total > 0 else 0
    color = "#30d158" if pct_libre > 30 else "#ffd60a" if pct_libre > 10 else "#ff2d55"
    with col:
        st.markdown(
            f"""<div style="background:#111520;border:1px solid #1e2535;
                            border-top:2px solid {color};border-radius:12px;padding:1rem;">
                <div style="font-size:0.68rem;color:#6b7394;font-family:monospace;
                             text-transform:uppercase;letter-spacing:0.1em;">
                    {tipo_emoji.get(tipo,'RECURSO')} {tipo}
                </div>
                <div style="font-size:2rem;color:{color};font-family:monospace;
                             font-weight:700;margin:0.3rem 0;">
                    {disp}<span style="font-size:1rem;color:#6b7394;">/{total}</span>
                </div>
                <div style="font-size:0.72rem;color:#6b7394;font-family:monospace;">
                    {pct_libre:.0f}% disponible
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICO GAUGE ─────────────────────────────────────────────────────────────
st.markdown("#### Ocupación por Recurso")

n = len(recursos)
cols_gauge = st.columns(min(n, 4))
for i, (col, r) in enumerate(zip(cols_gauge * ((n // 4) + 1), recursos)):
    if i >= n:
        break
    pct_ocup = r.get("ocupacion_pct", 0)
    color = "#30d158" if pct_ocup < 60 else "#ffd60a" if pct_ocup < 85 else "#ff2d55"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_ocup,
        number={"suffix": "%", "font": {"size": 20, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 9, "color": "#6b7394"}},
            "bar": {"color": color},
            "bgcolor": "#1e2535",
            "bordercolor": "#0a0d12",
            "steps": [
                {"range": [0, 60], "color": "rgba(48,209,88,0.08)"},
                {"range": [60, 85], "color": "rgba(255,214,10,0.08)"},
                {"range": [85, 100], "color": "rgba(255,45,85,0.08)"},
            ],
        },
        title={"text": f"<b>{r['nombre']}</b><br><span style='font-size:10px'>{r['disponibles']}/{r['total']} libres</span>",
               "font": {"size": 12, "color": "#e8eaf0"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(t=60, b=10, l=10, r=10),
        font=dict(color="#e8eaf0"),
    )
    with col:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── ACTUALIZAR RECURSOS ───────────────────────────────────────────────────────
st.markdown("#### Actualizar Disponibilidad")

recurso_opciones = {f"{r['nombre']} ({r['tipo']} · {r.get('area','')})": r for r in recursos}
sel_label = st.selectbox("Seleccionar recurso:", list(recurso_opciones.keys()))
sel_recurso = recurso_opciones[sel_label]

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    st.metric("Total", sel_recurso["total"])
with c2:
    st.metric("Disponibles actuales", sel_recurso["disponibles"])
with c3:
    nuevo_disp = st.number_input(
        "Nueva disponibilidad:",
        min_value=0,
        max_value=sel_recurso["total"],
        value=sel_recurso["disponibles"],
    )

if st.button("Actualizar recurso"):
    resultado = api.actualizar_recurso(sel_recurso["id"], nuevo_disp)
    if resultado and "error" not in resultado:
        st.success(f"{sel_recurso['nombre']} actualizado: {nuevo_disp}/{sel_recurso['total']}")
        st.rerun()
    else:
        err = resultado.get("error") if resultado else "Sin conexión"
        st.error(f"Error: {err}")

st.markdown("<br>", unsafe_allow_html=True)

# ── TABLA COMPLETA ────────────────────────────────────────────────────────────
st.markdown("#### Inventario Completo")

filas = ""
for r in recursos:
    pct = r.get("ocupacion_pct", 0)
    color = "#30d158" if pct < 60 else "#ffd60a" if pct < 85 else "#ff2d55"
    bar_width = min(pct, 100)
    filas += f"""
    <tr style="border-bottom:1px solid #1e2535;">
        <td style="padding:0.8rem 0.75rem;color:#e8eaf0;font-size:0.88rem;">
            {tipo_emoji.get(r['tipo'],'RECURSO')} {r['nombre']}
        </td>
        <td style="padding:0.8rem 0.75rem;font-family:monospace;font-size:0.75rem;color:#6b7394;">
            {r['tipo']}
        </td>
        <td style="padding:0.8rem 0.75rem;font-family:monospace;font-size:0.75rem;color:#6b7394;">
            {r.get('area','—')}
        </td>
        <td style="padding:0.8rem 0.75rem;text-align:center;font-family:monospace;font-size:0.88rem;color:{color};font-weight:600;">
            {r['disponibles']}/{r['total']}
        </td>
        <td style="padding:0.8rem 0.75rem;min-width:150px;">
            <div style="background:#1e2535;border-radius:4px;height:6px;overflow:hidden;">
                <div style="width:{bar_width}%;height:100%;background:{color};border-radius:4px;"></div>
            </div>
            <div style="font-family:monospace;font-size:0.65rem;color:{color};margin-top:3px;">{pct:.0f}% ocupado</div>
        </td>
    </tr>
    """

st.markdown(
    f"""
    <div style="background:#111520;border:1px solid #1e2535;border-radius:12px;overflow:hidden;">
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:#0d1117;border-bottom:1px solid #1e2535;">
                    <th style="padding:0.75rem;text-align:left;font-family:monospace;font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;text-transform:uppercase;">Recurso</th>
                    <th style="padding:0.75rem;text-align:left;font-family:monospace;font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;text-transform:uppercase;">Tipo</th>
                    <th style="padding:0.75rem;text-align:left;font-family:monospace;font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;text-transform:uppercase;">Área</th>
                    <th style="padding:0.75rem;text-align:center;font-family:monospace;font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;text-transform:uppercase;">Disponibles</th>
                    <th style="padding:0.75rem;text-align:left;font-family:monospace;font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;text-transform:uppercase;">Ocupación</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>
    </div>
    """,
    unsafe_allow_html=True,
)
