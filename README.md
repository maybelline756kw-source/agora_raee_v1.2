# Ágora RAEE — Prototipo web de baja fidelidad

**Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de Residuos de Aparatos Eléctricos y Electrónicos (RAEE).**

Ágora RAEE es un prototipo web orientado a facilitar la articulación entre gestores, puntos de entrega, ciudadanía, instituciones y actores técnicos, mediante herramientas de registro, consulta, seguimiento, compatibilidad y gestión logística de residuos de aparatos eléctricos y electrónicos (RAEE).

El proyecto explora el uso de soluciones tecnológicas para fortalecer la gestión comunitaria de estos residuos, promoviendo la conexión entre los actores involucrados en su recolección, aprovechamiento, reutilización y disposición final.

Se desarrolla como un prototipo educativo de baja fidelidad y enfoque incremental. Su propósito es materializar los procesos propuestos, validar reglas de negocio y evaluar el comportamiento de las funcionalidades mediante escenarios de prueba controlados.

---

# 1. Funcionalidades principales

## 1.1. Dashboard y monitoreo

El dashboard constituye el punto de acceso principal al sistema y permite consultar información general sobre los contenedores y la actividad registrada.

Sus funcionalidades incluyen:

- Visualización del estado de los contenedores.
- Consulta de los niveles de ocupación y capacidad disponible.
- Simulación de lecturas de sensores de distancia, tomando como referencia el funcionamiento del sensor HC-SR04.
- Clasificación de los niveles de ocupación mediante estados y alertas.
- Registro y consulta de eventos y actividades del sistema.

## 1.2. Módulo de ciudadanía

Espacio orientado a facilitar la participación ciudadana en los procesos de gestión de residuos RAEE.

### Registro de residuos

- Formulario para registrar aparatos eléctricos y electrónicos en desuso.
- Captura del tipo de equipo, cantidad, condición, procedencia y fecha de registro.
- Registro de características y descripción del residuo.
- Captura de información del generador, incluyendo nombre, documento, teléfono, correo electrónico y dirección.
- Almacenamiento de los registros en la base de datos SQLite.

### Solicitudes de recolección

- Consulta de residuos previamente registrados.
- Selección de registros para generar solicitudes de recolección.
- Verificación de la existencia del registro seleccionado.
- Prevención de solicitudes activas duplicadas para un mismo registro.
- Creación de solicitudes con estado inicial `Pendiente`.
- Consulta del historial y estado de las solicitudes generadas.

### Consulta de puntos de entrega

- Consulta de puntos de entrega registrados y activos.
- Visualización del nombre, dirección, tipo de punto y clasificación territorial.
- Consulta de descripciones y coordenadas geográficas cuando están disponibles.

## 1.3. Gestión de solicitudes y compatibilidad

El sistema incorpora mecanismos básicos para registrar y consultar solicitudes relacionadas con la gestión de residuos RAEE.

Entre sus funcionalidades se encuentran:

- Creación y consulta de solicitudes de recolección.
- Evaluación de compatibilidad entre lotes y gestores.
- Ejecución de un mecanismo de *matching* basado en reglas de negocio.
- Verificación del tipo de RAEE aceptado por el gestor.
- Evaluación de la capacidad disponible frente al peso requerido.
- Consideración del estado de autorización del gestor.
- Registro de estados y eventos asociados a las solicitudes.

El proceso de selección busca identificar gestores que cumplan las condiciones de compatibilidad definidas para cada lote.

## 1.4. Módulo de gestores

Portal orientado a las empresas y organizaciones encargadas de los procesos de recolección, aprovechamiento y gestión de residuos RAEE.

### Registro de empresas gestoras

- Formulario para registrar información institucional de las empresas gestoras.
- Captura de NIT, representante legal, correo electrónico, teléfono y ubicación.
- Registro del estado de autorización ambiental.
- Identificación de la autoridad ambiental correspondiente.
- Registro de capacidad, cobertura territorial, municipios y servicios ofrecidos.
- Selección de los tipos de RAEE aceptados.
- Almacenamiento de la información institucional en SQLite.

