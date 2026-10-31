# Ágora RAEE — Prototipo de baja fidelidad

**Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de Residuos de Aparatos Eléctricos y Electrónicos (RAEE).**

Ágora RAEE es un prototipo web orientado a facilitar la articulación entre gestores, puntos de entrega y comunidades mediante herramientas de registro, seguimiento, compatibilidad y gestión logística de residuos de aparatos eléctricos y electrónicos (RAEE).

El proyecto busca explorar soluciones tecnológicas que contribuyan a mejorar la gestión comunitaria de estos residuos, promoviendo la conexión entre los actores involucrados en su recolección, aprovechamiento, reutilización y disposición final.

Se desarrolla como un prototipo educativo de baja fidelidad, con un enfoque incremental que permite validar funcionalidades y explorar la viabilidad de los procesos propuestos.

---

## 1. Funcionalidades principales

### 1.1. Dashboard y monitoreo

- Panel web para consultar el estado de los contenedores.
- Visualización de niveles de ocupación y capacidad disponible.
- Simulación de lecturas de sensores de distancia, inspirada en el funcionamiento del sensor HC-SR04.
- Clasificación de niveles de ocupación mediante alertas.
- Registro de eventos y actividades del sistema.

### 1.2. Módulo de ciudadanía

El sistema incorpora un espacio orientado a la participación ciudadana en la gestión de residuos RAEE.

**Registro de residuos:**
- Formulario para registrar aparatos eléctricos y electrónicos en desuso.
- Captura del tipo de equipo, cantidad, condición, procedencia y fecha de registro.
- Registro de características del residuo.
- Captura de información del generador, incluyendo nombre, documento, teléfono, correo y dirección.
- Almacenamiento de los registros en la base de datos SQLite.

**Solicitud de recolección:**
- Consulta de residuos previamente registrados.
- Selección de residuos para iniciar una solicitud de recolección.
- Verificación de existencia del registro seleccionado.
- Prevención de solicitudes activas duplicadas para un mismo registro.
- Almacenamiento de solicitudes con estado inicial pendiente.
- Consulta del historial y estado de las solicitudes generadas.

**Consulta de puntos de entrega:**
- Consulta de puntos de entrega registrados y activos.
- Visualización de nombre, dirección, tipo de punto y clasificación territorial.
- Consulta de descripciones y coordenadas geográficas cuando están disponibles.

### 1.3. Gestión de solicitudes

- Creación de solicitudes de recolección.
- Consulta del historial de solicitudes.
- Evaluación de compatibilidad entre contenedores y gestores.
- Matching básico considerando el tipo de RAEE, la capacidad disponible y la autorización del gestor.
- Registro de estados y eventos asociados a las solicitudes.

### 1.4. Módulo de gestores

El sistema incorpora un espacio de gestión orientado al actor Gestor, con las siguientes secciones:

**Registro de empresa:**
- Formulario para ingresar información institucional de empresas gestoras.
- Captura de NIT, representante legal, correo, teléfono y ubicación.
- Registro del estado de autorización ambiental.
- Registro de autoridad ambiental, cobertura territorial, municipios y servicios ofrecidos.
- Almacenamiento de la información institucional en SQLite.

**Gestión de lotes:**
- Consulta de contenedores.
- Evaluación de compatibilidad entre lotes y gestores.
- Consulta de capacidad y disponibilidad.

**Rutas de gestión:**
- Consulta de contenedores, gestores y puntos de entrega asociados a la logística de recolección.
- Estructura para registrar recorridos y sus respectivos estados.

**Georreferenciación:**
- Consulta de ubicaciones y coordenadas.
- Visualización de información territorial.
- Clasificación de zonas rurales y urbanas.
- Identificación del origen de las coordenadas.

### 1.5. Gestión geográfica

Se incorpora una estructura de datos preparada para trabajar con ubicaciones geográficas:

- Coordenadas de contenedores y gestores.
- Registro de puntos de recolección y entrega.
- Clasificación de zonas rurales y urbanas.
- Identificación del origen de las coordenadas mediante los campos `demo` y `real`.
- Estructura para registrar rutas y sus respectivos estados.

El modelo geográfico utiliza inicialmente datos demostrativos y permite incorporar ubicaciones reales posteriormente.

