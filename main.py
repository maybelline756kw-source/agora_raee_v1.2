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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
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

@app.get("/api/status")
def api_status():
    containers = get_containers()
    return {"containers": containers, "count": len(containers),
            "critical_count": sum(c["status"] == "Crítico" for c in containers),
            "attention_count": sum(c["status"] == "Atención" for c in containers)}

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
