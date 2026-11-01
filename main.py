from html import escape as html_escape
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
# MENU PRINCIPAL DE INSTITUCIONES
# ------------------------------------------

@app.get("/form/instituciones", response_class=HTMLResponse)
def instituciones_menu(request: Request, notice: str = ""):

    return templates.TemplateResponse(
        request=request,
        name="instituciones/menu.html",
        context={
            "request": request,
            "notice": notice
        }
    )


# ------------------------------------------
# REGISTRO DE RAEE INSTITUCIONAL
# ------------------------------------------

@app.get("/form/instituciones/registrar", response_class=HTMLResponse)
def registrar_institucion(request: Request, notice: str = ""):

    return templates.TemplateResponse(
        request=request,
        name="instituciones/registrar.html",
        context={
            "request": request,
            "notice": notice
        }
    )


@app.post("/form/instituciones/registrar")
def guardar_raee_institucional(
    equipment_type: str = Form(...),
    quantity: int = Form(...),
    condition: str = Form(...),
    origin: str = Form(...),
    registration_date: str = Form(...),
    characteristics: str = Form(""),
    generator_name: str = Form(...),
    document_number: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    address: str = Form(...)
):

    if quantity < 1:
        return RedirectResponse(
            url="/form/instituciones/registrar?notice=Cantidad+invalida",
            status_code=303
        )

    with connect() as conn:

        cursor = conn.execute("""
            INSERT INTO raee_records (
                equipment_type,
                quantity,
                condition,
                origin,
                registration_date,
                characteristics,
                generator_type,
                generator_name,
                document_number,
                phone,
                email,
                address,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            equipment_type,
            quantity,
            condition,
            origin,
            registration_date,
            characteristics,
            "Institución",
            generator_name,
            document_number,
            phone,
            email,
            address,
            "Registrado"
        ))

        record_id = cursor.lastrowid

    log_event(
        "info",
        f"Nuevo registro institucional RAEE #{record_id}: {equipment_type}"
    )

    return RedirectResponse(
        url="/form/instituciones/registrar?notice=RAEE+registrado+correctamente",
        status_code=303
    )


# ------------------------------------------
# GESTION DE BAJAS INSTITUCIONALES
# ------------------------------------------

@app.get("/form/instituciones/bajas", response_class=HTMLResponse)
def gestionar_bajas(request: Request, notice: str = ""):

    with connect() as conn:
        records = conn.execute("""
            SELECT *
            FROM raee_records
            WHERE generator_type = 'Institución'
            ORDER BY created_at DESC
        """).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="instituciones/bajas.html",
        context={
            "request": request,
            "records": records,
            "notice": notice
        }
    )


@app.post("/form/instituciones/bajas")
def actualizar_baja(
    record_id: int = Form(...),
    new_status: str = Form(...)
):

    allowed_statuses = [
        "Registrado",
        "Baja solicitada",
        "Baja aprobada",
        "En gestión",
        "Gestionado"
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Estado de baja no válido"
        )

    with connect() as conn:

        record = conn.execute("""
            SELECT id
            FROM raee_records
            WHERE id = ?
            AND generator_type = 'Institución'
        """, (record_id,)).fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Registro institucional no encontrado"
            )

        conn.execute("""
            UPDATE raee_records
            SET status = ?
            WHERE id = ?
            AND generator_type = 'Institución'
        """, (new_status, record_id))

    log_event(
        "info",
        f"Actualización del estado del registro institucional RAEE #{record_id}: {new_status}"
    )

    return RedirectResponse(
        url="/form/instituciones/bajas?notice=Estado+actualizado",
        status_code=303
    )


# ------------------------------------------
# INVENTARIO INSTITUCIONAL
# ------------------------------------------

@app.get("/form/instituciones/inventario", response_class=HTMLResponse)
def inventario_institucional(request: Request):

    with connect() as conn:

        records = conn.execute("""
            SELECT *
            FROM raee_records
            WHERE generator_type = 'Institución'
            ORDER BY created_at DESC
        """).fetchall()

        summary = conn.execute("""
            SELECT
                COUNT(*) AS total_registros,
                COALESCE(SUM(quantity), 0) AS total_equipos,
                COUNT(DISTINCT document_number) AS total_instituciones
            FROM raee_records
            WHERE generator_type = 'Institución'
        """).fetchone()

    return templates.TemplateResponse(
        request=request,
        name="instituciones/inventario.html",
        context={
            "request": request,
            "records": records,
            "summary": summary
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
    nit: str = Form(""),
    representante: str = Form(""),
    correo: str = Form(""),
    telefono: str = Form(""),
    ubicacion: str = Form(""),
    autorizaciones: str = Form(...),
    autoridad: str = Form(""),
    capacidad: float = Form(...),
    ocupado: float = Form(0),
    cobertura: str = Form(...),
    municipios: str = Form(""),
    servicios: str = Form(...)
):
    """Guarda una empresa gestora en la base de datos."""

    # Validar la capacidad operativa
    if capacidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La capacidad máxima debe ser mayor que cero."
        )

    if ocupado < 0:
        raise HTTPException(
            status_code=400,
            detail="La capacidad ocupada no puede ser negativa."
        )

    if ocupado > capacidad:
        raise HTTPException(
            status_code=400,
            detail="La capacidad ocupada no puede superar la capacidad máxima."
        )

    # Solo se considera autorizado si las autorizaciones están vigentes.
    authorized = 1 if autorizaciones == "Vigentes" else 0

    with connect() as conn:
        conn.execute("""
            INSERT INTO managers (
                name,
                raee_types,
                max_capacity_kg,
                occupied_kg,
                distance_km,
                authorized,
                address,
                zone_type,
                coordinate_source,
                nit,
                legal_representative,
                email,
                phone,
                authorization_status,
                environmental_authority,
                coverage,
                municipalities,
                main_service
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            empresa,
            json.dumps([]),
            capacidad,
            ocupado,
            0,
            authorized,
            ubicacion,
            "No clasificada",
            "pendiente",
            nit,
            representante,
            correo,
            telefono,
            autorizaciones,
            autoridad,
            cobertura,
            municipios,
            servicios
        ))

    log_event(
        "info",
        f"Nueva empresa gestora registrada: {empresa}"
    )
    
    return RedirectResponse(
        url="/form/gestor?notice=Empresa+registrada+correctamente",
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

# ==========================================
# MODULO DE GEOREFERENCIACION
# ==========================================

@app.get("/form/gestor/georreferenciacion", response_class=HTMLResponse)
def gestor_georreferenciacion(request: Request):

    with connect() as conn:

        containers = conn.execute("""
            SELECT id, name, location, latitude, longitude,
                   zone_type, coordinate_source
            FROM containers
            ORDER BY id
        """).fetchall()

        managers = conn.execute("""
            SELECT id, name, address, latitude, longitude,
                   zone_type, coordinate_source
            FROM managers
            ORDER BY id
        """).fetchall()

        delivery_points = conn.execute("""
            SELECT *
            FROM delivery_points
            WHERE active = 1
            ORDER BY id
        """).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="gestor/georreferenciacion.html",
        context={
            "request": request,
            "containers": [dict(c) for c in containers],
            "managers": [dict(m) for m in managers],
            "delivery_points": [dict(p) for p in delivery_points]
        }
    )