---

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

---

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
│   ├── gestor/
│   │   ├── menu.html
│   │   ├── registro.html
│   │   ├── lotes.html
│   │   ├── rutas.html
│   │   └── georreferenciacion.html
│   │
│   └── ciudadania/
│       ├── menu.html
│       ├── registrar.html
│       ├── recoleccion.html
│       └── puntos.html
│
├── static/
│   └── styles.css
```

### Descripción de los archivos principales

- **main.py:** configura la aplicación FastAPI, inicializa los datos y define las rutas web y los endpoints de la API.
- **database.py:** establece la conexión SQLite, define las tablas y ejecuta las migraciones necesarias para actualizar la estructura de la base de datos.
- **seed.py:** contiene los datos de demostración utilizados para inicializar el sistema.
- **services.py:** implementa la lógica de negocio, el matching, las solicitudes, las simulaciones y el registro de eventos.
- **templates/:** contiene las interfaces HTML del dashboard y los módulos de gestores y ciudadanía.
- **static/:** almacena los recursos de diseño, como las hojas de estilo CSS.
- **data/:** almacena la base de datos local cuando se ejecuta en un entorno convencional.

---

## 4. Requisitos

- Python 3.10 o superior recomendado.
- pip.
- Navegador web actualizado.
- Conexión a internet únicamente si se incorporan recursos externos que la requieran.

Las dependencias del proyecto se encuentran definidas en `requirements.txt`.

---

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

7. Abrir el navegador en:

```text
http://127.0.0.1:8000
```

---

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
| `/form/ciudadania` | Menú principal de Ciudadanía |
| `/form/ciudadania/registrar` | Registro de residuos RAEE |
| `/form/ciudadania/recoleccion` | Solicitud y consulta de recolecciones |
| `/form/ciudadania/puntos` | Consulta de puntos de entrega |

### API

| Método | Endpoint | Funcionalidad |
|---|---|---|
| POST | `/api/simulate/{container_id}` | Genera una lectura simulada |
| POST | `/api/requests/{container_id}` | Crea una solicitud y ejecuta el matching |
| GET | `/api/managers` | Consulta los gestores registrados |
| GET | `/api/events` | Consulta los eventos del sistema |
| GET | `/api/requests` | Consulta las solicitudes de recolección |
| POST | `/api/reset-demo` | Reinicia los datos de demostración |

Las rutas de interfaz de ciudadanía utilizan operaciones web independientes para registrar residuos, generar solicitudes y consultar puntos de entrega.

---

## 7. Base de datos

El sistema utiliza SQLite para almacenar la información y facilitar la persistencia local.

Las principales tablas contempladas son:

| Tabla | Descripción |
|---|---|
| `containers` | Información de contenedores RAEE, capacidad, ocupación y ubicación. |
| `managers` | Información de gestores, tipos de residuos aceptados, capacidad, autorización y datos institucionales. |
| `events` | Registro de eventos y alertas del sistema. |
| `collection_requests` | Solicitudes de recolección asociadas a contenedores. |
| `delivery_points` | Puntos de recepción y entrega. |
| `routes` | Registro de recorridos y estados asociados. |
| `raee_records` | Información de los residuos registrados por la ciudadanía. |
| `pickup_requests` | Solicitudes de recolección asociadas a registros ciudadanos. |

### Estructura geográfica

La información geográfica contempla campos como:

- `latitude`: latitud.
- `longitude`: longitud.
- `zone_type`: clasificación territorial, rural o urbana.
- `coordinate_source`: origen de las coordenadas, demostrativo o real.

### Inicialización y actualización

La inicialización de la base de datos se realiza mediante `init_db()`, que crea las tablas y aplica las migraciones necesarias.

La carga de información demostrativa se realiza mediante `seed_if_empty()`.

La estructura permite incorporar nuevas tablas y columnas sin eliminar los registros existentes, mediante las operaciones de migración implementadas.

---

## 8. Escenarios de prueba manual

### Dashboard y monitoreo

1. Consultar el dashboard y verificar los contenedores disponibles.
2. Simular una nueva lectura y observar los cambios en los niveles de ocupación.
3. Consultar los eventos registrados.

### Módulo de ciudadanía

4. Ingresar al menú de Ciudadanía.
5. Registrar un residuo RAEE con sus datos y características.
6. Verificar que el registro se almacene correctamente.
7. Ingresar a Solicitar recolección.
8. Seleccionar un residuo previamente registrado.
9. Generar una solicitud y verificar su estado inicial.
10. Comprobar que no se permitan solicitudes activas duplicadas para el mismo registro.
11. Consultar el historial de solicitudes.
12. Ingresar a Consultar puntos de entrega y verificar la información de las ubicaciones activas.

### Módulo de gestores

13. Ingresar al módulo de Gestores.
14. Registrar una empresa y comprobar el almacenamiento de sus datos.
15. Consultar los lotes y verificar los resultados de compatibilidad.
16. Consultar las rutas de gestión.
17. Consultar las ubicaciones de contenedores, gestores y puntos de entrega.
18. Verificar la clasificación territorial de los puntos registrados.

### Gestión general

19. Consultar los gestores y eventos registrados mediante los endpoints correspondientes.
20. Ejecutar el reinicio de los datos de demostración y comprobar su inicialización nuevamente.

---

## 9. Limitaciones conocidas y consideraciones

Ágora RAEE se encuentra en una etapa de prototipado educativo. Por tanto, algunas funcionalidades corresponden a estructuras preparadas o procesos básicos que requieren mayor desarrollo.

- Las lecturas de sensores son simuladas y no representan mediciones físicas reales.
- El sistema no cuenta actualmente con conexión física a Arduino ni integración con Tinkercad.
- El matching utiliza reglas básicas de compatibilidad y no representa un algoritmo avanzado de optimización.
- Las solicitudes ciudadanas permiten seleccionar registros existentes, verificar su existencia y almacenar solicitudes; el flujo completo de verificación documental, asignación automática de gestores y seguimiento logístico todavía requiere desarrollo.
- El registro de empresas gestoras cuenta con persistencia de información institucional, pero requiere ampliar sus procesos de validación y administración.
- Las coordenadas utilizadas inicialmente son demostrativas y no deben interpretarse como ubicaciones verificadas.
- El módulo de georreferenciación permite consultar datos geográficos, pero todavía requiere la integración de un mapa interactivo.
- El módulo de rutas contempla la estructura de almacenamiento y consulta de información logística; el cálculo de recorridos reales y la optimización de rutas están pendientes de desarrollo.
- La consulta de puntos de entrega depende de que existan registros activos en la base de datos.
- La carga y almacenamiento de fotografías de los residuos todavía no están implementados.
- No se ha implementado autenticación ni control de acceso por roles. Por ello, las consultas ciudadanas aún no están restringidas a los registros de una persona específica.
- No existe integración con servicios externos de geolocalización, mapas o navegación.
- Los umbrales, indicadores y puntajes utilizados son ilustrativos y deben contrastarse con la arquitectura unificada de la Etapa 3 antes de considerarse requisitos definitivos.

**Consideración sobre el despliegue:** en entornos convencionales, SQLite almacena la información en el directorio local del proyecto. En el despliegue actual sobre Vercel, la configuración utiliza `/tmp/agora_raee.db`, cuyo contenido no constituye almacenamiento persistente garantizado. Para conservar información de manera permanente en producción será necesario integrar una base de datos persistente.

---

## 10. Proyección del proyecto

Como parte de su evolución, Ágora RAEE contempla:

- Integración de ubicaciones geográficas reales.
- Incorporación de mapas interactivos.
- Cálculo de distancias y planificación de recorridos.
- Fortalecimiento del matching entre gestores y lotes.
- Automatización de la verificación de solicitudes ciudadanas.
- Implementación de asignación de gestores y seguimiento de recolecciones.
- Registro y seguimiento de entregas.
- Fortalecimiento de los procesos de validación documental y clasificación de residuos.
- Implementación de autenticación y control de acceso por roles.
- Integración futura con dispositivos de medición y servicios externos.
- Validación de funcionalidades frente a los requerimientos de la arquitectura unificada.

---

**Ágora RAEE — Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de RAEE.**

*Prototipo académico de desarrollo incremental.*
