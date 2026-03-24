#!/bin/bash
# start.sh — Inicia backend y frontend en paralelo

echo "Iniciando Sistema de Triage..."
echo ""

# Crear .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Archivo .env creado desde .env.example"
fi

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt -q

echo ""
echo "─────────────────────────────────────────"
echo "  BACKEND  → http://localhost:8000"
echo "  FRONTEND → http://localhost:8501"
echo "  API DOCS → http://localhost:8000/docs"
echo "─────────────────────────────────────────"
echo ""

# Levantar backend en background
echo "Iniciando Backend (FastAPI)..."
cd backend && uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Esperar a que el backend esté listo
sleep 2

# Levantar frontend
echo "Iniciando Frontend (Streamlit)..."
cd frontend && streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "Sistema iniciado. Presiona Ctrl+C para detener."

# Manejar Ctrl+C
trap "echo ''; echo 'Deteniendo sistema...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait
