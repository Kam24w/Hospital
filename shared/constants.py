# shared/constants.py
# Constantes compartidas entre frontend y backend

from enum import Enum


class Prioridad(str, Enum):
    P1_CRITICO = "P1"
    P2_EMERGENCIA = "P2"
    P3_URGENTE = "P3"
    P4_MENOS_URGENTE = "P4"
    P5_NO_URGENTE = "P5"


class EstadoPaciente(str, Enum):
    EN_ESPERA = "en_espera"
    EN_ATENCION = "en_atencion"
    EN_OBSERVACION = "en_observacion"
    ALTA = "alta"
    DERIVADO = "derivado"
    FALLECIDO = "fallecido"


class AreaHospital(str, Enum):
    SHOCK_ROOM = "Shock Room"
    TRAUMA = "Trauma"
    CARDIOLOGIA = "Cardiología"
    NEUROLOGIA = "Neurología"
    GENERAL = "General"
    PEDIATRIA = "Pediatría"
    GINECOLOGIA = "Ginecología"
    OBSERVACION = "Observación"
    CIRUGIA = "Cirugía"


# Colores y etiquetas por prioridad (para UI)
PRIORIDAD_CONFIG = {
    "P1": {
        "label": "CRÍTICO",
        "color": "#ff2d55",
        "bg": "rgba(255,45,85,0.15)",
        "tiempo_max_min": 0,
        "descripcion": "Atención INMEDIATA — Riesgo vital"
    },
    "P2": {
        "label": "EMERGENCIA",
        "color": "#ff6b2b",
        "bg": "rgba(255,107,43,0.15)",
        "tiempo_max_min": 15,
        "descripcion": "Atención en ≤ 15 minutos"
    },
    "P3": {
        "label": "URGENTE",
        "color": "#ffd60a",
        "bg": "rgba(255,214,10,0.15)",
        "tiempo_max_min": 30,
        "descripcion": "Atención en ≤ 30 minutos"
    },
    "P4": {
        "label": "MENOS URGENTE",
        "color": "#30d158",
        "bg": "rgba(48,209,88,0.15)",
        "tiempo_max_min": 60,
        "descripcion": "Atención en ≤ 60 minutos"
    },
    "P5": {
        "label": "NO URGENTE",
        "color": "#5ac8fa",
        "bg": "rgba(90,200,250,0.15)",
        "tiempo_max_min": 120,
        "descripcion": "Consulta programada o derivación"
    },
}

# Estado → color
ESTADO_COLOR = {
    "en_espera": "#ffd60a",
    "en_atencion": "#30d158",
    "en_observacion": "#0a84ff",
    "alta": "#5ac8fa",
    "derivado": "#bf5af2",
    "fallecido": "#6b7394",
}

# URL del backend (puede sobreescribirse con variable de entorno)
BACKEND_URL = "http://localhost:8000"
API_VERSION = "/api/v1"
