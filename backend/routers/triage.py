# backend/routers/triage.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db, PacienteORM, EventoORM
from models.schemas import TriageStats, EventoResponse

router = APIRouter(prefix="/triage", tags=["Triage"])


# ── ESTADÍSTICAS GENERALES ────────────────────────────────────────────────────

@router.get("/stats", response_model=TriageStats, summary="Estadísticas del triage")
def estadisticas_triage(db: Session = Depends(get_db)):
    activos = (
        db.query(PacienteORM)
        .filter(PacienteORM.activo == True)
        .all()
    )

    por_prioridad: dict[str, int] = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 0}
    por_estado: dict[str, int]    = {}
    por_area: dict[str, int]      = {}
    alertas: list[str]            = []
    tiempos_espera: list[int]     = []

    for p in activos:
        por_prioridad[p.prioridad] = por_prioridad.get(p.prioridad, 0) + 1
        por_estado[p.estado]       = por_estado.get(p.estado, 0) + 1
        por_area[p.area]           = por_area.get(p.area, 0) + 1

        # Calcular tiempo de espera
        if p.estado == "en_espera":
            espera = int((datetime.utcnow() - p.hora_ingreso).total_seconds() / 60)
            tiempos_espera.append(espera)

            # Alertas por prioridad sobrepasada
            limites = {"P1": 0, "P2": 15, "P3": 30, "P4": 60, "P5": 120}
            lim = limites.get(p.prioridad, 999)
            if espera > lim:
                alertas.append(
                    f"ALERTA {p.codigo_urgencia} ({p.prioridad}): esperando {espera} min "
                    f"(límite: {lim} min)"
                )

        # Alertas de signos vitales
        if p.saturacion_o2 is not None and p.saturacion_o2 < 90:
            alertas.append(f"ALERTA {p.codigo_urgencia}: SpO₂ crítica ({p.saturacion_o2}%)")
        if p.frecuencia_cardiaca is not None and (p.frecuencia_cardiaca > 130 or p.frecuencia_cardiaca < 40):
            alertas.append(f"ALERTA {p.codigo_urgencia}: FC anormal ({p.frecuencia_cardiaca} bpm)")
        if p.presion_sistolica is not None and p.presion_sistolica > 200:
            alertas.append(f"ALERTA {p.codigo_urgencia}: PA sistólica alta ({p.presion_sistolica} mmHg)")

    promedio_espera = sum(tiempos_espera) / len(tiempos_espera) if tiempos_espera else 0.0

    return TriageStats(
        total_activos               = len(activos),
        por_prioridad               = por_prioridad,
        por_estado                  = por_estado,
        por_area                    = por_area,
        tiempo_espera_promedio_min  = round(promedio_espera, 1),
        alertas                     = alertas,
    )


# ── REGISTRO DE EVENTOS ───────────────────────────────────────────────────────

@router.get("/eventos", response_model=list[EventoResponse], summary="Registro de actividad")
def listar_eventos(
    limit: int = 30,
    db: Session = Depends(get_db),
):
    eventos = (
        db.query(EventoORM)
        .order_by(EventoORM.timestamp.desc())
        .limit(limit)
        .all()
    )
    return eventos


# ── CLASIFICACIÓN AUTOMÁTICA (SCORING) ───────────────────────────────────────

@router.post("/clasificar", summary="Sugerir prioridad automáticamente")
def clasificar_paciente(
    edad: int,
    frecuencia_cardiaca: Optional[int] = None,
    saturacion_o2: Optional[float] = None,
    presion_sistolica: Optional[int] = None,
    temperatura: Optional[float] = None,
    frecuencia_resp: Optional[int] = None,
):
    """
    Algoritmo simplificado de scoring basado en el sistema Manchester Triage System.
    Devuelve la prioridad sugerida y los criterios detectados.
    """
    score = 0
    criterios = []

    # Saturación de oxígeno
    if saturacion_o2 is not None:
        if saturacion_o2 < 85:
            score += 40; criterios.append(f"SpO₂ crítica ({saturacion_o2}%)")
        elif saturacion_o2 < 90:
            score += 25; criterios.append(f"SpO₂ baja ({saturacion_o2}%)")
        elif saturacion_o2 < 95:
            score += 10; criterios.append(f"SpO₂ reducida ({saturacion_o2}%)")

    # Frecuencia cardíaca
    if frecuencia_cardiaca is not None:
        if frecuencia_cardiaca > 150 or frecuencia_cardiaca < 40:
            score += 35; criterios.append(f"FC crítica ({frecuencia_cardiaca} bpm)")
        elif frecuencia_cardiaca > 130 or frecuencia_cardiaca < 50:
            score += 20; criterios.append(f"FC anormal ({frecuencia_cardiaca} bpm)")
        elif frecuencia_cardiaca > 110:
            score += 8; criterios.append(f"Taquicardia leve ({frecuencia_cardiaca} bpm)")

    # Presión arterial sistólica
    if presion_sistolica is not None:
        if presion_sistolica < 80 or presion_sistolica > 220:
            score += 35; criterios.append(f"PA crítica ({presion_sistolica} mmHg)")
        elif presion_sistolica < 90 or presion_sistolica > 200:
            score += 20; criterios.append(f"PA anormal ({presion_sistolica} mmHg)")
        elif presion_sistolica > 160:
            score += 8; criterios.append(f"HTA ({presion_sistolica} mmHg)")

    # Temperatura
    if temperatura is not None:
        if temperatura > 41.0 or temperatura < 32.0:
            score += 30; criterios.append(f"Temperatura crítica ({temperatura}°C)")
        elif temperatura > 39.5 or temperatura < 35.0:
            score += 15; criterios.append(f"Temperatura anormal ({temperatura}°C)")

    # Frecuencia respiratoria
    if frecuencia_resp is not None:
        if frecuencia_resp > 35 or frecuencia_resp < 8:
            score += 30; criterios.append(f"FR crítica ({frecuencia_resp} rpm)")
        elif frecuencia_resp > 25 or frecuencia_resp < 12:
            score += 12; criterios.append(f"FR anormal ({frecuencia_resp} rpm)")

    # Factor edad
    if edad >= 75 or edad <= 2:
        score += 10; criterios.append(f"Edad de riesgo ({edad} años)")
    elif edad >= 65:
        score += 5

    # Mapear score → prioridad
    if score >= 40:    prioridad = "P1"
    elif score >= 25:  prioridad = "P2"
    elif score >= 12:  prioridad = "P3"
    elif score >= 5:   prioridad = "P4"
    else:              prioridad = "P5"

    return {
        "prioridad_sugerida": prioridad,
        "score":              score,
        "criterios":          criterios,
        "descripcion": {
            "P1": "CRÍTICO — Atención inmediata",
            "P2": "EMERGENCIA — ≤ 15 minutos",
            "P3": "URGENTE — ≤ 30 minutos",
            "P4": "MENOS URGENTE — ≤ 60 minutos",
            "P5": "NO URGENTE — puede esperar o derivar",
        }[prioridad],
    }
