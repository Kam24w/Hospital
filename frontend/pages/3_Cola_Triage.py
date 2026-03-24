# frontend/pages/3_Cola_Triage.py
"""
Página 3: Cola de Triage — Gestión y actualización de pacientes activos.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../components"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

import streamlit as st

import api_client as api
from ui_helpers import inject_css, tabla_pacientes, badge_prioridad, badge_estado, mostrar_signos_vitales
from constants import PRIORIDAD_CONFIG, ESTADO_COLOR, AreaHospital

st.set_page_config(page_title="Cola Triage", page_icon="C", layout="wide")
inject_css()

st.markdown(
    """
    <h2 style="color:#fff;margin-bottom:0.3rem;">Cola de Triage</h2>
    <p style="color:#6b7394;font-family:monospace;font-size:0.75rem;margin-bottom:1.5rem;">
        Gestión de pacientes activos — actualizaciones de estado y prioridad
    </p>
    """,
    unsafe_allow_html=True,
)

# ── FILTROS ───────────────────────────────────────────────────────────────────
with st.expander("Filtros", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filtro_prioridad = st.multiselect(
            "Prioridad", options=["P1", "P2", "P3", "P4", "P5"],
            default=[], placeholder="Todas"
        )
    with fc2:
        filtro_estado = st.multiselect(
            "Estado",
            options=["en_espera", "en_atencion", "en_observacion", "alta", "derivado"],
            default=[], placeholder="Todos"
        )
    with fc3:
        filtro_area = st.selectbox("Área", options=["Todas"] + [a.value for a in AreaHospital])

# Cargar pacientes
todos = api.obtener_pacientes(activo=True)

# Aplicar filtros
pacientes = todos
if filtro_prioridad:
    pacientes = [p for p in pacientes if p["prioridad"] in filtro_prioridad]
if filtro_estado:
    pacientes = [p for p in pacientes if p["estado"] in filtro_estado]
if filtro_area and filtro_area != "Todas":
    pacientes = [p for p in pacientes if p["area"] == filtro_area]

st.markdown(f"**{len(pacientes)}** paciente(s) encontrado(s)")
st.markdown("<br>", unsafe_allow_html=True)

# ── TABLA ─────────────────────────────────────────────────────────────────────
tabla_pacientes(pacientes)

st.markdown("<br>", unsafe_allow_html=True)

# ── PANEL DE ACTUALIZACIÓN ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Actualizar Paciente")

if not todos:
    st.info("No hay pacientes activos en este momento.")
else:
    opciones = {
        f"{p['codigo_urgencia']} — {p['apellidos']}, {p['nombre']} ({p['prioridad']})": p["id"]
        for p in todos
    }

    seleccionado_label = st.selectbox("Seleccionar paciente:", list(opciones.keys()))
    paciente_id = opciones[seleccionado_label]

    # Obtener detalle del paciente
    detalle = api.obtener_paciente(paciente_id)
    if detalle:
        st.markdown(f"<br>", unsafe_allow_html=True)

        col_det, col_edit = st.columns([1, 1])

        with col_det:
            st.markdown("##### Estado actual")
            st.markdown(
                f"""<div style="background:#111520;border:1px solid #1e2535;
                                border-radius:10px;padding:1rem;">
                    <div style="margin-bottom:0.6rem;">
                        {badge_prioridad(detalle['prioridad'])}
                        &nbsp;&nbsp;
                        {badge_estado(detalle['estado'])}
                    </div>
                    <div style="font-size:0.82rem;color:#a0aabb;line-height:1.7;">
                        <b style="color:#e8eaf0;">Motivo:</b> {detalle['motivo']}<br>
                        <b style="color:#e8eaf0;">Área:</b> {detalle['area']}<br>
                        <b style="color:#e8eaf0;">Edad:</b> {detalle['edad']} años<br>
                        {'<b style="color:#e8eaf0;">Médico:</b> ' + detalle['medico_asignado'] + '<br>' if detalle.get('medico_asignado') else ''}
                        {'<b style="color:#e8eaf0;">Descripción:</b> ' + detalle['descripcion'] + '<br>' if detalle.get('descripcion') else ''}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown("##### Signos Vitales")
            mostrar_signos_vitales(detalle)

        with col_edit:
            st.markdown("##### Modificar")

            nueva_prioridad = st.selectbox(
                "Nueva prioridad",
                options=list(PRIORIDAD_CONFIG.keys()),
                index=list(PRIORIDAD_CONFIG.keys()).index(detalle["prioridad"]),
                format_func=lambda p: f"{p} — {PRIORIDAD_CONFIG[p]['label']}",
                key="upd_prioridad",
            )

            nuevo_estado = st.selectbox(
                "Nuevo estado",
                options=["en_espera", "en_atencion", "en_observacion", "alta", "derivado"],
                index=["en_espera", "en_atencion", "en_observacion", "alta", "derivado"].index(
                    detalle.get("estado", "en_espera")
                ),
                key="upd_estado",
            )

            nueva_area = st.selectbox(
                "Área",
                options=[a.value for a in AreaHospital],
                index=[a.value for a in AreaHospital].index(detalle["area"])
                      if detalle["area"] in [a.value for a in AreaHospital] else 0,
                key="upd_area",
            )

            nuevo_medico = st.text_input(
                "Médico asignado",
                value=detalle.get("medico_asignado", "") or "",
                key="upd_medico",
            )

            st.markdown("**Actualizar signos vitales:**")
            sv1, sv2 = st.columns(2)
            with sv1:
                u_fc   = st.number_input("FC", value=detalle.get("frecuencia_cardiaca") or 0, key="u_fc")
                u_pas  = st.number_input("PA Sistólica", value=detalle.get("presion_sistolica") or 0, key="u_pas")
                u_temp = st.number_input("Temperatura", value=detalle.get("temperatura") or 0.0, step=0.1, key="u_temp")
            with sv2:
                u_spo2 = st.number_input("SpO₂", value=detalle.get("saturacion_o2") or 0.0, step=0.1, key="u_spo2")
                u_pad  = st.number_input("PA Diastólica", value=detalle.get("presion_diastolica") or 0, key="u_pad")
                u_fr   = st.number_input("Frec. Resp.", value=detalle.get("frecuencia_resp") or 0, key="u_fr")

            c_act, c_alta = st.columns(2)

            with c_act:
                if st.button("Guardar cambios", use_container_width=True):
                    cambios = {
                        "prioridad":       nueva_prioridad,
                        "estado":          nuevo_estado,
                        "area":            nueva_area,
                        "medico_asignado": nuevo_medico or None,
                    }
                    sv_update = {}
                    if u_fc   > 0:   sv_update["frecuencia_cardiaca"] = u_fc
                    if u_spo2 > 0:   sv_update["saturacion_o2"]       = u_spo2
                    if u_pas  > 0:   sv_update["presion_sistolica"]    = u_pas
                    if u_pad  > 0:   sv_update["presion_diastolica"]   = u_pad
                    if u_temp > 0:   sv_update["temperatura"]           = u_temp
                    if u_fr   > 0:   sv_update["frecuencia_resp"]       = u_fr
                    if sv_update:    cambios["signos_vitales"] = sv_update

                    resultado = api.actualizar_paciente(paciente_id, cambios)
                    if resultado and "error" not in resultado:
                        st.success("Paciente actualizado")
                        st.rerun()
                    else:
                        st.error(f"Error: {resultado.get('error') if resultado else 'Sin conexión'}")

            with c_alta:
                if st.button("Dar de Alta", use_container_width=True, type="secondary"):
                    if api.dar_alta_paciente(paciente_id):
                        st.success(f"{detalle['codigo_urgencia']} dado de alta")
                        st.rerun()
                    else:
                        st.error("No se pudo dar de alta al paciente")
