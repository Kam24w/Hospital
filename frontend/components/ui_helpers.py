# frontend/components/ui_helpers.py
"""
Componentes de UI reutilizables para Streamlit.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from constants import PRIORIDAD_CONFIG, ESTADO_COLOR


# ── BADGES HTML ───────────────────────────────────────────────────────────────

def badge_prioridad(prioridad: str) -> str:
    cfg = PRIORIDAD_CONFIG.get(prioridad, {})
    color  = cfg.get("color", "#888")
    label  = cfg.get("label", prioridad)
    return (
        f'<span style="background:{cfg.get("bg","#333")};color:{color};'
        f'border:1px solid {color};border-radius:6px;padding:3px 10px;'
        f'font-size:0.72rem;font-weight:600;letter-spacing:0.05em;">'
        f'{prioridad} · {label}</span>'
    )


def badge_estado(estado: str) -> str:
    color = ESTADO_COLOR.get(estado, "#888")
    label = estado.replace("_", " ").upper()
    return (
        f'<span style="background:rgba(255,255,255,0.05);color:{color};'
        f'border:1px solid {color}55;border-radius:6px;padding:3px 10px;'
        f'font-size:0.72rem;">'
        f'● {label}</span>'
    )


# ── MÉTRICA COLORIDA ──────────────────────────────────────────────────────────

def metrica_color(label: str, value: str, color: str, sub: str = ""):
    st.markdown(
        f"""
        <div style="
            background:#161b27;border:1px solid #1e2535;border-radius:12px;
            padding:1.1rem;border-top:2px solid {color};
        ">
            <div style="font-size:0.68rem;color:#6b7394;
                        font-family:monospace;letter-spacing:0.1em;
                        text-transform:uppercase;margin-bottom:0.3rem;">
                {label}
            </div>
            <div style="font-size:2.4rem;color:{color};
                        font-family:'Bebas Neue',sans-serif;line-height:1;
                        letter-spacing:0.04em;">
                {value}
            </div>
            {"<div style='font-size:0.7rem;color:#6b7394;margin-top:0.2rem;font-family:monospace;'>" + sub + "</div>" if sub else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── TABLA DE PACIENTES ────────────────────────────────────────────────────────

def tabla_pacientes(pacientes: list[dict]) -> None:
    """Renderiza la cola de pacientes como tabla HTML estilizada."""
    if not pacientes:
        st.info("No hay pacientes con los filtros seleccionados.")
        return

    filas_html = ""
    for p in pacientes:
        espera = p.get("tiempo_espera_min")
        espera_str = f"{espera} min" if espera is not None else "—"
        hora = p.get("hora_ingreso", "")[:16].replace("T", " ") if p.get("hora_ingreso") else "—"

        cfg_p = PRIORIDAD_CONFIG.get(p["prioridad"], {})
        color_p = cfg_p.get("color", "#888")
        label_p = f"{p['prioridad']} · {cfg_p.get('label','')}"

        color_e = ESTADO_COLOR.get(p.get("estado",""), "#888")
        label_e = p.get("estado","").replace("_"," ").upper()

        filas_html += f"""
        <tr style="border-bottom:1px solid #1e2535;transition:background 0.15s;"
            onmouseover="this.style.background='rgba(255,255,255,0.02)'"
            onmouseout="this.style.background='transparent'">
          <td style="padding:0.85rem 0.75rem;font-family:monospace;font-size:0.72rem;color:#6b7394;">
              {p.get('codigo_urgencia','—')}
          </td>
          <td style="padding:0.85rem 0.75rem;">
              <div style="font-size:0.88rem;font-weight:500;color:#e8eaf0;">
                  {p.get('apellidos','')}, {p.get('nombre','')}
              </div>
              <div style="font-size:0.7rem;color:#6b7394;font-family:monospace;">
                  {p.get('edad','?')} años · {p.get('area','—')}
              </div>
          </td>
          <td style="padding:0.85rem 0.75rem;">
              <span style="background:{cfg_p.get('bg','#333')};color:{color_p};
                           border:1px solid {color_p};border-radius:5px;
                           padding:3px 9px;font-size:0.68rem;font-weight:600;
                           font-family:monospace;white-space:nowrap;">
                  {label_p}
              </span>
          </td>
          <td style="padding:0.85rem 0.75rem;font-size:0.82rem;color:#a0aabb;">
              {p.get('motivo','—')}
          </td>
          <td style="padding:0.85rem 0.75rem;font-family:monospace;font-size:0.78rem;color:#6b7394;">
              {hora}
          </td>
          <td style="padding:0.85rem 0.75rem;font-family:monospace;font-size:0.82rem;color:#e8eaf0;">
              {espera_str}
          </td>
          <td style="padding:0.85rem 0.75rem;">
              <span style="color:{color_e};font-size:0.75rem;font-family:monospace;">
                  ● {label_e}
              </span>
          </td>
        </tr>
        """

    tabla = f"""
    <div style="background:#111520;border:1px solid #1e2535;border-radius:12px;overflow:hidden;overflow-x:auto;">
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#0d1117;border-bottom:1px solid #1e2535;">
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">ID</th>
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">Paciente</th>
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">Prioridad</th>
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">Motivo</th>
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">Ingreso</th>
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">Espera</th>
            <th style="padding:0.75rem;text-align:left;font-family:monospace;
                       font-size:0.65rem;color:#6b7394;letter-spacing:0.1em;
                       text-transform:uppercase;">Estado</th>
          </tr>
        </thead>
        <tbody>
          {filas_html}
        </tbody>
      </table>
    </div>
    """
    # Streamlit can escape complex table HTML in markdown on some versions.
    # Render with components.html to force proper HTML table rendering.
    table_height = min(620, max(220, 72 + len(pacientes) * 54))
    components.html(tabla, height=table_height, scrolling=True)


# ── SIGNOS VITALES ────────────────────────────────────────────────────────────

def mostrar_signos_vitales(p: dict) -> None:
    sv = {
        "PA": f"{p.get('presion_sistolica','—')}/{p.get('presion_diastolica','—')} mmHg",
        "FC": f"{p.get('frecuencia_cardiaca','—')} bpm",
        "SpO₂": f"{p.get('saturacion_o2','—')} %",
        "Temp": f"{p.get('temperatura','—')} °C",
        "FR": f"{p.get('frecuencia_resp','—')} rpm",
    }
    alertas = []
    if p.get("saturacion_o2") and p["saturacion_o2"] < 90:
        alertas.append("saturacion_o2")
    if p.get("frecuencia_cardiaca") and (p["frecuencia_cardiaca"] > 130 or p["frecuencia_cardiaca"] < 50):
        alertas.append("frecuencia_cardiaca")

    cols = st.columns(len(sv))
    for col, (key, val) in zip(cols, sv.items()):
        is_alert = any(k in key.lower() for k in alertas)
        color = "#ff2d55" if is_alert else "#5ac8fa"
        with col:
            st.markdown(
                f"""<div style="text-align:center;background:#111520;
                    border:1px solid {'#ff2d5544' if is_alert else '#1e2535'};
                    border-radius:8px;padding:0.6rem;">
                    <div style="font-size:0.65rem;color:#6b7394;font-family:monospace;
                                text-transform:uppercase;">{key}</div>
                    <div style="font-size:1.05rem;color:{color};font-family:monospace;
                                font-weight:600;margin-top:2px;">{val}</div>
                </div>""",
                unsafe_allow_html=True,
            )


# ── CSS GLOBAL ───────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* Streamlit overrides */
.stApp { background-color: #0a0d12 !important; }
section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1e2535 !important; }
.stButton button {
    background: #0a84ff !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.85 !important; }
[data-testid="stMetricValue"] { color: #e8eaf0 !important; }
.stSelectbox label, .stTextInput label, .stNumberInput label {
    color: #6b7394 !important;
    font-family: monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
div[data-testid="stExpander"] {
    background: #111520 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 8px !important;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