### Gestión de lotes

- Consulta de contenedores y lotes registrados.
- Evaluación de compatibilidad entre los residuos y los gestores.
- Consulta de capacidad máxima y disponibilidad.
- Identificación de gestores elegibles según las reglas de negocio implementadas.

### Rutas de gestión

- Consulta de contenedores, gestores y puntos de entrega relacionados con la logística de recolección.
- Estructura para registrar recorridos y sus respectivos estados.

### Georreferenciación

- Consulta de ubicaciones y coordenadas disponibles.
- Visualización de información territorial.
- Clasificación de zonas rurales y urbanas.
- Identificación del origen de las coordenadas mediante los campos correspondientes.

## 1.5. Módulo institucional

Espacio orientado a las instituciones que generan residuos de aparatos eléctricos y electrónicos, permitiendo registrar equipos dados de baja, consultar inventarios y gestionar los estados asociados a estos registros.

### Registro institucional de RAEE

- Formulario para registrar residuos electrónicos generados por instituciones.
- Captura del tipo de equipo, cantidad, condición, origen y fecha de registro.
- Registro de características de los residuos.
- Captura de información institucional, incluyendo nombre del generador, documento, teléfono, correo electrónico y dirección.
- Almacenamiento de los registros en la tabla `raee_records` de SQLite.
- Identificación del origen del registro mediante el campo `generator_type`, establecido como `Institución`.

### Gestión de bajas institucionales

- Consulta de registros RAEE pertenecientes a instituciones.
- Visualización de la información de los equipos registrados.
- Actualización del estado de los registros.
- Manejo de estados como:
  - `Registrado`.
  - `Baja solicitada`.
  - `Baja aprobada`.
  - `En gestión`.
  - `Gestionado`.

### Inventario institucional

- Consulta de los registros institucionales almacenados.
- Visualización de la información de los residuos registrados.
- Resumen del total de registros.
- Cálculo de la cantidad total de equipos registrados.
- Identificación de instituciones mediante los documentos registrados.

## 1.6. Módulo técnico

Portal orientado a actores técnicos interesados en consultar lotes de residuos electrónicos y registrar solicitudes de equipos o componentes para actividades de reparación, mantenimiento o aprovechamiento.

El módulo cuenta con tres secciones principales:

### Consulta de lotes disponibles

- Consulta de los contenedores registrados en el sistema.
- Visualización del nombre, tipo de RAEE y ubicación.
- Consulta de la cantidad de residuos registrada en cada contenedor.
- Visualización de la capacidad máxima y el porcentaje de ocupación.
- Identificación del estado del contenedor mediante las categorías `Normal`, `Atención` y `Crítico`.
- Resumen del número de lotes y de los kilogramos registrados.

### Solicitud de equipos o componentes

- Formulario para registrar solicitudes de recursos tecnológicos.
- Identificación del solicitante.
- Selección del tipo de recurso: equipo completo o componente.
- Registro del nombre del equipo o componente requerido.
- Captura de la cantidad solicitada.
- Registro de la justificación de la solicitud.
- Validación de campos obligatorios y cantidades permitidas.
- Almacenamiento de las solicitudes en la tabla `technical_requests`.
- Asignación automática del estado inicial `Pendiente`.

### Seguimiento de solicitudes

- Consulta del historial de solicitudes técnicas.
- Visualización del identificador de cada solicitud.
- Consulta del nombre del solicitante.
- Visualización del tipo de recurso y la cantidad solicitada.
- Consulta de la justificación y fecha de registro.
- Visualización del estado de cada solicitud.
- Resumen de solicitudes totales, pendientes y aprobadas, de acuerdo con los estados almacenados.

## 1.7. Gestión geográfica

El sistema incorpora una estructura de datos preparada para trabajar con información geográfica relacionada con los contenedores, gestores y puntos de entrega.

