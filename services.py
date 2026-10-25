from .database import connect
import json
import random

# Umbrales de demostración: confirmar con la arquitectura de Etapa 3.
WARNING_PERCENT = 60
CRITICAL_PERCENT = 85

def log_event(level: str, message: str):
    with connect() as conn:
        conn.execute("INSERT INTO events(level, message) VALUES (?, ?)", (level, message))
        conn.commit()

def get_containers():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM containers ORDER BY id").fetchall()
    result = []
    for row in rows:
        c = dict(row)
        c["occupancy_percent"] = round((c["occupied_kg"] / c["max_capacity_kg"]) * 100, 1)
        c["available_kg"] = round(c["max_capacity_kg"] - c["occupied_kg"], 1)
        c["status"] = status_for(c["occupancy_percent"])
        result.append(c)
    return result

def status_for(percent):
    if percent >= CRITICAL_PERCENT:
        return "Crítico"
    if percent >= WARNING_PERCENT:
        return "Atención"
    return "Normal"

def simulate_reading(container_id: int):
    with connect() as conn:
        row = conn.execute("SELECT * FROM containers WHERE id=?", (container_id,)).fetchone()
        if not row:
            return None
        c = dict(row)
        # Simulación: variar el nivel de llenado ±8 puntos porcentuales.
        current = c["occupied_kg"] / c["max_capacity_kg"]
        new_percent = max(0.0, min(1.0, current + random.uniform(-0.08, 0.12)))
        occupied = round(c["max_capacity_kg"] * new_percent, 1)
        # El sensor se representa como distancia desde la parte superior.
        distance = round(c["height_cm"] * (1 - new_percent), 1)
        conn.execute("UPDATE containers SET occupied_kg=?, distance_cm=? WHERE id=?",
                     (occupied, distance, container_id))
        conn.commit()
    pct = round(new_percent * 100, 1)
    level = "error" if pct >= CRITICAL_PERCENT else ("warning" if pct >= WARNING_PERCENT else "info")
    log_event(level, f"Lectura simulada para contenedor #{container_id}: {pct}% de ocupación.")
    if pct >= CRITICAL_PERCENT:
        log_event("critical", f"Contenedor #{container_id} alcanzó el umbral crítico.")
    return next((x for x in get_containers() if x["id"] == container_id), None)

def get_managers():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM managers ORDER BY id").fetchall()
    managers = []
    for row in rows:
        m = dict(row)
        m["raee_types"] = json.loads(m["raee_types"])
        m["available_kg"] = round(m["max_capacity_kg"] - m["occupied_kg"], 1)
        managers.append(m)
    return managers

def matching(container, requested_kg=None):
    # Reglas iniciales: tipo compatible, autorizado y capacidad suficiente.
    # Distancia se usa como criterio secundario de orden, no como ruta optimizada.
    requested_kg = requested_kg or max(1.0, container["occupied_kg"])
    candidates = []
    for manager in get_managers():
        compatible_type = container["raee_type"] in manager["raee_types"]
        enough_capacity = manager["available_kg"] >= requested_kg
        eligible = compatible_type and enough_capacity and bool(manager["authorized"])
        score = 0.0
        if eligible:
            # Puntaje demostrativo: 70% capacidad disponible normalizada + 30% cercanía.
            capacity_score = min(manager["available_kg"] / max(requested_kg, 1.0), 1.0)
            distance_score = 1.0 / (1.0 + manager["distance_km"])
            score = round(0.7 * capacity_score + 0.3 * distance_score, 3)
        candidates.append({
            **manager,
            "compatible_type": compatible_type,
            "enough_capacity": enough_capacity,
            "eligible": eligible,
            "score": score
        })
    return sorted(candidates, key=lambda m: (m["eligible"], m["score"]), reverse=True)

def create_request(container_id: int):
    container = next((c for c in get_containers() if c["id"] == container_id), None)
    if not container:
        return None
    requested_kg = max(1.0, container["occupied_kg"])
    matches = matching(container, requested_kg)
    selected = next((m for m in matches if m["eligible"]), None)
    status = "Asignada (simulada)" if selected else "Pendiente: sin gestor compatible"
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO collection_requests(container_id, requested_kg, status, matched_manager_id) VALUES (?, ?, ?, ?)",
            (container_id, requested_kg, status, selected["id"] if selected else None)
        )
        request_id = cur.lastrowid
        conn.commit()
    log_event("success" if selected else "warning",
              f"Solicitud #{request_id} para contenedor #{container_id}: {status}.")
    return {"id": request_id, "container": container, "requested_kg": requested_kg,
            "status": status, "selected": selected, "matches": matches}

def get_events(limit=30):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_requests(limit=20):
    with connect() as conn:
        rows = conn.execute("""
            SELECT r.*, c.name AS container_name, m.name AS manager_name
            FROM collection_requests r
            JOIN containers c ON c.id = r.container_id
            LEFT JOIN managers m ON m.id = r.matched_manager_id
            ORDER BY r.id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]
