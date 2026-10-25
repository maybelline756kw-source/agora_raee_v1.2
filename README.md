# Agora RAEE — prototipo de baja fidelidad

Prototipo educativo para el Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de RAEE.

## Qué incluye
- Panel web con estado de contenedores.
- Simulador de lectura de sensor de distancia (inspirado en HC-SR04).
- Alertas por nivel de ocupación.
- Registro de solicitudes de recolección.
- Matching básico de gestores por tipo de RAEE y capacidad disponible.
- Registro de eventos y pruebas exploratorias.
- Persistencia SQLite local.

## Importante
Este proyecto usa datos simulados. No se conecta a Arduino/Tinkercad, Google Sheets ni a la aplicación de otra persona. Los umbrales y puntajes son configurables/ilustrativos y deben validarse contra la arquitectura unificada de la Etapa 3 antes de presentarlos como requisitos definitivos.

## Requisitos
Python 3.10 o superior recomendado.

## Ejecutar en Windows
1. Descomprime el ZIP.
2. Abre una terminal dentro de la carpeta `agora_raee`.
3. Crea un entorno virtual:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Instala dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
5. Inicia el servidor:
   ```powershell
   uvicorn app.main:app --reload
   ```
6. Abre http://127.0.0.1:8000 en tu navegador.

## API útil
- `GET /api/status`: resumen y contenedores.
- `POST /api/simulate/{container_id}`: genera una lectura simulada.
- `POST /api/requests/{container_id}`: crea solicitud de recolección y calcula matching.
- `GET /api/managers`: gestores de demostración.
- `GET /api/events`: eventos registrados.
- `POST /api/reset-demo`: reinicia los datos de demostración.

## Escenarios de prueba manual
1. Contenedor con ocupación normal.
2. Simular una nueva lectura para observar el cambio de ocupación.
3. Crear una solicitud de recolección y revisar gestores compatibles.
4. Revisar el comportamiento cuando no hay capacidad compatible (puede modificarse el archivo `app/seed.py`).
5. Revisar eventos desde el panel o `GET /api/events`.

## Limitaciones conocidas
- La simulación no mide distancia física real.
- El matching usa reglas sencillas de demostración, no una optimización de rutas real.
- No hay autenticación, roles, geolocalización real ni conexión a servicios externos.
- Antes de la entrega académica, contrastar los datos, indicadores y umbrales con el documento de Etapa 3 y documentar los resultados experimentales.
