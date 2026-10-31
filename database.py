                   distance_cm REAL NOT NULL
            )
        """)

        # Agregar datos geográficos a contenedores existentes.
        add_missing_columns(conn, "containers", {
            "latitude": "REAL",
            "longitude": "REAL",
            "zone_type": "TEXT DEFAULT 'No clasificada'",
            "coordinate_source": "TEXT DEFAULT 'demo'"
        })

        # ----------------------------------
        # TABLA: MANAGERS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS managers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                raee_types TEXT NOT NULL,
                max_capacity_kg REAL NOT NULL,
                occupied_kg REAL NOT NULL,
                distance_km REAL NOT NULL,
                authorized INTEGER NOT NULL
            )
        """)

        # Datos geográficos de los gestores.
        add_missing_columns(conn, "managers", {
            "address": "TEXT",
            "latitude": "REAL",
            "longitude": "REAL",
            "zone_type": "TEXT DEFAULT 'No clasificada'",
            "coordinate_source": "TEXT DEFAULT 'demo'"
        })

        # Datos institucionales del formulario de registro.
        # Estas columnas permiten guardar la información enviada desde
        # templates/gestor/registro.html y procesada en main.py.
        add_missing_columns(conn, "managers", {
            "nit": "TEXT",
            "legal_representative": "TEXT",
            "email": "TEXT",
            "phone": "TEXT",
            "authorization_status": "TEXT",
            "environmental_authority": "TEXT",
            "coverage": "TEXT",
            "municipalities": "TEXT",
            "main_service": "TEXT"
        })

        # ----------------------------------
        # TABLA: EVENTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        # ----------------------------------
        # TABLA: COLLECTION_REQUESTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS collection_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_id INTEGER NOT NULL,
                requested_kg REAL NOT NULL,
                status TEXT NOT NULL,
                matched_manager_id INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------
        # TABLA: DELIVERY_POINTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS delivery_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                point_type TEXT NOT NULL,
                zone_type TEXT NOT NULL DEFAULT 'No clasificada',
                latitude REAL,
                longitude REAL,
                coordinate_source TEXT NOT NULL DEFAULT 'demo',
                description TEXT,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Asegurar columnas si la tabla existía desde una versión anterior.
        add_missing_columns(conn, "delivery_points", {
            "zone_type": "TEXT DEFAULT 'No clasificada'",
            "latitude": "REAL",
            "longitude": "REAL",
            "coordinate_source": "TEXT DEFAULT 'demo'",
            "description": "TEXT",
            "active": "INTEGER NOT NULL DEFAULT 1"
        })

        # ----------------------------------
        # TABLA: ROUTES
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_id INTEGER NOT NULL,
                delivery_point_id INTEGER NOT NULL,
                manager_id INTEGER,
                distance_km REAL,
                status TEXT NOT NULL DEFAULT 'Pendiente',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    print("Estructura de la base de datos verificada correctamente.")
