# Ágora RAEE — Prototipo de baja fidelidad

Prototipo educativo del **Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de Residuos de Aparatos Eléctricos y Electrónicos (RAEE)**.

Ágora RAEE busca facilitar la articulación entre puntos de recolección, gestores y comunidades, mediante herramientas de registro, seguimiento, compatibilidad y gestión logística de residuos electrónicos.

El proyecto se desarrolla como un prototipo web de baja fidelidad, orientado a validar funcionalidades y explorar posibles soluciones para la gestión comunitaria de RAEE.

## 1. Funcionalidades principales

### Dashboard y monitoreo

- Panel web para consultar el estado de los contenedores.
- Visualización de niveles de ocupación y capacidad disponible.
- Simulación de lecturas de sensores de distancia, inspirada en el funcionamiento del HC-SR04.
- Clasificación de los niveles de ocupación mediante alertas.
- Registro de eventos y actividades del sistema.

### Gestión de solicitudes

- Creación de solicitudes de recolección de RAEE.
- Consulta del historial de solicitudes.
- Evaluación de compatibilidad entre contenedores y gestores.
- Matching básico considerando el tipo de RAEE, la capacidad disponible y la autorización del gestor.

### Módulo de gestores

El sistema incorpora un espacio de gestión orientado al actor Gestor, con las siguientes secciones:

- **Registro de empresa:** formulario para ingresar información de empresas gestoras.
- **Gestión de lotes:** consulta de contenedores y evaluación de compatibilidad con gestores.
- **Rutas de gestión:** consulta de contenedores, gestores y puntos de entrega asociados a la logística de recolección.
- **Georreferenciación:** consulta de ubicaciones, coordenadas y clasificación territorial de los puntos registrados.

### Gestión geográfica

Se incorpora una estructura de datos preparada para trabajar con ubicaciones geográficas:

- Coordenadas de contenedores y gestores.
- Registro de puntos de recolección y entrega.
- Clasificación de zonas rurales y urbanas.
- Identificación del origen de las coordenadas mediante los campos `demo` y `real`.
- Estructura para registrar rutas y sus respectivos estados.

El modelo geográfico utiliza inicialmente datos demostrativos y permite incorporar ubicaciones reales posteriormente.

## 2. Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| Python | Lenguaje principal |
| FastAPI | Desarrollo del backend y servicios web |
| SQLite | Persistencia de información |
| HTML5 | Estructura de las interfaces |
| CSS3 | Diseño y presentación visual |
| Jinja2 | Renderizado de plantillas dinámicas |
| Uvicorn | Servidor de desarrollo |

## 3. Estructura general del proyecto

```text
AGORA_RAEE/
│
├── main.py
├── database.py
├── seed.py
├── services.py
├── requirements.txt
│
├── data/
│   └── agora_raee.db
│
├── templates/
│   ├── index.html
│   │
│   └── gestor/
│       ├── menu.html
│       ├── registro.html
│       ├── lotes.html
│       ├── rutas.html
│       └── georreferenciacion.html
│
└── static/
    └── styles.css
```

**Descripción de los archivos principales:**

- `main.py`: configura la aplicación FastAPI, inicializa los datos y define las rutas web y los endpoints de la API.
- `database.py`: establece la conexión SQLite y define la estructura de las tablas.
- `seed.py`: contiene los datos de demostración utilizados para inicializar el sistema.
- `services.py`: implementa la lógica de negocio, el matching, las solicitudes, las simulaciones y el registro de eventos.
- `templates/`: contiene las interfaces HTML del dashboard y del módulo de gestores.
- `static/`: almacena los recursos de diseño, como las hojas de estilo CSS.
- `data/`: almacena la base de datos local cuando se ejecuta en un entorno convencional.

## 4. Requisitos

- Python 3.10 o superior recomendado.
- pip.
- Navegador web actualizado.
- Conexión a internet únicamente si se incorporan recursos externos que la requieran.

Las dependencias del proyecto se encuentran definidas en `requirements.txt`.

## 5. Instalación y ejecución en Windows

1. Descargar o descomprimir el proyecto.
2. Abrir una terminal dentro de la carpeta raíz `AGORA_RAEE`.
3. Crear un entorno virtual:

```bash
py -m venv .venv
```

4. Activar el entorno virtual:

```bash
.venv\Scripts\activate
```

5. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

6. Iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

## 6. Rutas principales de la aplicación

### Interfaces web

| Ruta | Descripción |
|---|---|
| `/` | Dashboard principal |
| `/form/gestor` | Menú principal del Gestor |
| `/form/gestor/registro` | Formulario de registro de empresa |
| `/form/gestor/lotes` | Consulta y compatibilidad de lotes |
| `/form/gestor/rutas` | Módulo de rutas de gestión |
| `/form/gestor/georreferenciacion` | Consulta de ubicaciones geográficas |

### API

| Método | Endpoint | Funcionalidad |
|---|---|---|
| POST | `/api/simulate/{container_id}` | Genera una lectura simulada |
| POST | `/api/requests/{container_id}` | Crea una solicitud y ejecuta el matching |
| GET | `/api/managers` | Consulta los gestores registrados |
| GET | `/api/events` | Consulta los eventos del sistema |
| GET | `/api/requests` | Consulta las solicitudes de recolección |
| POST | `/api/reset-demo` | Reinicia los datos de demostración |

## 7. Base de datos

El sistema utiliza SQLite para almacenar la información y facilitar la persistencia local.

Las principales tablas contempladas son:

- `containers`: información de los contenedores RAEE, capacidad, ocupación y ubicación.
- `managers`: información de gestores, tipos de residuos aceptados, capacidad y autorización.
- `events`: registro de eventos y alertas.
- `collection_requests`: solicitudes de recolección.
- `delivery_points`: puntos de recepción y entrega.
- `routes`: registro de recorridos y estados asociados.

La estructura geográfica contempla campos como:

- `latitude`: latitud.
- `longitude`: longitud.
- `zone_type`: clasificación de zona rural o urbana.
- `coordinate_source`: origen de las coordenadas (`demo` o `real`).

La inicialización de la base de datos se realiza mediante `init_db()` y la carga de información demostrativa mediante `seed_if_empty()`.

## 8. Escenarios de prueba manual

1. Consultar el dashboard y verificar los contenedores disponibles.
2. Simular una nueva lectura y observar los cambios en los niveles de ocupación.
3. Generar una solicitud de recolección.
4. Verificar la compatibilidad de los gestores según el tipo de RAEE, la capacidad disponible y la autorización.
5. Consultar los eventos registrados.
6. Ingresar al módulo de Gestores y navegar por sus diferentes secciones.
7. Consultar los lotes y verificar los resultados de compatibilidad.
8. Consultar las ubicaciones de contenedores, gestores y puntos de entrega.
9. Verificar la clasificación de los puntos según su zona rural o urbana.
10. Ejecutar el reinicio de los datos de demostración y comprobar su inicialización nuevamente.

## 9. Limitaciones conocidas y consideraciones

- Las lecturas de sensores son simuladas y no representan mediciones físicas reales.
- El sistema no cuenta actualmente con conexión física a Arduino ni integración con Tinkercad.
- El matching utiliza reglas básicas de compatibilidad y no representa un algoritmo avanzado de optimización.
- Las coordenadas utilizadas inicialmente son demostrativas y no deben interpretarse como ubicaciones verificadas.
- El módulo de georreferenciación permite consultar datos geográficos, pero todavía requiere la integración de un mapa interactivo.
- El módulo de rutas contempla la estructura de almacenamiento y consulta de información logística; el cálculo de recorridos reales y la optimización de rutas están pendientes de desarrollo.
- El registro de empresas gestoras y las postulaciones a lotes todavía no cuentan con persistencia funcional completa.
- No se ha implementado autenticación ni control de acceso por roles.
- No existe integración con servicios externos de geolocalización, mapas o navegación.

Los umbrales, indicadores y puntajes utilizados son ilustrativos y deben contrastarse con la arquitectura unificada de la Etapa 3 antes de considerarse requisitos definitivos.

## 10. Proyección del proyecto

Como parte de su evolución, Ágora RAEE contempla:

- Integración de ubicaciones geográficas reales.
- Incorporación de mapas interactivos.
- Cálculo de distancias y planificación de recorridos.
- Fortalecimiento del matching entre gestores y lotes.
- Implementación de registros persistentes para empresas y postulaciones.
- Integración futura con dispositivos de medición y servicios externos.
- Validación de funcionalidades frente a los requerimientos de la arquitectura unificada.

---

**Ágora RAEE — Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de RAEE.**

*Prototipo académico de desarrollo incremental.*
