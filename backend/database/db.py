# backend/database/db.py
import os
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, DateTime,
    Boolean, Text, Enum as SAEnum, create_engine
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./triage.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ── MODELOS ORM ──────────────────────────────────────────────────────────────

class PacienteORM(Base):
    __tablename__ = "pacientes"

    id              = Column(Integer, primary_key=True, index=True)
    codigo_urgencia = Column(String(20), unique=True, index=True, nullable=False)
    nombre          = Column(String(120), nullable=False)
    apellidos       = Column(String(120), nullable=False)
    edad            = Column(Integer, nullable=False)
    dni             = Column(String(20), nullable=True)
    prioridad       = Column(String(5), nullable=False, default="P3")
    motivo          = Column(String(200), nullable=False)
    descripcion     = Column(Text, nullable=True)
    area            = Column(String(60), nullable=False)
    estado          = Column(String(30), nullable=False, default="en_espera")
    medico_asignado = Column(String(120), nullable=True)
    # Signos vitales
    presion_sistolica   = Column(Integer, nullable=True)
    presion_diastolica  = Column(Integer, nullable=True)
    frecuencia_cardiaca = Column(Integer, nullable=True)
    saturacion_o2       = Column(Float, nullable=True)
    temperatura         = Column(Float, nullable=True)
    frecuencia_resp     = Column(Integer, nullable=True)
    # Tiempos
    hora_ingreso    = Column(DateTime, default=datetime.utcnow, nullable=False)
    hora_atencion   = Column(DateTime, nullable=True)
    hora_alta       = Column(DateTime, nullable=True)
    activo          = Column(Boolean, default=True)


class RecursoORM(Base):
    __tablename__ = "recursos"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(80), nullable=False)
    tipo        = Column(String(40), nullable=False)   # cama, personal, equipo, sala
    area        = Column(String(60), nullable=True)
    total       = Column(Integer, nullable=False, default=0)
    disponibles = Column(Integer, nullable=False, default=0)
    activo      = Column(Boolean, default=True)


class EventoORM(Base):
    __tablename__ = "eventos"

    id          = Column(Integer, primary_key=True, index=True)
    timestamp   = Column(DateTime, default=datetime.utcnow, nullable=False)
    tipo        = Column(String(40), nullable=False)   # admision, alta, cambio_estado, etc.
    descripcion = Column(Text, nullable=False)
    paciente_id = Column(Integer, nullable=True)
    usuario     = Column(String(80), nullable=True, default="sistema")


# ── UTILIDADES ───────────────────────────────────────────────────────────────

