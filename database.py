import os
import sqlite3
from pathlib import Path

# Si estamos en Vercel, usamos /tmp; si estamos en local, usamos la carpeta data
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/agora_raee.db")
else:
    DB_PATH = Path(__file__).resolve().parent / "data" / "agora_raee.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
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
        conn.commit()


        # ==========================================
        # CAMPOS GEOGRAFICOS PARA CONTENEDORES
        # ==========================================

        container_columns = {
            "latitude": "REAL",
            "longitude": "REAL",
            "zone_type": "TEXT DEFAULT 'No clasificada'",
            "coordinate_source": "TEXT DEFAULT 'demo'"
        }

        for column, definition in container_columns.items():
            existing = [
                row["name"]
                for row in conn.execute("PRAGMA table_info(containers)")
            ]

            if column not in existing:
                conn.execute(
                    f"ALTER TABLE containers ADD COLUMN {column} {definition}"
                )

        # ==========================================
        # CAMPOS GEOGRAFICOS PARA GESTORES
        # ==========================================

        manager_columns = {
            "address": "TEXT",
            "latitude": "REAL",
            "longitude": "REAL",
            "zone_type": "TEXT DEFAULT 'No clasificada'",
            "coordinate_source": "TEXT DEFAULT 'demo'"
        }

        for column, definition in manager_columns.items():
            existing = [
                row["name"]
                for row in conn.execute("PRAGMA table_info(managers)")
            ]

            if column not in existing:
                conn.execute(
                    f"ALTER TABLE managers ADD COLUMN {column} {definition}"
                )

        # ==========================================
        # TABLA DE PUNTOS DE ENTREGA
        # ==========================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS delivery_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                point_type TEXT NOT NULL,
                zone_type TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                coordinate_source TEXT NOT NULL DEFAULT 'demo',
                description TEXT,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ==========================================
        # TABLA DE RUTAS
        # ==========================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_id INTEGER NOT NULL,
                delivery_point_id INTEGER,
                manager_id INTEGER,
                distance_km REAL,
                status TEXT NOT NULL DEFAULT 'Pendiente',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (container_id) REFERENCES containers(id),
                FOREIGN KEY (delivery_point_id) REFERENCES delivery_points(id),
                FOREIGN KEY (manager_id) REFERENCES managers(id)
            )
        """)

        conn.commit()

