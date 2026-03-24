# Sistema de Triage y Flujo de Sala de Urgencias

## Arquitectura

```
triage_system/
├── backend/                    # FastAPI (Python)
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── database/
│   │   └── db.py               # SQLite + SQLAlchemy
│   └── routers/
│       ├── patients.py         # CRUD pacientes
│       ├── triage.py           # Lógica de triage
│       └── resources.py        # Gestión de recursos
│
├── frontend/                   # Streamlit (Python)
│   ├── app.py                  # App principal
│   ├── pages/
│   │   ├── 1_Dashboard.py      # Panel principal
│   │   ├── 2_Admision.py       # Admitir pacientes
│   │   ├── 3_Cola_Triage.py    # Cola por prioridad
│   │   └── 4_Recursos.py       # Gestión recursos
│   └── components/
│       ├── api_client.py       # Llamadas al backend
│       └── ui_helpers.py       # Componentes UI reutilizables
│
├── shared/
│   └── constants.py            # Constantes compartidas
│
├── requirements.txt
├── .env.example
└── README.md
```

## Instalación y Ejecución

### Opción rápida en Windows 
Desde la raíz del proyecto:

```powershell
pip install -r requirements.txt
.\run.ps1
```

Puertos por defecto:
- Backend: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- Frontend: http://127.0.0.1:8501

Si quieres cambiar puertos:

```powershell
.\run.ps1 -BackendPort 8001 -FrontendPort 8502
```

### Opción manual (dos terminales)

1. Instalar dependencias

```powershell
pip install -r requirements.txt
```

2. Backend (terminal 1)

```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

3. Frontend (terminal 2)

```powershell
cd frontend
python -m streamlit run app.py
```

Nota: si aparece "No se puede conectar al backend", verifica que el backend responda en:

http://127.0.0.1:8000/health

## Tecnologías
- **Frontend**: Streamlit 1.32+
- **Backend**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy
- **Base de Datos**: SQLite (dev) / PostgreSQL (prod)
- **Validación**: Pydantic v2
- **HTTP Client**: httpx (async)