def get_db():
    """Dependency para FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas y carga datos iniciales si la BD está vacía."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_data(db)
    finally:
        db.close()


def _seed_data(db: Session):
    """Datos de muestra para desarrollo."""
    if db.query(RecursoORM).count() > 0:
        return  # Ya tiene datos

    recursos_seed = [
        RecursoORM(nombre="Camas UCI",        tipo="cama",     area="UCI",        total=8,  disponibles=2),
        RecursoORM(nombre="Camas Urgencias",  tipo="cama",     area="General",    total=20, disponibles=6),
        RecursoORM(nombre="Sala Trauma",      tipo="sala",     area="Trauma",     total=4,  disponibles=3),
        RecursoORM(nombre="Quirófano",        tipo="sala",     area="Cirugía",    total=3,  disponibles=0),
        RecursoORM(nombre="Médicos Guardia",  tipo="personal", area="General",    total=12, disponibles=5),
        RecursoORM(nombre="Enfermeros",       tipo="personal", area="General",    total=20, disponibles=8),
        RecursoORM(nombre="Ventiladores",     tipo="equipo",   area="UCI",        total=6,  disponibles=2),
        RecursoORM(nombre="Desfibriladores",  tipo="equipo",   area="Shock Room", total=4,  disponibles=2),
    ]
    db.add_all(recursos_seed)

    pacientes_seed = [
        PacienteORM(
            codigo_urgencia="URG-001", nombre="Carlos", apellidos="García Morales",
            edad=67, prioridad="P1", motivo="IAM Sospechoso",
            descripcion="Dolor torácico opresivo irradiado a brazo izquierdo. ECG con elevación ST.",
            area="Shock Room", estado="en_atencion",
            presion_sistolica=160, presion_diastolica=100,
            frecuencia_cardiaca=110, saturacion_o2=92.0, temperatura=37.2, frecuencia_resp=22,
        ),
        PacienteORM(
            codigo_urgencia="URG-002", nombre="Ana", apellidos="Rodríguez Pérez",
            edad=45, prioridad="P1", motivo="TCE Severo",
            descripcion="Traumatismo craneoencefálico tras accidente de tráfico. GCS 9.",
            area="Trauma", estado="en_atencion",
            presion_sistolica=145, presion_diastolica=90,
            frecuencia_cardiaca=95, saturacion_o2=97.0, temperatura=36.8, frecuencia_resp=18,
        ),
        PacienteORM(
            codigo_urgencia="URG-003", nombre="Miguel", apellidos="López Torres",
            edad=72, prioridad="P1", motivo="ACV Isquémico",
            descripcion="Hemiparesia izquierda brusca. Afasia. Inicio síntomas hace 90 min.",
            area="Neurología", estado="en_atencion",
            presion_sistolica=180, presion_diastolica=110,
            frecuencia_cardiaca=88, saturacion_o2=89.0, temperatura=37.5, frecuencia_resp=20,
        ),
        PacienteORM(
            codigo_urgencia="URG-004", nombre="Elena", apellidos="Martínez Ruiz",
            edad=38, prioridad="P2", motivo="Fractura Fémur",
            descripcion="Caída desde altura. Deformidad en muslo derecho. Dolor severo.",
            area="Trauma", estado="en_espera",
            presion_sistolica=120, presion_diastolica=78,
            frecuencia_cardiaca=102, saturacion_o2=98.0, temperatura=36.6, frecuencia_resp=16,
        ),
        PacienteORM(
            codigo_urgencia="URG-005", nombre="José", apellidos="Sánchez Villa",
            edad=54, prioridad="P2", motivo="Disnea Aguda",
            descripcion="Disnea de reposo. Crepitantes bilaterales. Edemas en MMII.",
            area="General", estado="en_espera",
            presion_sistolica=140, presion_diastolica=88,
            frecuencia_cardiaca=115, saturacion_o2=88.0, temperatura=36.9, frecuencia_resp=28,
        ),
        PacienteORM(
            codigo_urgencia="URG-006", nombre="Laura", apellidos="Hernández Cruz",
            edad=29, prioridad="P3", motivo="Dolor Abdominal",
            descripcion="Dolor en fosa iliaca derecha. Nauseas. Signo de Blumberg positivo.",
            area="General", estado="en_espera",
            presion_sistolica=118, presion_diastolica=74,
            frecuencia_cardiaca=96, saturacion_o2=99.0, temperatura=38.1, frecuencia_resp=18,
        ),
        PacienteORM(
            codigo_urgencia="URG-007", nombre="Pedro", apellidos="Jiménez Ramos",
            edad=61, prioridad="P3", motivo="Crisis HTA",
            descripcion="Cefalea intensa + HTA severa. 220/130 mmHg. Sin focalidad neurológica.",
            area="Cardiología", estado="en_observacion",
            presion_sistolica=220, presion_diastolica=130,
            frecuencia_cardiaca=82, saturacion_o2=97.0, temperatura=36.7, frecuencia_resp=16,
        ),
    ]
    db.add_all(pacientes_seed)

    eventos_seed = [
        EventoORM(tipo="admision",      descripcion="URG-001 admitido — IAM Sospechoso",       paciente_id=1),
        EventoORM(tipo="admision",      descripcion="URG-002 admitido — TCE Severo",            paciente_id=2),
        EventoORM(tipo="admision",      descripcion="URG-003 admitido — ACV Isquémico",         paciente_id=3),
        EventoORM(tipo="cambio_estado", descripcion="URG-003 alerta: SpO₂ < 90%",              paciente_id=3),
        EventoORM(tipo="recurso",       descripcion="Nueva camilla UCI disponible"),
        EventoORM(tipo="admision",      descripcion="URG-007 admitido — Crisis HTA",            paciente_id=7),
    ]
    db.add_all(eventos_seed)
    db.commit()
