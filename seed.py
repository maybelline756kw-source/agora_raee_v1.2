"""Datos de demostración. Ajustar según la arquitectura acordada en Etapa 3."""

CONTAINERS = [
    {"id": 1, "name": "Punto RAEE — Campus", "location": "Sede educativa", "raee_type": "pequenos_electrodomesticos",
     "max_capacity_kg": 100.0, "occupied_kg": 35.0, "height_cm": 100.0, "distance_cm": 65.0},
    {"id": 2, "name": "Punto RAEE — Centro comunitario", "location": "Centro comunitario", "raee_type": "computadores",
     "max_capacity_kg": 150.0, "occupied_kg": 105.0, "height_cm": 100.0, "distance_cm": 25.0},
    {"id": 3, "name": "Punto RAEE — Vereda", "location": "Punto rural", "raee_type": "cables_y_accesorios",
     "max_capacity_kg": 80.0, "occupied_kg": 18.0, "height_cm": 100.0, "distance_cm": 78.0},
]

MANAGERS = [
    {"id": 1, "name": "Gestor autorizado Demo A", "raee_types": ["pequenos_electrodomesticos", "computadores"],
     "max_capacity_kg": 200.0, "occupied_kg": 80.0, "distance_km": 8.0, "authorized": True},
    {"id": 2, "name": "Gestor autorizado Demo B", "raee_types": ["computadores", "cables_y_accesorios"],
     "max_capacity_kg": 120.0, "occupied_kg": 30.0, "distance_km": 14.0, "authorized": True},
    {"id": 3, "name": "Taller de aprovechamiento Demo C", "raee_types": ["cables_y_accesorios"],
     "max_capacity_kg": 50.0, "occupied_kg": 15.0, "distance_km": 4.0, "authorized": False},
]