Esta estructura contempla:

- Coordenadas geográficas de contenedores y gestores.
- Registro de puntos de recolección y entrega.
- Clasificación territorial de zonas rurales y urbanas.
- Identificación del origen de las coordenadas mediante los valores `demo` y `real`.
- Almacenamiento de información asociada a recorridos y sus respectivos estados.

El modelo utiliza inicialmente datos demostrativos y permite incorporar ubicaciones reales en futuras etapas de desarrollo.

---

# 2. Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| Python | Lenguaje principal de desarrollo. |
| FastAPI | Desarrollo del backend, rutas y servicios web. |
| SQLite | Persistencia y almacenamiento de información. |
| HTML5 | Estructura de las interfaces web. |
| CSS3 | Diseño y presentación visual. |
| Jinja2 | Renderizado dinámico de plantillas HTML. |
| Uvicorn | Servidor ASGI para la ejecución de la aplicación. |

---

# 3. Estructura general del proyecto

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
│   ├── ciudadania/
│   │   ├── menu.html
│   │   ├── registrar.html
│   │   ├── recoleccion.html
│   │   └── puntos.html
│   │
│   ├── instituciones/
│   │   ├── menu.html
│   │   ├── registrar.html
│   │   ├── bajas.html
│   │   └── inventario.html
│   │
│   └── tecnico/
│       ├── menu.html
│       ├── lotes.html
│       ├── solicitar.html
│       └── seguimiento.html
│
└── static/
    └── styles.css
