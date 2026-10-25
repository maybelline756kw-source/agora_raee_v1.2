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
