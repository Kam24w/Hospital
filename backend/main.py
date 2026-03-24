# backend/main.py
"""
Sistema de Triage — Backend FastAPI
Punto de entrada principal.

Ejecución:
    uvicorn main:app --reload --port 8000
"""
import sys
import os

# Permitir imports relativos desde /backend
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routers import patients, triage, resources

# ── APP ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sistema de Triage — API",
    description=(
        "API REST para el Sistema de Triage y Flujo de Sala de Urgencias.\n\n"
        "Gestiona pacientes, prioridades, recursos hospitalarios y registro de eventos."
    ),
    version="2.4.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (permite que Streamlit llame al backend en dev) ──────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ──────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(patients.router,  prefix=API_PREFIX)
app.include_router(triage.router,    prefix=API_PREFIX)
app.include_router(resources.router, prefix=API_PREFIX)

# ── EVENTOS ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    """Inicializa la BD y carga datos de semilla en el primer arranque."""
    print("Iniciando Sistema de Triage - Backend")
    init_db()
    print("Base de datos lista")


@app.get("/", tags=["Health"])
def root():
    return {
        "servicio": "Sistema de Triage API",
        "version": "2.4.1",
        "estado": "activo",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
