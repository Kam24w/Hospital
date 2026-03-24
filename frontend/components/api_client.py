# frontend/components/api_client.py
"""
Cliente HTTP para comunicarse con el backend FastAPI.
Centraliza todas las llamadas a la API.
"""
import os
import requests
from typing import Optional

TIMEOUT     = 10  # segundos


def _normalize_url(url: str) -> str:
    return url.rstrip("/")


_env_backend = _normalize_url(os.getenv("BACKEND_URL", "http://localhost:8000"))
_candidate_backends = []
for _url in [_env_backend, "http://127.0.0.1:8000", "http://localhost:8000"]:
    if _url not in _candidate_backends:
        _candidate_backends.append(_url)

ACTIVE_BACKEND_URL = _candidate_backends[0]


def _request(method: str, endpoint: str, *, params: dict = None, data: dict = None, timeout: int = TIMEOUT):
    global ACTIVE_BACKEND_URL
    last_connection_error = None

    # Try active backend first, then fall back to alternatives.
    ordered_backends = [ACTIVE_BACKEND_URL] + [u for u in _candidate_backends if u != ACTIVE_BACKEND_URL]

    for backend_url in ordered_backends:
        api_base = f"{backend_url}/api/v1"
        try:
            response = requests.request(method, f"{api_base}{endpoint}", params=params, json=data, timeout=timeout)
            response.raise_for_status()
            ACTIVE_BACKEND_URL = backend_url
            return response
        except requests.exceptions.ConnectionError as exc:
            last_connection_error = exc
            continue

    raise requests.exceptions.ConnectionError(str(last_connection_error) if last_connection_error else "Sin conexión")


def _get(endpoint: str, params: dict = None) -> dict | list | None:
    try:
        r = _request("GET", endpoint, params=params)
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.HTTPError as e:
        return {"error": _format_http_error(e)}


def _format_http_error(e: requests.exceptions.HTTPError) -> str:
    if e.response is None:
        return str(e)
    try:
        payload = e.response.json()
    except Exception:
        return str(e)

    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, list):
        parts = []
        for item in detail:
            if isinstance(item, dict):
                loc = item.get("loc", [])
                field = ".".join(str(x) for x in loc[1:]) if len(loc) > 1 else "campo"
                msg = item.get("msg", "valor invalido")
                parts.append(f"{field}: {msg}")
        if parts:
            return " ; ".join(parts)
    if isinstance(detail, str):
        return detail
    return str(e)


def _post(endpoint: str, data: dict | None = None, params: dict | None = None) -> dict | None:
    try:
        r = _request("POST", endpoint, data=data, params=params)
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.HTTPError as e:
        return {"error": _format_http_error(e)}


def _patch(endpoint: str, data: dict) -> dict | None:
    try:
        r = _request("PATCH", endpoint, data=data)
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.HTTPError as e:
        return {"error": _format_http_error(e)}


def _delete(endpoint: str) -> bool:
    try:
        r = _request("DELETE", endpoint)
        return r.status_code == 204
    except Exception:
        return False


# ── PACIENTES ────────────────────────────────────────────────────────────────

def obtener_pacientes(
    activo: bool = True,
    prioridad: Optional[str] = None,
    estado: Optional[str] = None,
    area: Optional[str] = None,
) -> list[dict]:
    params = {"activo": activo}
    if prioridad: params["prioridad"] = prioridad
    if estado:    params["estado"]    = estado
    if area:      params["area"]      = area
    result = _get("/pacientes/", params)
    return result if isinstance(result, list) else []


def obtener_paciente(paciente_id: int) -> dict | None:
    result = _get(f"/pacientes/{paciente_id}")
    return result if result and "error" not in result else None


def admitir_paciente(datos: dict) -> dict | None:
    return _post("/pacientes/", datos)


def actualizar_paciente(paciente_id: int, cambios: dict) -> dict | None:
    return _patch(f"/pacientes/{paciente_id}", cambios)


def dar_alta_paciente(paciente_id: int) -> bool:
    return _delete(f"/pacientes/{paciente_id}")


# ── TRIAGE ───────────────────────────────────────────────────────────────────

def obtener_stats() -> dict | None:
    return _get("/triage/stats")


def obtener_eventos(limit: int = 20) -> list[dict]:
    result = _get("/triage/eventos", {"limit": limit})
    return result if isinstance(result, list) else []


def clasificar_automatico(
    edad: int,
    frecuencia_cardiaca: Optional[int] = None,
    saturacion_o2: Optional[float] = None,
    presion_sistolica: Optional[int] = None,
    temperatura: Optional[float] = None,
    frecuencia_resp: Optional[int] = None,
) -> dict | None:
    params = {"edad": edad}
    if frecuencia_cardiaca is not None: params["frecuencia_cardiaca"] = frecuencia_cardiaca
    if saturacion_o2       is not None: params["saturacion_o2"]       = saturacion_o2
    if presion_sistolica   is not None: params["presion_sistolica"]   = presion_sistolica
    if temperatura         is not None: params["temperatura"]         = temperatura
    if frecuencia_resp     is not None: params["frecuencia_resp"]     = frecuencia_resp
    return _post("/triage/clasificar", params=params)


# ── RECURSOS ─────────────────────────────────────────────────────────────────

def obtener_recursos() -> list[dict]:
    result = _get("/recursos/")
    return result if isinstance(result, list) else []


def actualizar_recurso(recurso_id: int, disponibles: int) -> dict | None:
    return _patch(f"/recursos/{recurso_id}", {"disponibles": disponibles})


# ── HEALTH ───────────────────────────────────────────────────────────────────

def backend_disponible() -> bool:
    global ACTIVE_BACKEND_URL
    candidates = [ACTIVE_BACKEND_URL] + [u for u in _candidate_backends if u != ACTIVE_BACKEND_URL]
    for backend_url in candidates:
        try:
            r = requests.get(f"{backend_url}/health", timeout=3)
            if r.status_code == 200:
                ACTIVE_BACKEND_URL = backend_url
                return True
        except Exception:
            continue
    return False