```

### Descripción de los archivos y directorios principales

- **`main.py`:** configura la aplicación FastAPI, inicializa los datos y define las rutas web y los endpoints de la API.
- **`database.py`:** establece la conexión con SQLite, define las tablas y ejecuta las migraciones necesarias para actualizar la estructura de la base de datos.
- **`seed.py`:** contiene los datos de demostración utilizados para inicializar el sistema.
- **`services.py`:** implementa la lógica de negocio relacionada con el matching, las solicitudes, las simulaciones y el registro de eventos.
- **`requirements.txt`:** contiene las dependencias necesarias para ejecutar el proyecto.
- **`templates/`:** almacena las interfaces HTML y las plantillas dinámicas de los módulos de gestores, ciudadanía, instituciones y técnicos.
- **`static/`:** contiene los recursos de presentación, como las hojas de estilo CSS.
- **`data/`:** almacena la base de datos local cuando la aplicación se ejecuta en un entorno convencional.

---

# 4. Requisitos de ejecución

Para ejecutar el proyecto en un entorno local se recomienda disponer de:

- Python 3.10 o superior.
- `pip` para la instalación de dependencias.
- Un navegador web actualizado.
- Conexión a internet únicamente cuando se utilicen recursos externos que la requieran.

Las dependencias del proyecto se encuentran definidas en el archivo `requirements.txt`.

---

# 5. Rutas principales de la aplicación

## 5.1. Interfaces web

### Dashboard

| Ruta | Descripción |
|---|---|
| `/` | Dashboard principal del sistema. |

### Gestores

| Ruta | Descripción |
|---|---|
| `/form/gestor` | Menú principal del módulo de gestores. |
| `/form/gestor/registro` | Formulario de registro de empresas gestoras. |
| `/form/gestor/lotes` | Consulta y compatibilidad de lotes. |
| `/form/gestor/rutas` | Módulo de rutas de gestión. |
| `/form/gestor/georreferenciacion` | Consulta de ubicaciones geográficas. |

### Ciudadanía

| Ruta | Descripción |
|---|---|
| `/form/ciudadania` | Menú principal de ciudadanía. |
| `/form/ciudadania/registrar` | Registro de residuos RAEE. |
| `/form/ciudadania/recoleccion` | Solicitud y consulta de recolecciones. |
| `/form/ciudadania/puntos` | Consulta de puntos de entrega. |

### Instituciones

| Ruta | Descripción |
|---|---|
| `/form/instituciones` | Menú principal de instituciones. |
| `/form/instituciones/registrar` | Registro de residuos RAEE institucionales. |
| `/form/instituciones/bajas` | Gestión y actualización de estados de bajas. |
| `/form/instituciones/inventario` | Consulta del inventario institucional. |

### Técnicos

| Ruta | Descripción |
|---|---|
| `/form/tecnico` | Menú principal del portal técnico. |
| `/form/tecnico/lotes` | Consulta de lotes registrados. |
| `/form/tecnico/solicitar` | Solicitud de equipos y componentes. |
| `/form/tecnico/seguimiento` | Consulta del historial de solicitudes técnicas. |

## 5.2. API

| Método | Endpoint | Funcionalidad |
|---|---|---|
| POST | `/api/simulate/{container_id}` | Genera una lectura simulada de un contenedor. |
| POST | `/api/requests/{container_id}` | Crea una solicitud y ejecuta el proceso de matching. |
| GET | `/api/managers` | Consulta los gestores registrados. |
| GET | `/api/events` | Consulta los eventos del sistema. |
| GET | `/api/requests` | Consulta las solicitudes de recolección. |
| POST | `/api/reset-demo` | Reinicia los datos de demostración. |

Las interfaces de ciudadanía, instituciones y técnicos cuentan adicionalmente con operaciones web para registrar, consultar y gestionar la información de sus respectivos módulos.

---

# 6. Base de datos

El sistema utiliza SQLite para almacenar la información y facilitar la persistencia de los registros durante la ejecución local.

## 6.1. Principales tablas

| Tabla | Descripción |
|---|---|
| `containers` | Información de contenedores RAEE, capacidad, ocupación y ubicación. |
| `managers` | Información de gestores, tipos de residuos aceptados, capacidad, autorización y datos institucionales. |
| `events` | Registro de eventos y alertas del sistema. |
| `collection_requests` | Solicitudes de recolección asociadas a contenedores. |
| `delivery_points` | Información de puntos de recepción y entrega. |
| `routes` | Registro de recorridos y estados asociados. |
| `raee_records` | Información de los residuos registrados por ciudadanía e instituciones. |
| `pickup_requests` | Solicitudes de recolección asociadas a registros de residuos. |
| `community_posts` | Publicaciones comunitarias. |
| `community_comments` | Comentarios asociados a publicaciones comunitarias. |
| `technical_requests` | Solicitudes técnicas de equipos completos o componentes. |

## 6.2. Información de las solicitudes técnicas

La tabla `technical_requests` almacena la información correspondiente a las solicitudes realizadas desde el portal técnico.

Sus principales campos son:

| Campo | Descripción |
|---|---|
| `id` | Identificador único de la solicitud. |
| `applicant_name` | Nombre del solicitante. |
| `resource_type` | Tipo de recurso solicitado. |
| `resource_name` | Nombre del equipo o componente. |
| `quantity` | Cantidad solicitada. |
| `justification` | Justificación de la solicitud. |
| `status` | Estado de la solicitud. |
| `created_at` | Fecha de creación del registro. |

Las solicitudes se almacenan inicialmente con el estado `Pendiente`.

## 6.3. Estructura geográfica

La información geográfica contempla campos como:

- `latitude`: latitud.
- `longitude`: longitud.
- `zone_type`: clasificación territorial, rural o urbana.
- `coordinate_source`: origen de las coordenadas, demostrativo o real.

## 6.4. Inicialización y actualización de la base de datos

La inicialización de la base de datos se realiza mediante la función `init_db()`, encargada de crear las tablas y aplicar las migraciones necesarias.

La carga de información demostrativa se realiza mediante `seed_if_empty()`.

La estructura permite incorporar nuevas tablas y columnas mediante las operaciones de migración implementadas, sin requerir la eliminación de los registros existentes.

---

# 7. Escenarios de prueba manual

Los siguientes escenarios permiten verificar el comportamiento general de los módulos y las principales operaciones del prototipo.

## 7.1. Dashboard y monitoreo

- Consultar el dashboard y verificar los contenedores disponibles.
- Simular una nueva lectura y observar los cambios en los niveles de ocupación.
- Verificar la clasificación de los estados de ocupación.
- Consultar los eventos registrados.

## 7.2. Módulo de ciudadanía

- Ingresar al menú de ciudadanía.
- Registrar un residuo RAEE con sus datos y características.
- Verificar que el registro se almacene correctamente.
- Ingresar a la sección de solicitudes de recolección.
- Seleccionar un residuo previamente registrado.
- Generar una solicitud y verificar su estado inicial.
- Comprobar que no se permitan solicitudes activas duplicadas para un mismo registro.
- Consultar el historial de solicitudes.
- Ingresar a la consulta de puntos de entrega y verificar la información de las ubicaciones activas.

## 7.3. Módulo de gestores

- Ingresar al módulo de gestores.
- Registrar una empresa y comprobar el almacenamiento de sus datos.
- Consultar los lotes y verificar los resultados de compatibilidad.
- Comprobar la selección de gestores según el tipo de RAEE, la capacidad disponible y la autorización.
- Consultar las rutas de gestión.
- Consultar las ubicaciones de contenedores, gestores y puntos de entrega.
- Verificar la clasificación territorial de los puntos registrados.

## 7.4. Módulo institucional

- Ingresar al portal de instituciones.
- Registrar un residuo electrónico institucional.
- Verificar que los datos se almacenen correctamente.
- Ingresar a la sección de gestión de bajas.
- Consultar los registros institucionales.
- Actualizar el estado de un registro y comprobar que el cambio se refleje.
- Ingresar al inventario institucional.
- Verificar el total de registros, equipos e instituciones contabilizados.

## 7.5. Módulo técnico

- Ingresar al portal técnico.
- Consultar los lotes registrados en el sistema.
- Verificar la cantidad de residuos, capacidad y porcentaje de ocupación.
- Registrar una solicitud de equipo completo.
- Registrar una solicitud de componente.
- Comprobar la validación de campos obligatorios y cantidades.
- Verificar que las solicitudes queden almacenadas con estado inicial `Pendiente`.
- Ingresar a la sección de seguimiento.
- Comprobar que aparezcan las solicitudes registradas.
- Verificar el resumen de solicitudes totales, pendientes y aprobadas, según los estados disponibles.

## 7.6. Gestión general

- Consultar los gestores y eventos registrados mediante los endpoints correspondientes.
- Consultar las solicitudes de recolección.
- Verificar el comportamiento de las operaciones de persistencia.
- Comprobar la inicialización de los datos de demostración cuando corresponda.

---

# 8. Limitaciones conocidas y consideraciones

Ágora RAEE se encuentra en una etapa de prototipado educativo. Por esta razón, algunas funcionalidades corresponden a procesos simulados, estructuras preparadas o mecanismos básicos que requieren ampliación para su implementación en un entorno real.

Las siguientes consideraciones delimitan el alcance actual del sistema.

## 8.1. Monitoreo y logística

- Las lecturas de sensores son simuladas y no representan mediciones físicas reales.
- El sistema no cuenta actualmente con conexión física a Arduino ni integración con Tinkercad.
- El matching utiliza reglas básicas de compatibilidad y no representa un algoritmo avanzado de optimización logística.
- Las solicitudes ciudadanas permiten seleccionar registros existentes, verificar su existencia y almacenar solicitudes. El flujo completo de verificación documental, asignación automática de gestores y seguimiento logístico requiere desarrollo adicional.

## 8.2. Gestión institucional y técnica

- El registro de empresas gestoras permite almacenar información institucional, pero requiere ampliar sus procesos de validación y administración.
- El módulo institucional permite registrar residuos, consultar inventarios y actualizar estados de bajas. Estos cambios de estado no equivalen a una certificación ambiental ni a la eliminación física de los residuos.
- El inventario institucional se basa en los registros almacenados en `raee_records`.
- El portal técnico consulta los contenedores registrados, pero la cantidad de residuos almacenada no representa necesariamente componentes disponibles para reutilización o reparación.
- No existe todavía un inventario desagregado de componentes como memorias RAM, discos duros, fuentes de poder u otras piezas recuperables.
- Las solicitudes técnicas permiten registrar equipos o componentes requeridos y consultar su estado, pero todavía no cuentan con un proceso administrativo completo de aprobación, rechazo, asignación o entrega de recursos.
- El seguimiento técnico muestra las solicitudes registradas en el sistema y no restringe los resultados a un solicitante específico.
- No existe una relación automática entre los registros institucionales de `raee_records` y los contenedores de `containers`.

## 8.3. Georreferenciación y rutas

- Las coordenadas utilizadas inicialmente son demostrativas y no deben interpretarse como ubicaciones verificadas.
- El módulo de georreferenciación permite consultar datos geográficos, pero requiere la integración de un mapa interactivo.
- El módulo de rutas contempla la estructura de almacenamiento y consulta de información logística; el cálculo de recorridos reales y la optimización de rutas están pendientes de desarrollo.
- La consulta de puntos de entrega depende de la existencia de registros activos en la base de datos.
- No existe integración con servicios externos de geolocalización, mapas o navegación.

## 8.4. Seguridad y almacenamiento

- La carga y el almacenamiento de fotografías de los residuos todavía no están implementados.
- No se ha implementado autenticación ni control de acceso por roles.
- Las consultas ciudadanas aún no están restringidas a los registros de una persona específica.
- Las solicitudes técnicas tampoco cuentan con identificación individual ni seguimiento privado por usuario.

## 8.5. Indicadores y datos demostrativos

- Los datos utilizados para las demostraciones no representan necesariamente condiciones reales de operación.
- Los umbrales, indicadores y puntajes utilizados tienen carácter ilustrativo y deben contrastarse con la arquitectura unificada de la Etapa 3 antes de considerarse requisitos definitivos.
- Los indicadores ambientales y sociales requieren información real y procesos adicionales de consolidación para representar resultados verificables.

## 8.6. Consideraciones sobre el despliegue

En entornos convencionales, SQLite almacena la información en el directorio local del proyecto.

En el despliegue actual sobre Vercel, la configuración utiliza `/tmp/agora_raee.db`, cuyo contenido no constituye almacenamiento persistente garantizado.

Por lo tanto, para conservar información de manera permanente en un entorno de producción será necesario integrar una base de datos persistente.

---

# 9. Proyección y mejoras futuras

Como parte de su evolución, Ágora RAEE contempla las siguientes posibilidades de ampliación:

- Integración de ubicaciones geográficas reales.
- Incorporación de mapas interactivos.
- Cálculo de distancias y planificación de recorridos.
- Fortalecimiento del matching entre gestores y lotes.
- Automatización de la verificación de solicitudes ciudadanas.
- Implementación de procesos de asignación de gestores y seguimiento de recolecciones.
- Registro y seguimiento de entregas.
- Fortalecimiento de los procesos de validación documental y clasificación de residuos.
- Implementación de autenticación y control de acceso por roles.
- Desarrollo de procesos administrativos para aprobar, rechazar y asignar solicitudes técnicas.
- Creación de un inventario de equipos y componentes recuperables.
- Integración de los registros institucionales con los procesos de gestión y aprovechamiento.
- Integración futura con dispositivos físicos de medición y servicios externos.
- Validación de funcionalidades frente a los requerimientos de la arquitectura unificada.
- Incorporación de mecanismos de almacenamiento persistente para el despliegue en producción.

---

**Ágora RAEE — Marketplace Interinstitucional y Comunitario para la Gestión y Disposición de RAEE.**

*Prototipo académico de baja fidelidad y desarrollo incremental.*
