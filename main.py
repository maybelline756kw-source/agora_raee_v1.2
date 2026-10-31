
from fastapi import FastAPI, Form, Request, HTTPException
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from database import connect, init_db
from seed import CONTAINERS, MANAGERS, DELIVERY_POINTS
from services import (
    get_containers,
    get_managers,
    get_events,
    get_requests,
    simulate_reading,
    create_request,
    log_event,
    matching
)


# ==========================================
# CONFIGURACION GENERAL
# ==========================================

BASE_DIR = Path(__file__).resolve().parent


# ==========================================
# INICIALIZACION DE DATOS DE DEMOSTRACION
# ==========================================

def seed_if_empty():
    """Inicializa la base de datos y agrega datos de demostración."""

    try:
        # Crear tablas y actualizar estructura de la BD
        init_db()

        with connect() as conn:

            # ----------------------------------
            # CONTENEDORES
            # ----------------------------------

            count = conn.execute(
                "SELECT COUNT(*) FROM containers"
            ).fetchone()[0]

            if count == 0:
                conn.executemany("""
                    INSERT INTO containers(
                        id,
                        name,
                        location,
                        raee_type,
                        max_capacity_kg,
                        occupied_kg,
                        height_cm,
                        distance_cm,
                        latitude,
                        longitude,
                        zone_type,
                        coordinate_source
                    )
                    VALUES(
                        :id,
                        :name,
                        :location,
                        :raee_type,
                        :max_capacity_kg,
                        :occupied_kg,
                        :height_cm,
                        :distance_cm,
                        :latitude,
                        :longitude,
                        :zone_type,
                        :coordinate_source
                    )
                """, CONTAINERS)

            # ----------------------------------
            # GESTORES
            # ----------------------------------

            managers_count = conn.execute(
                "SELECT COUNT(*) FROM managers"
            ).fetchone()[0]

            if managers_count == 0:
                for m in MANAGERS:
                    conn.execute("""
                        INSERT INTO managers(
                            id,
                            name,
                            raee_types,
                            max_capacity_kg,
                            occupied_kg,
                            distance_km,
                            authorized,
                            address,
                            latitude,
                            longitude,
                            zone_type,
                            coordinate_source
                        )
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        m["id"],
                        m["name"],
                        json.dumps(m["raee_types"]),
                        m["max_capacity_kg"],
                        m["occupied_kg"],
                        m["distance_km"],
                        int(m["authorized"]),
                        m["address"],
                        m["latitude"],
                        m["longitude"],
                        m["zone_type"],
                        m["coordinate_source"]
                    ))

            # ----------------------------------
            # PUNTOS DE ENTREGA
            # ----------------------------------

            points_count = conn.execute(
                "SELECT COUNT(*) FROM delivery_points"
            ).fetchone()[0]

            if points_count == 0:
                conn.executemany("""
                    INSERT INTO delivery_points(
                        name,
                        address,
                        point_type,
                        zone_type,
                        latitude,
                        longitude,
                        coordinate_source,
                        description
                    )
                    VALUES(
                        :name,
                        :address,
                        :point_type,
                        :zone_type,
                        :latitude,
                        :longitude,
                        :coordinate_source,
                        :description
                    )
                """, DELIVERY_POINTS)

            # ----------------------------------
            # COMPLETAR DATOS GEOGRAFICOS
            # DE REGISTROS ANTERIORES
            # ----------------------------------

            for c in CONTAINERS:
                conn.execute("""
                    UPDATE containers
                    SET latitude = ?,
                        longitude = ?,
                        zone_type = ?,
                        coordinate_source = ?
                    WHERE id = ?
                    AND latitude IS NULL
                """, (
                    c["latitude"],
                    c["longitude"],
                    c["zone_type"],
                    c["coordinate_source"],
                    c["id"]
                ))

            for m in MANAGERS:
                conn.execute("""
                    UPDATE managers
                    SET address = ?,
                        latitude = ?,
                        longitude = ?,
                        zone_type = ?,
                        coordinate_source = ?
                    WHERE id = ?
                    AND latitude IS NULL
                """, (
                    m["address"],
                    m["latitude"],
                    m["longitude"],
                    m["zone_type"],
                    m["coordinate_source"],
                    m["id"]
                ))

            conn.commit()

        print("Base de datos inicializada correctamente.")

    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")


# ==========================================
# CICLO DE VIDA DE FASTAPI
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_if_empty()
    yield


# ==========================================
# CREACION DE LA APLICACION
# ==========================================

app = FastAPI(
    title="Agora RAEE",
    description="Prototipo educativo de gestión comunitaria de RAEE",
    version="0.1.0",
    lifespan=lifespan
)


# ==========================================
# ARCHIVOS ESTATICOS Y PLANTILLAS
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, notice: str = ""):

    containers = get_containers()

    total = len(containers)

    critical = sum(
        1 for c in containers
        if c["status"] == "Crítico"
    )

    attention = sum(
        1 for c in containers
        if c["status"] == "Atención"
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "containers": containers,
            "managers": get_managers(),
            "events": get_events(8),
            "requests": get_requests(8),
            "total": total,
            "critical": critical,
            "attention": attention,
            "notice": notice
        }
    )


# ==========================================
# SIMULACION DE LECTURA DE CONTENEDORES
# ==========================================

@app.post("/simulate/{container_id}")
def simulate(container_id: int):

    result = simulate_reading(container_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contenedor no encontrado"
        )

    return RedirectResponse(
        url="/?notice=Lectura+simulada+registrada",
        status_code=303
    )


# ==========================================
# SOLICITUDES DE RECOLECCION
# ==========================================

@app.post("/requests/{container_id}")
def request_collection(container_id: int):

    result = create_request(container_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contenedor no encontrado"
        )

    return RedirectResponse(
        url="/?notice=Solicitud+de+recoleccion+procesada",
        status_code=303
    )


# ==========================================
# API: SIMULACION DE LECTURAS
# ==========================================

@app.post("/api/simulate/{container_id}")
def api_simulate(container_id: int):

    result = simulate_reading(container_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contenedor no encontrado"
        )

    return result


# ==========================================
# API: SOLICITUDES
# ==========================================

@app.post("/api/requests/{container_id}")
def api_request(container_id: int):

    result = create_request(container_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contenedor no encontrado"
        )

    return result


# ==========================================
# API: GESTORES
# ==========================================

@app.get("/api/managers")
def api_managers():
    return get_managers()


# ==========================================
# API: EVENTOS
# ==========================================

@app.get("/api/events")
def api_events():
    return get_events(100)


# ==========================================
# API: SOLICITUDES REGISTRADAS
# ==========================================

@app.get("/api/requests")
def api_requests():
    return get_requests(100)


# ==========================================
# REINICIAR DATOS DE DEMOSTRACION
# ==========================================

@app.post("/api/reset-demo")
def reset_demo():

    with connect() as conn:

        # Eliminar primero las rutas relacionadas
        conn.execute("DELETE FROM routes")

        # Eliminar los registros de demostración
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM collection_requests")
        conn.execute("DELETE FROM delivery_points")
        conn.execute("DELETE FROM containers")
        conn.execute("DELETE FROM managers")

        conn.commit()

    # Volver a insertar los datos de demostración
    seed_if_empty()

    log_event(
        "info",
        "Datos de demostración reiniciados manualmente."
    )

    return {
        "ok": True,
        "message": "Datos de demostración reiniciados."
    }


# ==========================================
# MODULO DE GESTORES
# ==========================================

# ------------------------------------------
# MENU PRINCIPAL DEL GESTOR
# ------------------------------------------

@app.get("/form/gestor", response_class=HTMLResponse)
def gestor_menu(request: Request, notice: str = ""):

    return templates.TemplateResponse(
        request=request,
        name="gestor/menu.html",
        context={
            "request": request,
            "notice": notice
        }
    )


# ------------------------------------------
# FORMULARIO DE REGISTRO DE GESTOR
# ------------------------------------------

@app.get("/form/gestor/registro", response_class=HTMLResponse)
def gestor_registro_form(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="gestor/registro.html",
        context={
            "request": request
        }
    )


# ------------------------------------------
# PROCESAMIENTO DEL REGISTRO
# ------------------------------------------

@app.post("/form/gestor/registro")
def gestor_registro_submit(
    empresa: str = Form(...),
    autorizaciones: str = Form(...),
    capacidad: float = Form(...),
    cobertura: str = Form(...),
    servicios: str = Form(...)
):

    # Actualmente el registro es una simulación.
    # La persistencia de empresas gestoras se implementará después.

    return RedirectResponse(
        url="/form/gestor?notice=Registro+de+empresa+exitoso",
        status_code=303
    )


# ------------------------------------------
# VISUALIZACION DE LOTES
# ------------------------------------------

@app.get("/form/gestor/lotes", response_class=HTMLResponse)
def gestor_lotes(request: Request):

    # Consultar los contenedores registrados
    containers = get_containers()

    lotes = []

    # Evaluar compatibilidad de cada lote
    for container in containers:

        matches = matching(container)

        compatible = any(
            manager["eligible"]
            for manager in matches
        )

        lotes.append({
            "id": container["id"],
            "nombre": container["name"],
            "tipo": container["raee_type"],
            "cantidad": container["occupied_kg"],
            "ubicacion": container["location"],
            "estado": container["status"],
            "compatible": compatible
        })

    # Calcular cantidad de lotes compatibles
    compatibles = sum(
        1 for lote in lotes
        if lote["compatible"]
    )

    return templates.TemplateResponse(
        request=request,
        name="gestor/lotes.html",
        context={
            "request": request,
            "lotes": lotes,
            "compatibles": compatibles,

            # Las postulaciones reales aún no están implementadas.
            "postulaciones": 0
        }
    )

# ==========================================
# MODULO DE RUTAS Y GEOREFERENCIACION
# ==========================================

@app.get("/form/gestor/rutas", response_class=HTMLResponse)
def gestor_rutas(request: Request):

    with connect() as conn:

        # Consultar contenedores con ubicación
        containers = conn.execute("""
            SELECT id, name, location, raee_type,
                   latitude, longitude, zone_type,
                   coordinate_source
            FROM containers
            ORDER BY id
        """).fetchall()

        # Consultar gestores con ubicación
        managers = conn.execute("""
            SELECT id, name, address, latitude,
                   longitude, zone_type, coordinate_source
            FROM managers
            ORDER BY id
        """).fetchall()

        # Consultar puntos de entrega
        delivery_points = conn.execute("""
            SELECT *
            FROM delivery_points
            WHERE active = 1
            ORDER BY id
        """).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="gestor/rutas.html",
        context={
            "request": request,
            "containers": [dict(c) for c in containers],
            "managers": [dict(m) for m in managers],
            "delivery_points": [dict(p) for p in delivery_points]
        }
    )

