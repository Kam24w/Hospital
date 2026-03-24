# backend/routers/patients.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.db import get_db, PacienteORM, EventoORM
from models.schemas import PacienteCreate, PacienteUpdate, PacienteResponse

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def _generar_codigo(db: Session) -> str:
    """Genera el siguiente código URG-XXX correlativo."""
    ultimo = (
        db.query(PacienteORM)
        .order_by(PacienteORM.id.desc())
        .first()
    )
    siguiente = (ultimo.id + 1) if ultimo else 1
    return f"URG-{siguiente:03d}"


def _calcular_espera(paciente: PacienteORM) -> Optional[int]:
    if paciente.estado == "en_espera":
        delta = datetime.utcnow() - paciente.hora_ingreso
        return int(delta.total_seconds() / 60)
    return None


def _orm_to_response(p: PacienteORM) -> PacienteResponse:
    data = PacienteResponse.model_validate(p)
    data.tiempo_espera_min = _calcular_espera(p)
    return data


# ── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[PacienteResponse], summary="Listar pacientes")
def listar_pacientes(
    activo:    bool           = Query(True,  description="Solo pacientes activos"),
    prioridad: Optional[str]  = Query(None,  description="Filtrar por prioridad P1–P5"),
    estado:    Optional[str]  = Query(None,  description="Filtrar por estado"),
    area:      Optional[str]  = Query(None,  description="Filtrar por área"),
    db:        Session        = Depends(get_db),
):
    q = db.query(PacienteORM).filter(PacienteORM.activo == activo)
    if prioridad:
        q = q.filter(PacienteORM.prioridad == prioridad)
    if estado:
        q = q.filter(PacienteORM.estado == estado)
    if area:
        q = q.filter(PacienteORM.area == area)
    # Ordenar: prioridad ASC (P1 primero), luego hora ingreso ASC
    q = q.order_by(PacienteORM.prioridad.asc(), PacienteORM.hora_ingreso.asc())
    return [_orm_to_response(p) for p in q.all()]


@router.get("/{paciente_id}", response_model=PacienteResponse, summary="Detalle de paciente")
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    p = db.query(PacienteORM).filter(PacienteORM.id == paciente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return _orm_to_response(p)


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED,
             summary="Admitir nuevo paciente")
def admitir_paciente(payload: PacienteCreate, db: Session = Depends(get_db)):
    nuevo = PacienteORM(
        codigo_urgencia = _generar_codigo(db),
        nombre          = payload.nombre,
        apellidos       = payload.apellidos,
        edad            = payload.edad,
        dni             = payload.dni,
        prioridad       = payload.prioridad,
        motivo          = payload.motivo,
        descripcion     = payload.descripcion,
        area            = payload.area,
        medico_asignado = payload.medico_asignado,
        estado          = "en_espera",
        hora_ingreso    = datetime.utcnow(),
    )
    if payload.signos_vitales:
        sv = payload.signos_vitales
        nuevo.presion_sistolica   = sv.presion_sistolica
        nuevo.presion_diastolica  = sv.presion_diastolica
        nuevo.frecuencia_cardiaca = sv.frecuencia_cardiaca
        nuevo.saturacion_o2       = sv.saturacion_o2
        nuevo.temperatura         = sv.temperatura
        nuevo.frecuencia_resp     = sv.frecuencia_resp

    db.add(nuevo)
    db.flush()  # Obtener ID antes del commit

    evento = EventoORM(
        tipo        = "admision",
        descripcion = f"{nuevo.codigo_urgencia} admitido — {nuevo.motivo}",
        paciente_id = nuevo.id,
    )
    db.add(evento)
    db.commit()
    db.refresh(nuevo)
    return _orm_to_response(nuevo)


@router.patch("/{paciente_id}", response_model=PacienteResponse, summary="Actualizar paciente")
def actualizar_paciente(
    paciente_id: int,
    payload: PacienteUpdate,
    db: Session = Depends(get_db),
):
    p = db.query(PacienteORM).filter(PacienteORM.id == paciente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    changes = []

    if payload.prioridad is not None and payload.prioridad != p.prioridad:
        changes.append(f"prioridad {p.prioridad}→{payload.prioridad}")
        p.prioridad = payload.prioridad

    if payload.estado is not None and payload.estado != p.estado:
        changes.append(f"estado {p.estado}→{payload.estado}")
        if payload.estado == "en_atencion" and not p.hora_atencion:
            p.hora_atencion = datetime.utcnow()
        if payload.estado == "alta" and not p.hora_alta:
            p.hora_alta = datetime.utcnow()
        p.estado = payload.estado

    if payload.area is not None:
        p.area = payload.area
    if payload.medico_asignado is not None:
        p.medico_asignado = payload.medico_asignado
    if payload.descripcion is not None:
        p.descripcion = payload.descripcion

    if payload.signos_vitales:
        sv = payload.signos_vitales
        if sv.presion_sistolica   is not None: p.presion_sistolica   = sv.presion_sistolica
        if sv.presion_diastolica  is not None: p.presion_diastolica  = sv.presion_diastolica
        if sv.frecuencia_cardiaca is not None: p.frecuencia_cardiaca = sv.frecuencia_cardiaca
        if sv.saturacion_o2       is not None: p.saturacion_o2       = sv.saturacion_o2
        if sv.temperatura         is not None: p.temperatura         = sv.temperatura
        if sv.frecuencia_resp     is not None: p.frecuencia_resp     = sv.frecuencia_resp
        changes.append("signos vitales actualizados")

    if changes:
        evento = EventoORM(
            tipo        = "cambio_estado",
            descripcion = f"{p.codigo_urgencia}: {', '.join(changes)}",
            paciente_id = p.id,
        )
        db.add(evento)

    db.commit()
    db.refresh(p)
    return _orm_to_response(p)


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Dar de alta / eliminar")
def dar_alta(paciente_id: int, db: Session = Depends(get_db)):
    p = db.query(PacienteORM).filter(PacienteORM.id == paciente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    p.activo    = False
    p.estado    = "alta"
    p.hora_alta = datetime.utcnow()
    evento = EventoORM(
        tipo        = "alta",
        descripcion = f"{p.codigo_urgencia} dado de alta",
        paciente_id = p.id,
    )
    db.add(evento)
    db.commit()
