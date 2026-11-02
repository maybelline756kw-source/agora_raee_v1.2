import os
import sqlite3
from pathlib import Path


# ==========================================
# CONFIGURACION DE LA BASE DE DATOS
# ==========================================

if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/agora_raee.db")
else:
    DB_PATH = Path(__file__).resolve().parent / "data" / "agora_raee.db"


def connect():
    """Abre una conexión con SQLite y permite acceder a las filas por nombre."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def add_missing_columns(conn, table_name, columns):
    """
    Agrega columnas que todavía no existen en una tabla.
    Permite actualizar la estructura sin borrar los registros existentes.
    """
    existing_columns = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table_name})")
    }

    for column, definition in columns.items():
        if column not in existing_columns:
            conn.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column} {definition}"
            )


# ==========================================
# INICIALIZACION Y MIGRACIONES
# ==========================================

def init_db():
    """Crea las tablas del sistema y aplica migraciones necesarias."""

    with connect() as conn:

        # ----------------------------------
        # TABLA: CONTAINERS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS containers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                raee_type TEXT NOT NULL,
                max_capacity_kg REAL NOT NULL,
                occupied_kg REAL NOT NULL,
                height_cm REAL NOT NULL,
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

        # ----------------------------------
        # TABLA: RAEE_RECORDS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS raee_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                equipment_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                condition TEXT NOT NULL,
                origin TEXT NOT NULL,
                registration_date TEXT NOT NULL,

                characteristics TEXT,

                generator_type TEXT NOT NULL,
                generator_name TEXT NOT NULL,
                document_number TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'Registrado',

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

                # ----------------------------------
        # TABLA: PICKUP_REQUESTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS pickup_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raee_record_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendiente',
                verification_status TEXT NOT NULL DEFAULT 'Pendiente',
                matched_manager_id INTEGER,
                route_id INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (raee_record_id)
                    REFERENCES raee_records(id),

                FOREIGN KEY (matched_manager_id)
                    REFERENCES managers(id),

                FOREIGN KEY (route_id)
                    REFERENCES routes(id)
            )
        """)

        
        # ----------------------------------
        # TABLA: TECHNICAL_REQUESTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS technical_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                applicant_name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                justification TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'Pendiente',

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # ----------------------------------
        # TABLA: COMMUNITY_POSTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS community_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                post_type TEXT NOT NULL,
                description TEXT NOT NULL,
                author_name TEXT NOT NULL,
                author_role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Recibida',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------
        # TABLA: COMMUNITY_COMMENTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS community_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                author_role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (post_id)
                    REFERENCES community_posts(id)
                    ON DELETE CASCADE
            )
        """)

                # ----------------------------------
        # TABLA: CITIZEN_REPORTS
        # ----------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS citizen_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Recibido',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    print("Estructura de la base de datos verificada correctamente.")

