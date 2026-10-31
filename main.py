from fastapi import FastAPI, Form, Request, Depends
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from database import connect, init_db
from seed import CONTAINERS, MANAGERS
from services import (
    get_containers, get_managers, get_events, get_requests,
    simulate_reading, create_request, log_event
)

# --- RUTA BASE ABSOLUTA ---
BASE_DIR = Path(__file__).resolve().parent

def seed_if_empty():
    try:
        init_db()
        with connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM containers").fetchone()[0]
            if count == 0:
                conn.executemany("""
                    INSERT INTO containers(id,name,location,raee_type,max_capacity_kg,occupied_kg,height_cm,distance_cm)
                    VALUES(:id,:name,:location,:raee_type,:max_capacity_kg,:occupied_kg,:height_cm,:distance_cm)
                """, CONTAINERS)
                for m in MANAGERS:
                    conn.execute("""
                        INSERT INTO managers(id,name,raee_types,max_capacity_kg,occupied_kg,distance_km,authorized)
                        VALUES(?,?,?,?,?,?,?)
                    """, (m["id"], m["name"], json.dumps(m["raee_types"]), m["max_capacity_kg"],
                          m["occupied_kg"], m["distance_km"], int(m["authorized"])))
                conn.commit()
                log_event("info", "Datos de demostración inicializados.")
    except Exception as e:
        print(f"Error inicializando BD: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_if_empty()
    yield

app = FastAPI(title="Agora RAEE", description="Prototipo educativo de gestión comunitaria de RAEE", version="0.1.0", lifespan=lifespan)

# --- AQUÍ ESTÁ EL CAMBIO CLAVE (Rutas Absolutas con BASE_DIR) ---
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, notice: str = ""):
    containers = get_containers()
    total = len(containers)
    critical = sum(1 for c in containers if c["status"] == "Crítico")
    attention = sum(1 for c in containers if c["status"] == "Atención")
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, "containers": containers, "managers": get_managers(),
        "events": get_events(8), "requests": get_requests(8),
        "total": total, "critical": critical, "attention": attention, "notice": notice
    })

@app.post("/simulate/{container_id}")
def simulate(container_id: int):
    result = simulate_reading(container_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return RedirectResponse(url="/?notice=Lectura+simulada+registrada", status_code=303)

@app.post("/requests/{container_id}")
def request_collection(container_id: int):
    result = create_request(container_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return RedirectResponse(url="/?notice=Solicitud+de+recoleccion+procesada", status_code=303)

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, notice: str = ""):
    seed_if_empty()  # Asegura que la BD existe e incluye datos demo
    containers = get_containers()
    total = len(containers)
    critical = sum(1 for c in containers if c["status"] == "Crítico")
    attention = sum(1 for c in containers if c["status"] == "Atención")
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, "containers": containers, "managers": get_managers(),
        "events": get_events(8), "requests": get_requests(8),
        "total": total, "critical": critical, "attention": attention, "notice": notice
    })

@app.post("/api/simulate/{container_id}")
def api_simulate(container_id: int):
    result = simulate_reading(container_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return result

@app.post("/api/requests/{container_id}")
def api_request(container_id: int):
    result = create_request(container_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return result

@app.get("/api/managers")
def api_managers():
    return get_managers()

@app.get("/api/events")
def api_events():
    return get_events(100)

@app.get("/api/requests")
def api_requests():
    return get_requests(100)

@app.post("/api/reset-demo")
def reset_demo():
    with connect() as conn:
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM collection_requests")
        conn.execute("DELETE FROM containers")
        conn.execute("DELETE FROM managers")
        conn.commit()
    seed_if_empty()
    log_event("info", "Datos de demostración reiniciados manualmente.")
    return {"ok": True, "message": "Datos de demostración reiniciados."}


# ==========================================
# NUEVAS RUTAS: MÓDULO DE GESTORES
# ==========================================

@app.get("/form/gestor", response_class=HTMLResponse)
def gestor_menu(request: Request):
    """Menú principal para el rol de Gestor."""
    return templates.TemplateResponse(request=request, name="gestor_menu.html", context={"request": request})

@app.get("/form/gestor/registro", response_class=HTMLResponse)
def gestor_registro_form(request: Request):
    """Formulario de registro de datos de la empresa gestora."""
    return templates.TemplateResponse(request=request, name="gestor_registro.html", context={"request": request})

@app.post("/form/gestor/registro")
def gestor_registro_submit(
    empresa: str = Form(...),
    autorizaciones: str = Form(...),
    capacidad: float = Form(...),
    cobertura: str = Form(...),
    servicios: str = Form(...)
):
    """Procesa el registro del gestor y lo guarda o simula."""
    # Aquí puedes agregar lógica para guardar en base de datos si lo deseas
    return RedirectResponse(url="/form/gestor?notice=Registro+de+empresa+exitoso", status_code=303)

@app.get("/form/gestor/lotes", response_class=HTMLResponse)
def gestor_lotes(request: Request):
    """Vista de lotes asignados, actor responsable, compatibilidad y capacidad."""
    # Puedes pasar datos reales de tus contenedores/gestores aquí
    return templates.TemplateResponse(request=request, name="gestor_lotes.html", context={"request": request, "managers": get_managers(), "containers": get_containers()})

@app.get("/form/gestor/rutas", response_class=HTMLResponse)
def gestor_rutas(request: Request):
    """Determinación de rutas de gestión (reparar, reutilizar, aprovechar, disponer)."""
    return templates.TemplateResponse(request=request, name="gestor_rutas.html", context={"request": request})

@app.get("/form/gestor/georreferenciacion", response_class=HTMLResponse)
def gestor_georreferenciacion(request: Request):
    """Georreferenciación logística, distancia y clasificación rural/urbana."""
    return templates.TemplateResponse(request=request, name="gestor_geo.html", context={"request": request, "containers": get_containers()})