# ==========================================
# MODULO DE CIUDADANIA
# ==========================================

@app.get("/form/ciudadania", response_class=HTMLResponse)
def ciudadania_menu(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="ciudadania/menu.html",
        context={
            "request": request
        }
    )

@app.get("/form/ciudadania/registrar", response_class=HTMLResponse)
def ciudadania_registrar(request: Request, notice: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="ciudadania/registrar.html",
        context={
            "request": request,
            "notice": notice
        }
    )


@app.post("/form/ciudadania/registrar")
def ciudadania_registrar_submit(
    equipment_type: str = Form(...),
    quantity: int = Form(...),
    condition: str = Form(...),
    origin: str = Form(...),
    registration_date: str = Form(...),
    characteristics: str = Form(""),
    generator_type: str = Form(...),
    generator_name: str = Form(...),
    document_number: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    address: str = Form(...)
):
    if quantity < 1:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser de al menos una unidad."
        )

    with connect() as conn:
        cursor = conn.execute("""
            INSERT INTO raee_records (
                equipment_type,
                quantity,
                condition,
                origin,
                registration_date,
                characteristics,
                generator_type,
                generator_name,
                document_number,
                phone,
                email,
                address,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            equipment_type,
            quantity,
            condition,
            origin,
            registration_date,
            characteristics,
            generator_type,
            generator_name,
            document_number,
            phone,
            email,
            address,
            "Registrado"
        ))

        record_id = cursor.lastrowid

    log_event(
        "info",
        f"Nuevo registro RAEE #{record_id}: {equipment_type} ({quantity} unidad/es)"
    )
    
    return RedirectResponse(
        url="/form/ciudadania/registrar?notice=RAEE+registrado+correctamente",
        status_code=303
    )



# ==========================================
# CIUDADANIA - SOLICITUD DE RECOLECCION
# ==========================================

@app.get("/form/ciudadania/recoleccion", response_class=HTMLResponse)
def ciudadania_recoleccion(request: Request, notice: str = ""):

    with connect() as conn:
        records = conn.execute("""
            SELECT
                id,
                equipment_type,
                quantity,
                condition,
                origin,
                registration_date,
                generator_name,
                address,
                status
            FROM raee_records
            ORDER BY id DESC
        """).fetchall()

        requests = conn.execute("""
            SELECT
                p.id,
                p.raee_record_id,
                p.status,
                p.verification_status,
                p.created_at,
                r.equipment_type,
                r.quantity
            FROM pickup_requests p
            INNER JOIN raee_records r
                ON p.raee_record_id = r.id
            ORDER BY p.id DESC
        """).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="ciudadania/recoleccion.html",
        context={
            "request": request,
            "records": records,
            "requests": requests,
            "notice": notice
        }
    )


@app.post("/form/ciudadania/recoleccion")
def ciudadania_solicitar_recoleccion(
    record_id: int = Form(...)
):

    with connect() as conn:

        # 1. Verificar que el residuo exista.
        record = conn.execute("""
            SELECT id, equipment_type, quantity
            FROM raee_records
            WHERE id = ?
        """, (record_id,)).fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="El registro RAEE seleccionado no existe."
            )

        # 2. Evitar solicitudes pendientes duplicadas.
        existing_request = conn.execute("""
            SELECT id
            FROM pickup_requests
            WHERE raee_record_id = ?
            AND status IN ('Pendiente', 'En verificación', 'Asignada')
        """, (record_id,)).fetchone()

        if existing_request:
            return RedirectResponse(
                url="/form/ciudadania/recoleccion?notice=Este+residuo+ya+tiene+una+solicitud+activa",
                status_code=303
            )

        # 3. Crear la solicitud.
        cursor = conn.execute("""
            INSERT INTO pickup_requests (
                raee_record_id,
                status,
                verification_status
            )
            VALUES (?, ?, ?)
        """, (
            record_id,
            "Pendiente",
            "Pendiente"
        ))

        request_id = cursor.lastrowid

    # 4. Registrar actividad.
    log_event(
        "info",
        f"Solicitud de recolección #{request_id} creada para el registro RAEE #{record_id}"
    )

    return RedirectResponse(
        url="/form/ciudadania/recoleccion?notice=Solicitud+de+recoleccion+registrada+correctamente",
        status_code=303
    )

# ==========================================
# CIUDADANIA - CONSULTAR PUNTOS DE ENTREGA
# ==========================================

@app.get("/form/ciudadania/puntos", response_class=HTMLResponse)
def ciudadania_puntos(request: Request):

    with connect() as conn:
        points = conn.execute("""
            SELECT
                id,
                name,
                address,
                point_type,
                zone_type,
                latitude,
                longitude,
                coordinate_source,
                description
            FROM delivery_points
            WHERE active = 1
            ORDER BY name ASC
        """).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="ciudadania/puntos.html",
        context={
            "request": request,
            "points": points
        }
    )

# ==========================================
# MODULO DE FORO COMUNITARIO
# ==========================================


@app.get("/foro", response_class=HTMLResponse)
def foro_comunitario(request: Request):

    # Retrieve publications and their comment counts
    with connect() as conn:
        posts = conn.execute("""
            SELECT
                p.*,
                (
                    SELECT COUNT(*)
                    FROM community_comments c
                    WHERE c.post_id = p.id
                ) AS comment_count
            FROM community_posts p
            ORDER BY p.created_at DESC
        """).fetchall()

        # Retrieve all comments
        comments = conn.execute("""
            SELECT *
            FROM community_comments
            ORDER BY created_at ASC
        """).fetchall()

    # HTML template
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Foro comunitario | Ágora RAEE</title>

        <style>
            body {
                margin: 0;
                padding: 30px 20px;
                font-family: Arial, sans-serif;
                background: #f8f7fc;
                color: #35245c;
            }

            .forum-container {
                max-width: 950px;
                margin: 30px auto;
            }

            .forum-header, .forum-create, .forum-post {
                background: white;
                padding: 28px;
                margin-bottom: 22px;
                border-radius: 16px;
                box-shadow: 0 5px 25px rgba(0,0,0,.05);
            }

            h1, h2 {
                color: #6d28d9;
            }

            p {
                line-height: 1.6;
                color: #655b75;
            }

            label {
                display: block;
                margin: 14px 0 7px;
                font-weight: bold;
            }

            input, select, textarea {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                border: 1px solid #ded5ed;
                border-radius: 8px;
                font-size: 14px;
            }

            button, .forum-back {
                display: inline-block;
                margin-top: 18px;
                padding: 12px 20px;
                background: #6d28d9;
                color: white;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                cursor: pointer;
            }

            button:hover, .forum-back:hover {
                background: #5521a8;
            }

            .post-information {
                display: flex;
                flex-wrap: wrap;
                gap: 14px;
                font-size: 12px;
                color: #81758f;
                margin-top: 18px;
            }

            .post-category {
                color: #6d28d9;
                font-weight: bold;
                font-size: 13px;
            }

            .empty-message {
                text-align: center;
                padding: 30px;
            }

            .forum-comments {
                margin-top: 25px;
                padding-top: 20px;
                border-top: 1px solid #e8e0f2;
            }

            .forum-comments h3 {
                color: #6d28d9;
                font-size: 17px;
            }

            .forum-comment {
                background: #f8f5fd;
                border-left: 4px solid #9b72dc;
                padding: 14px;
                margin: 12px 0;
                border-radius: 8px;
            }

            .forum-comment p {
                margin-bottom: 0;
            }

            .comment-meta {
                font-size: 12px;
                color: #81758f;
            }
        </style>
    </head>

    <body>
        <main class="forum-container">

            <section class="forum-header">
                <p>ÁGORA RAEE · PARTICIPACIÓN COMUNITARIA</p>
                <h1>Foro comunitario</h1>

                <p>
                    Comparte experiencias, plantea inquietudes y construye
                    soluciones para la gestión responsable de residuos electrónicos.
                </p>

                <a href="/" class="forum-back">← Volver al inicio</a>
            </section>

            <section class="forum-create">
                <h2>Crear una publicación</h2>

                <form action="/foro/publicar" method="POST">

                    <label>Título</label>
                    <input type="text" name="title" maxlength="150" required>

                    <label>Categoría</label>
                    <select name="category" required>
                        <option value="">Seleccionar</option>
                        <option>Recolección</option>
                        <option>Educación ambiental</option>
                        <option>Campañas</option>
                        <option>Reutilización</option>
                        <option>Diagnóstico técnico</option>
                        <option>Dudas y sugerencias</option>
                    </select>

                    <label>Tipo de publicación</label>
                    <select name="post_type" required>
                        <option value="">Seleccionar</option>
                        <option>Pregunta</option>
                        <option>Debate</option>
                        <option>Iniciativa</option>
                        <option>Información</option>
                    </select>

                    <label>Nombre del participante</label>
                    <input type="text" name="author_name" maxlength="100" required>

                    <label>Perfil</label>
                    <select name="author_role" required>
                        <option value="">Seleccionar</option>
                        <option>Ciudadanía</option>
                        <option>Gestor</option>
                        <option>Institución</option>
                        <option>Técnico</option>
                    </select>

                    <label>Descripción</label>
                    <textarea name="description" rows="5" maxlength="3000" required></textarea>

                    <button type="submit">Publicar</button>
                </form>
            </section>

            <section>
                <h2>Publicaciones recientes</h2>
                {posts_html}
            </section>

        </main>
    </body>
    </html>
    """

    # Generate the HTML for publications
    posts_html = ""

    # Check whether there are publications
    if not posts:
        posts_html = """
        <div class="forum-post empty-message">
            <h3>Aún no hay publicaciones</h3>
            <p>¡Sé la primera persona en compartir una idea con la comunidad!</p>
        </div>
        """

    # Generate each publication
    for post in posts:

        safe_title = html_escape(post["title"])
        safe_category = html_escape(post["category"])
        safe_type = html_escape(post["post_type"])
        safe_description = html_escape(post["description"])
        safe_author = html_escape(post["author_name"])
        safe_role = html_escape(post["author_role"])
        safe_date = html_escape(post["created_at"])

        posts_html += f"""
        <article class="forum-post">

            <span class="post-category">{safe_category}</span>

            <h3>{safe_title}</h3>

            <p>{safe_description}</p>

            <div class="post-information">
                <span>Tipo: {safe_type}</span>
                <span>Publicado por: {safe_author}</span>
                <span>Perfil: {safe_role}</span>
                <span>Fecha: {safe_date}</span>
                <span>Comentarios: {post["comment_count"]}</span>
            </div>

            <section class="forum-comments">
                <h3>Comentarios</h3>
        """

        # Display comments belonging to this publication
        post_comments = [
            comment for comment in comments
            if comment["post_id"] == post["id"]
        ]

        if post_comments:

            for comment in post_comments:

                safe_comment_author = html_escape(comment["author_name"])
                safe_comment_role = html_escape(comment["author_role"])
                safe_comment_content = html_escape(comment["content"])
                safe_comment_date = html_escape(comment["created_at"])

                posts_html += f"""
                <div class="forum-comment">

                    <strong>{safe_comment_author}</strong>

                    <span class="comment-meta">
                        · {safe_comment_role} · {safe_comment_date}
                    </span>

                    <p>{safe_comment_content}</p>

                </div>
                """

        else:
            posts_html += """
            <p class="comment-meta">
                Todavía no hay comentarios. ¡Participa en la conversación!
            </p>
            """

        # Comment form
        posts_html += f"""
                <form action="/foro/comentar" method="POST">

                    <input
                        type="hidden"
                        name="post_id"
                        value="{post["id"]}"
                    >

                    <label>Nombre del participante</label>
                    <input
                        type="text"
                        name="author_name"
                        maxlength="100"
                        required
                    >

                    <label>Perfil</label>
                    <select name="author_role" required>
                        <option value="">Seleccionar</option>
                        <option>Ciudadanía</option>
                        <option>Gestor</option>
                        <option>Institución</option>
                        <option>Técnico</option>
                    </select>

                    <label>Escribe un comentario</label>
                    <textarea
                        name="content"
                        rows="3"
                        maxlength="2000"
                        required
                    ></textarea>

                    <button type="submit">Comentar</button>

                </form>

            </section>
        </article>
        """

    # Return the completed HTML page
    return HTMLResponse(html.replace("{posts_html}", posts_html))

    
@app.post("/foro/publicar")
def foro_publicar(
    title: str = Form(...),
    category: str = Form(...),
    post_type: str = Form(...),
    description: str = Form(...),
    author_name: str = Form(...),
    author_role: str = Form(...)
):
    title = title.strip()
    description = description.strip()
    author_name = author_name.strip()

    if not title or not description or not author_name:
        raise HTTPException(
            status_code=400,
            detail="Todos los campos son obligatorios."
        )

    allowed_categories = [
        "Recolección",
        "Educación ambiental",
        "Campañas",
        "Reutilización",
        "Diagnóstico técnico",
        "Dudas y sugerencias"
    ]

    allowed_types = [
        "Pregunta",
        "Debate",
        "Iniciativa",
        "Información"
    ]

    allowed_roles = [
        "Ciudadanía",
        "Gestor",
        "Institución",
        "Técnico"
    ]

    if category not in allowed_categories:
        raise HTTPException(status_code=400, detail="Categoría inválida.")

    if post_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo inválido.")

    if author_role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Perfil inválido.")

    with connect() as conn:
        conn.execute("""
            INSERT INTO community_posts (
                title,
                category,
                post_type,
                description,
                author_name,
                author_role
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            category,
            post_type,
            description,
            author_name,
            author_role
        ))

    return RedirectResponse(url="/foro", status_code=303)


    
@app.post("/foro/comentar")
def foro_comentar(
    post_id: int = Form(...),
    author_name: str = Form(...),
    author_role: str = Form(...),
    content: str = Form(...)
):
    # Clean input values
    author_name = author_name.strip()
    content = content.strip()

    # Allowed participant profiles
    allowed_roles = [
        "Ciudadanía",
        "Gestor",
        "Institución",
        "Técnico"
    ]

    # Validate required fields
    if not author_name or not content:
        raise HTTPException(
            status_code=400,
            detail="Nombre y comentario son obligatorios."
        )

    if post_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Publicación inválida."
        )

    if author_role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Perfil inválido."
        )

    if len(author_name) > 100 or len(content) > 2000:
        raise HTTPException(
            status_code=400,
            detail="El comentario supera la longitud permitida."
        )

    # Save comment in the database
    with connect() as conn:

        post = conn.execute(
            "SELECT id FROM community_posts WHERE id = ?",
            (post_id,)
        ).fetchone()

        if post is None:
            raise HTTPException(
                status_code=404,
                detail="Publicación no encontrada."
            )

        conn.execute("""
            INSERT INTO community_comments (
                post_id,
                author_name,
                author_role,
                content
            )
            VALUES (?, ?, ?, ?)
        """, (
            post_id,
            author_name,
            author_role,
            content
        ))

    # Return to the community forum
    return RedirectResponse(
        url="/foro",
        status_code=303
    )

