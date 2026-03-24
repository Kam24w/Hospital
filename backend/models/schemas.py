# backend/models/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ── PACIENTE ─────────────────────────────────────────────────────────────────

class SignosVitales(BaseModel):
    presion_sistolica:   Optional[int]   = Field(None, ge=50, le=300)
    presion_diastolica:  Optional[int]   = Field(None, ge=20, le=200)
    frecuencia_cardiaca: Optional[int]   = Field(None, ge=20, le=300)
    saturacion_o2:       Optional[float] = Field(None, ge=50.0, le=100.0)
    temperatura:         Optional[float] = Field(None, ge=30.0, le=45.0)
    frecuencia_resp:     Optional[int]   = Field(None, ge=5, le=60)


class PacienteCreate(BaseModel):
    nombre:          str = Field(..., min_length=2, max_length=120)
    apellidos:       str = Field(..., min_length=2, max_length=120)
    edad:            int = Field(..., ge=0, le=130)
    dni:             Optional[str] = None
    prioridad:       str = Field(..., pattern="^P[1-5]$")
    motivo:          str = Field(..., min_length=3, max_length=200)
    descripcion:     Optional[str] = None
    area:            str = Field(..., min_length=2, max_length=60)
    medico_asignado: Optional[str] = None
    signos_vitales:  Optional[SignosVitales] = None

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v: str) -> str:
        if v not in ("P1", "P2", "P3", "P4", "P5"):
            raise ValueError("Prioridad debe ser P1–P5")
        return v


class PacienteUpdate(BaseModel):
    prioridad:       Optional[str] = Field(None, pattern="^P[1-5]$")
    estado:          Optional[str] = None
    area:            Optional[str] = None
    medico_asignado: Optional[str] = None
    descripcion:     Optional[str] = None
    signos_vitales:  Optional[SignosVitales] = None


class PacienteResponse(BaseModel):
    id:                  int
    codigo_urgencia:     str
    nombre:              str
    apellidos:           str
    edad:                int
    dni:                 Optional[str]
    prioridad:           str
    motivo:              str
    descripcion:         Optional[str]
    area:                str
    estado:              str
    medico_asignado:     Optional[str]
    presion_sistolica:   Optional[int]
    presion_diastolica:  Optional[int]
    frecuencia_cardiaca: Optional[int]
    saturacion_o2:       Optional[float]
    temperatura:         Optional[float]
    frecuencia_resp:     Optional[int]
    hora_ingreso:        datetime
    hora_atencion:       Optional[datetime]
    hora_alta:           Optional[datetime]
    tiempo_espera_min:   Optional[int] = None

    model_config = {"from_attributes": True}


# ── RECURSO ──────────────────────────────────────────────────────────────────

class RecursoCreate(BaseModel):
    nombre:      str = Field(..., min_length=2, max_length=80)
    tipo:        str = Field(..., min_length=2, max_length=40)
    area:        Optional[str] = None
    total:       int = Field(..., ge=0)
    disponibles: int = Field(..., ge=0)

    @field_validator("disponibles")
    @classmethod
    def disponibles_lte_total(cls, v: int, info) -> int:
        total = info.data.get("total", 0)
        if v > total:
            raise ValueError("Disponibles no puede ser mayor que el total")
        return v


class RecursoUpdate(BaseModel):
    disponibles: Optional[int] = Field(None, ge=0)
    total:       Optional[int] = Field(None, ge=0)


class RecursoResponse(BaseModel):
    id:          int
    nombre:      str
    tipo:        str
    area:        Optional[str]
    total:       int
    disponibles: int
    ocupacion_pct: float = 0.0

    model_config = {"from_attributes": True}


# ── EVENTO ───────────────────────────────────────────────────────────────────

class EventoResponse(BaseModel):
    id:          int
    timestamp:   datetime
    tipo:        str
    descripcion: str
    paciente_id: Optional[int]
    usuario:     Optional[str]

    model_config = {"from_attributes": True}


# ── STATS / DASHBOARD ────────────────────────────────────────────────────────

class TriageStats(BaseModel):
    total_activos:    int
    por_prioridad:    dict[str, int]
    por_estado:       dict[str, int]
    por_area:         dict[str, int]
    tiempo_espera_promedio_min: float
    alertas:          list[str]
