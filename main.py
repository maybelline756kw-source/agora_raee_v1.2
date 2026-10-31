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
def ciudadania_registrar(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="ciudadania/registrar.html",
        context={"request": request}
    )
 

