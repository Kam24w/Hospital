# frontend/pages/2_Admision.py
"""
Página 2: Admisión de nuevos pacientes con clasificación automática.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../components"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

import streamlit as st

import api_client as api
from ui_helpers import inject_css, badge_prioridad, mostrar_signos_vitales
from constants import PRIORIDAD_CONFIG, AreaHospital

st.set_page_config(page_title="Admisión — Triage", page_icon="A", layout="wide")
inject_css()

st.markdown(
    """
    <h2 style="color:#fff;margin-bottom:0.3rem;">Admisión de Paciente</h2>
    <p style="color:#6b7394;font-family:monospace;font-size:0.75rem;margin-bottom:1.5rem;">
        Registro de nuevo paciente y asignación de prioridad de triage
    </p>
    """,
    unsafe_allow_html=True,
)

col_form, col_info = st.columns([2, 1])

# ── FORMULARIO ────────────────────────────────────────────────────────────────
with col_form:
    st.markdown("#### Datos del Paciente")

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        nombre = st.text_input("Nombre *", placeholder="Nombre del paciente")
    with c2:
        apellidos = st.text_input("Apellidos *", placeholder="Apellidos del paciente")
    with c3:
        edad = st.number_input("Edad *", min_value=0, max_value=130, value=35)

    c4, c5 = st.columns([1, 1])
    with c4:
        dni = st.text_input("DNI / Identificación", placeholder="Opcional")
    with c5:
        area = st.selectbox("Área de destino *", [a.value for a in AreaHospital])

    motivo = st.text_input("Motivo de consulta *", placeholder="Síntoma o motivo principal")
    descripcion = st.text_area(
        "Descripción clínica",
        placeholder="Antecedentes, evolución, observaciones...",
        height=80,
    )
    medico = st.text_input("Médico asignado", placeholder="Nombre del médico (opcional)")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Signos Vitales")

    sv1, sv2, sv3 = st.columns(3)
    with sv1:
        fc = st.number_input("FC (bpm)", min_value=0, max_value=300, value=0)
        pa_s = st.number_input("PA Sistólica (mmHg)", min_value=0, max_value=300, value=0)
    with sv2:
        spo2 = st.number_input("SpO₂ (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        pa_d = st.number_input("PA Diastólica (mmHg)", min_value=0, max_value=200, value=0)
    with sv3:
        temp = st.number_input("Temperatura (°C)", min_value=0.0, max_value=45.0, value=0.0, step=0.1)
        fr = st.number_input("Frec. Respiratoria (rpm)", min_value=0, max_value=60, value=0)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Prioridad de Triage")

    # Botón clasificación automática
    if st.button("Clasificar automáticamente con signos vitales"):
        resultado = api.clasificar_automatico(
            edad=edad,
            frecuencia_cardiaca=fc if fc > 0 else None,
            saturacion_o2=spo2 if spo2 > 0 else None,
            presion_sistolica=pa_s if pa_s > 0 else None,
            temperatura=temp if temp > 0 else None,
            frecuencia_resp=fr if fr > 0 else None,
        )
        if resultado and "error" not in resultado:
            st.session_state["prioridad_sugerida"] = resultado["prioridad_sugerida"]
            st.session_state["criterios_triage"] = resultado.get("criterios", [])
            st.session_state["descripcion_triage"] = resultado.get("descripcion", "")
        else:
            detalle = resultado.get("error") if isinstance(resultado, dict) else None
            st.warning(f"No se pudo clasificar automáticamente. {detalle or 'Verifica backend y datos enviados.'}")

    if "criterios_triage" in st.session_state and st.session_state["criterios_triage"]:
        st.info(
            f"**Prioridad sugerida: {st.session_state.get('prioridad_sugerida')}** — "
            f"{st.session_state.get('descripcion_triage')}\n\n"
            f"Criterios: {', '.join(st.session_state['criterios_triage'])}"
        )

    prioridad_default = list(PRIORIDAD_CONFIG.keys()).index(
        st.session_state.get("prioridad_sugerida", "P3")
    )
    prioridad = st.selectbox(
        "Prioridad asignada *",
        options=list(PRIORIDAD_CONFIG.keys()),
        index=prioridad_default,
        format_func=lambda p: f"{p} — {PRIORIDAD_CONFIG[p]['label']} ({PRIORIDAD_CONFIG[p]['descripcion']})",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BOTÓN ADMITIR ─────────────────────────────────────────────────────────
    if st.button("ADMITIR PACIENTE", type="primary", use_container_width=True):
        errores = []
        if not nombre.strip():    errores.append("Nombre requerido")
        if nombre.strip() and len(nombre.strip()) < 2: errores.append("Nombre debe tener al menos 2 caracteres")
        if not apellidos.strip(): errores.append("Apellidos requeridos")
        if apellidos.strip() and len(apellidos.strip()) < 2: errores.append("Apellidos deben tener al menos 2 caracteres")
        if not motivo.strip():    errores.append("Motivo de consulta requerido")
        if motivo.strip() and len(motivo.strip()) < 3: errores.append("Motivo debe tener al menos 3 caracteres")
        if edad <= 0:             errores.append("Edad debe ser mayor a 0")

        if errores:
            for e in errores:
                st.error(e)
        else:
            payload = {
                "nombre":          nombre.strip(),
                "apellidos":       apellidos.strip(),
                "edad":            edad,
                "dni":             dni.strip() or None,
                "prioridad":       prioridad,
                "motivo":          motivo.strip(),
                "descripcion":     descripcion.strip() or None,
                "area":            area,
                "medico_asignado": medico.strip() or None,
            }

            sv_data = {}
            if fc > 0:    sv_data["frecuencia_cardiaca"] = fc
            if spo2 > 0:  sv_data["saturacion_o2"]       = spo2
            if pa_s > 0:  sv_data["presion_sistolica"]    = pa_s
            if pa_d > 0:  sv_data["presion_diastolica"]   = pa_d
            if temp > 0:  sv_data["temperatura"]           = temp
            if fr > 0:    sv_data["frecuencia_resp"]       = fr
            if sv_data:
                payload["signos_vitales"] = sv_data

            resultado = api.admitir_paciente(payload)

            if resultado and "error" not in resultado:
                st.success(
                    f"Paciente **{resultado['codigo_urgencia']}** admitido correctamente — "
                    f"Prioridad: **{prioridad}**"
                )
                # Limpiar sugerencias
                for key in ["prioridad_sugerida", "criterios_triage", "descripcion_triage"]:
                    st.session_state.pop(key, None)
                st.rerun()
            elif resultado and "error" in resultado:
                st.error(f"Error al admitir: {resultado['error']}")
            else:
                st.error("No se pudo conectar al backend.")

# ── PANEL INFORMATIVO ─────────────────────────────────────────────────────────
with col_info:
    st.markdown("#### Escala de Triage")
    for p, cfg in PRIORIDAD_CONFIG.items():
        st.markdown(
            f"""<div style="background:{cfg['bg']};border:1px solid {cfg['color']}44;
                            border-left:3px solid {cfg['color']};border-radius:8px;
                            padding:0.75rem;margin-bottom:0.6rem;">
                <div style="font-weight:600;color:{cfg['color']};
                             font-family:monospace;font-size:0.78rem;">
                    {p} — {cfg['label']}
                </div>
                <div style="font-size:0.75rem;color:#a0aabb;margin-top:2px;">
                    {cfg['descripcion']}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Estado actual")
    stats = api.obtener_stats()
    if stats:
        total = stats.get("total_activos", 0)
        pp = stats.get("por_prioridad", {})
        st.markdown(
            f"""<div style="background:#111520;border:1px solid #1e2535;border-radius:8px;
                            padding:1rem;font-family:monospace;font-size:0.78rem;">
                <div style="color:#6b7394;margin-bottom:0.5rem;">
                    PACIENTES ACTIVOS: <span style="color:#e8eaf0;">{total}</span>
                </div>
                {''.join([
                    f'<div style="color:{PRIORIDAD_CONFIG[p]["color"]};margin-bottom:2px;">'
                    f'{p}: {pp.get(p,0)} pacientes</div>'
                    for p in ["P1","P2","P3","P4","P5"]
                ])}
            </div>""",
            unsafe_allow_html=True,
        )
