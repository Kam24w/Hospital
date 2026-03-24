# backend/routers/resources.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db, RecursoORM, EventoORM
from models.schemas import RecursoCreate, RecursoUpdate, RecursoResponse

router = APIRouter(prefix="/recursos", tags=["Recursos"])


def _to_response(r: RecursoORM) -> RecursoResponse:
    ocupados = r.total - r.disponibles
    pct = round((ocupados / r.total * 100), 1) if r.total > 0 else 0.0
    return RecursoResponse(
        id=r.id, nombre=r.nombre, tipo=r.tipo, area=r.area,
        total=r.total, disponibles=r.disponibles, ocupacion_pct=pct
    )


@router.get("/", response_model=list[RecursoResponse], summary="Listar recursos")
def listar_recursos(db: Session = Depends(get_db)):
    recursos = db.query(RecursoORM).filter(RecursoORM.activo == True).all()
    return [_to_response(r) for r in recursos]


@router.post("/", response_model=RecursoResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear recurso")
def crear_recurso(payload: RecursoCreate, db: Session = Depends(get_db)):
    nuevo = RecursoORM(**payload.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return _to_response(nuevo)


@router.patch("/{recurso_id}", response_model=RecursoResponse, summary="Actualizar disponibilidad")
def actualizar_recurso(
    recurso_id: int,
    payload: RecursoUpdate,
    db: Session = Depends(get_db),
):
    r = db.query(RecursoORM).filter(RecursoORM.id == recurso_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")

    if payload.total is not None:
        r.total = payload.total
    if payload.disponibles is not None:
        if payload.disponibles > r.total:
            raise HTTPException(
                status_code=400,
                detail=f"Disponibles ({payload.disponibles}) no puede superar el total ({r.total})"
            )
        r.disponibles = payload.disponibles

    evento = EventoORM(
        tipo        = "recurso",
        descripcion = f"Recurso '{r.nombre}': {r.disponibles}/{r.total} disponibles",
    )
    db.add(evento)
    db.commit()
    db.refresh(r)
    return _to_response(r)
