# PowerShell script para ejecutar el Sistema de Triage en Windows
# Uso:
#   .\run.ps1
# Opcional:
#   .\run.ps1 -BackendPort 8000 -FrontendPort 8501

param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 8501
)

$ErrorActionPreference = "Stop"
$backendProcess = $null

function Cleanup {
    if ($null -ne $backendProcess -and -not $backendProcess.HasExited) {
        Write-Host "Deteniendo backend (PID $($backendProcess.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
    }
}

try {
    $projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $projectRoot

    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  SISTEMA DE TRIAGE - Arranque local" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""

    if (!(Test-Path ".env") -and (Test-Path ".env.example")) {
        Copy-Item ".env.example" ".env"
        Write-Host "OK: Archivo .env creado desde .env.example" -ForegroundColor Green
    }

    Write-Host "Iniciando backend en puerto $BackendPort..." -ForegroundColor Yellow
    $backendProcess = Start-Process python -ArgumentList @("-m", "uvicorn", "main:app", "--reload", "--port", "$BackendPort") -WorkingDirectory (Join-Path $projectRoot "backend") -PassThru

    $healthOk = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Milliseconds 600
        try {
            $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 2
            if ($health.StatusCode -eq 200) {
                $healthOk = $true
                break
            }
        }
        catch {
            # Esperar siguiente intento
        }
    }

    if (-not $healthOk) {
        throw "No fue posible iniciar backend en http://127.0.0.1:$BackendPort. Revisa si el puerto esta ocupado."
    }

    Write-Host "OK: Backend activo  http://127.0.0.1:$BackendPort" -ForegroundColor Green
    Write-Host "OK: API Docs       http://127.0.0.1:$BackendPort/docs" -ForegroundColor Green
    Write-Host ""

    Write-Host "Iniciando frontend en puerto $FrontendPort..." -ForegroundColor Yellow
    Set-Location (Join-Path $projectRoot "frontend")
    python -m streamlit run app.py --server.port $FrontendPort
}
catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Cleanup
    Write-Host ""
    Write-Host "Proceso finalizado." -ForegroundColor Cyan
}
