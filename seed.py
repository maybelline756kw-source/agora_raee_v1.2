
"""Datos de demostración de Ágora RAEE.
Las coordenadas son simuladas y sirven para probar el módulo geográfico.
"""

CONTAINERS = [
    {
        "id": 1,
        "name": "Punto RAEE — Campus",
        "location": "Sede educativa",
        "raee_type": "pequenos_electrodomesticos",
        "max_capacity_kg": 100.0,
        "occupied_kg": 35.0,
        "height_cm": 100.0,
        "distance_cm": 65.0,
        "latitude": 4.3370,
        "longitude": -74.3630,
        "zone_type": "Urbana",
        "coordinate_source": "demo"
    },
    {
        "id": 2,
        "name": "Punto RAEE — Centro comunitario",
        "location": "Centro comunitario",
        "raee_type": "computadores",
        "max_capacity_kg": 150.0,
        "occupied_kg": 105.0,
        "height_cm": 100.0,
        "distance_cm": 25.0,
        "latitude": 4.3400,
        "longitude": -74.3600,
        "zone_type": "Urbana",
        "coordinate_source": "demo"
    },
    {
        "id": 3,
        "name": "Punto RAEE — Vereda",
        "location": "Punto rural",
        "raee_type": "cables_y_accesorios",
        "max_capacity_kg": 80.0,
        "occupied_kg": 18.0,
        "height_cm": 100.0,
        "distance_cm": 78.0,
        "latitude": 4.3200,
        "longitude": -74.3900,
        "zone_type": "Rural",
        "coordinate_source": "demo"
    }
]


MANAGERS = [
    {
        "id": 1,
        "name": "Gestor autorizado Demo A",
        "raee_types": [
            "pequenos_electrodomesticos",
            "computadores"
        ],
        "max_capacity_kg": 200.0,
        "occupied_kg": 80.0,
        "distance_km": 8.0,
        "authorized": True,
        "address": "Ubicación demostrativa A",
        "latitude": 4.3450,
        "longitude": -74.3550,
        "zone_type": "Urbana",
        "coordinate_source": "demo"
    },
    {
        "id": 2,
        "name": "Gestor autorizado Demo B",
        "raee_types": [
            "computadores",
            "cables_y_accesorios"
        ],
        "max_capacity_kg": 120.0,
        "occupied_kg": 30.0,
        "distance_km": 14.0,
        "authorized": True,
        "address": "Ubicación demostrativa B",
        "latitude": 4.3150,
        "longitude": -74.3800,
        "zone_type": "Rural",
        "coordinate_source": "demo"
    },
    {
        "id": 3,
        "name": "Taller de aprovechamiento Demo C",
        "raee_types": ["cables_y_accesorios"],
        "max_capacity_kg": 50.0,
        "occupied_kg": 15.0,
        "distance_km": 4.0,
        "authorized": False,
        "address": "Ubicación demostrativa C",
        "latitude": 4.3300,
        "longitude": -74.3700,
        "zone_type": "Urbana",
        "coordinate_source": "demo"
    }
]


DELIVERY_POINTS = [
    {
        "name": "Centro de recepción RAEE",
        "address": "Punto demostrativo urbano",
        "point_type": "Recepción",
        "zone_type": "Urbana",
        "latitude": 4.3380,
        "longitude": -74.3610,
        "coordinate_source": "demo",
        "description": "Punto de recepción de residuos electrónicos."
    },
    {
        "name": "Punto de entrega comunitario",
        "address": "Punto demostrativo rural",
        "point_type": "Entrega",
        "zone_type": "Rural",
        "latitude": 4.3180,
        "longitude": -74.3850,
        "coordinate_source": "demo",
        "description": "Punto comunitario para la entrega de RAEE."
    }
]
