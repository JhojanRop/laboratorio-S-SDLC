# Bitácora Técnica — Laboratorio S-SDLC

Documento de seguimiento de decisiones arquitectónicas, cambios relevantes y lecciones aprendidas durante el desarrollo del laboratorio.

---

## Estandarización del proyecto con uv e inicialización de Git

### Contexto

El proyecto necesitaba una base sólida de gestión de dependencias y control de versiones antes de comenzar a construir la aplicación vulnerable. Se definió que el laboratorio debía ser fácil de reproducir por cualquier estudiante, sin importar su sistema operativo o versión de Python instalada.

### Decisiones tomadas

**1. Adopción de uv como gestor de dependencias y entorno**

Se eligió [uv](https://docs.astral.sh/uv/) sobre alternativas tradicionales (pip + virtualenv, pipenv, poetry) por las siguientes razones:

- Es un estándar emergente en la industria, con adopción creciente en proyectos Python modernos.
- Gestiona de forma integrada: dependencias, entorno virtual (`.venv/`) y versión de Python (mediante `.python-version`).
- El archivo `uv.lock` garantiza reproducibilidad exacta de las dependencias entre distintos entornos.
- Es significativamente más rápido que pip gracias a su implementación en Rust.

**2. Creación de un `.gitignore` robusto**

Se configuró un `.gitignore` exhaustivo que actúa como **primera capa de seguridad** al impedir que archivos sensibles lleguen al repositorio. Las categorías cubiertas incluyen:

- Entornos virtuales (`.venv/`, `venv/`, etc.)
- Bases de datos locales (`*.db`, `*.sqlite3`)
- Variables de entorno (`.env`, `.env.*`)
- Claves y certificados (`*.pem`, `*.key`, `id_rsa*`, etc.)
- Credenciales de servicios en la nube (`.aws/`, `.gcloud/`, `credentials.json`)
- Reportes de herramientas de seguridad (bandit, semgrep, trivy, ZAP)
- Archivos de subida de usuarios (`uploads/*`)
- Artefactos de compilación y caché de Python

**3. Inicialización del repositorio Git**

Se ejecutó `git init` para establecer control de versiones desde el inicio del proyecto, permitiendo:

- Trazabilidad de todos los cambios realizados.
- Ramas para experimentar con fixes de seguridad sin afectar la versión vulnerable principal.
- Colaboración entre estudiantes y docentes mediante un historial claro.

### Impacto

Con estas decisiones, el proyecto queda en una base estandarizada, reproducible y con buenas prácticas de seguridad desde el commit inicial. Cualquier estudiante puede clonar el repositorio y ejecutar `uv sync && uv run app.py` para tener el laboratorio funcionando en segundos.

---

## Implementación de prácticas Shift-Left

### Contexto

Una vez establecida la base del proyecto, el siguiente paso fue incorporar prácticas de seguridad desde las etapas tempranas del desarrollo (Shift-Left). El objetivo era que la seguridad no sea una revisión al final, sino que esté integrada en el flujo cotidiano de trabajo.

### Decisiones tomadas

**1. Integración de pre-commit con hooks de calidad y seguridad**

Se configuró [pre-commit](https://pre-commit.com/) para ejecutar validaciones automáticas antes de cada commit. Los hooks incluidos cubren:

- **Formateo y linting** con `ruff` para mantener un estilo de código uniforme.
- **Análisis de seguridad estático** con `bandit`, introduciendo así el primer vestigio de seguridad automatizada en el pipeline local.
- Validación de Conventional Commits mediante `commitlint`.

Esto garantiza que ningún código que no cumpla con los estándares de calidad o que presente vulnerabilidades conocidas pueda ser commiteado sin revisión.

**2. Creación de AGENTS.md para gobernanza de agentes IA**

Se definió un archivo `AGENTS.md` que establece los límites y reglas de operación para cualquier agente de IA que trabaje en el repositorio (OpenCode, Claude Code, Codex, etc.). Esto asegura que:

- Independientemente de la herramienta utilizada, el agente respete la misma estructura y convenciones.
- Se preserve la intencionalidad de las vulnerabilidades salvo tarea explícita.
- No se mezclen tipos de trabajo (código, documentación, git) en una sola sesión.

**3. Flujo de Git simplificado con protección de rama principal**

Se implementó un flujo basado en Git Flow simplificado:

- `main`: rama protegida, solo recibe cambios mediante Pull Requests.
- `dev`: rama de integración donde se fusionan las ramas funcionales.
- Ramas de corta duración (`feat/`, `fix/`, `docs/`, `refactor/`) creadas desde `dev`.

La protección de `main` garantiza que ningún cambio llegue a producción sin revisión previa, cumpliendo así con un principio básico de control de acceso en el ciclo de vida del software.

**4. Versionado automático con release-please**

Se añadió la acción de GitHub [release-please](https://github.com/googleapis/release-please) para gestionar de forma automática el versionado de la aplicación basándose en los Conventional Commits. Esto elimina la carga manual de mantener changelogs y tags de versión.

### Estado actual y pendientes

La implementación del Shift-Left en este punto es **parcial**. Varios ajustes de CI/CD marcaban errores debido a las vulnerabilidades intencionales de la aplicación, lo que hacía inviable completar el pipeline en este momento. La idea es retomar estas integraciones una vez que se hayan abordado los hallazgos de seguridad o se hayan configurado las exclusiones correspondientes.

---

## Creación de la versión segura del laboratorio

### Contexto

Siguiendo la metodología del taller, se decidió no modificar los archivos originales vulnerables y crear en paralelo una versión segura. Esto permite a los estudiantes comparar ambos flujos, entender exactamente qué se corrigió y por qué, y practicar la migración de un código vulnerable a uno seguro.

### Decisiones tomadas

**1. Archivos originales intactos, versión segura en archivos paralelos**

Se dejó `app.py`, `database.py` y `templates/` sin modificar. La versión segura se creó en archivos nuevos: `app_segura.py`, `models.py`, `config.py` y `templates_seguras/`. Esto garantiza que el laboratorio vulnerable siga funcionando para prácticas de explotación mientras se ofrece una referencia segura para comparación.

**2. Configuración por entorno con `config.py`**

Se implementó un archivo `config.py` basado en entornos (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`). Esto es fundamental tanto para el despliegue como para las pruebas, ya que cada entorno tiene necesidades distintas:

- `SECRET_KEY` y `DATABASE_URI` se leen desde variables de entorno (vía `python-dotenv`).
- `DEBUG` se controla por entorno y **no** está hardcodeado.
- Endurecimiento de cookies de sesión (`HTTPONLY`, `SAMESITE`, `SECURE` en producción).
- Límite de tamaño de archivo (`MAX_CONTENT_LENGTH` de 2 MB).
- La aplicación **falla en arrancar** si `SECRET_KEY` no está configurada, evitando así el uso de claves débiles por defecto.

**3. Migración a SQLAlchemy ORM para eliminar SQLi**

Se reemplazó el acceso directo a SQLite con consultas concatenadas por **Flask-SQLAlchemy**. Toda la interacción con la base de datos ahora pasa a través del ORM (`Usuario.query.filter_by(...)`, `Estudiante.query.filter(...)`), lo que elimina por completo la superficie de inyección SQL al usar consultas parametrizadas internamente.

**4. Puerto separado para el flujo seguro**

La versión segura corre en el **puerto 3001**, mientras que la vulnerable permanece en el 5000. Esto permite ejecutar ambos entornos simultáneamente y comparar comportamientos sin interferencias.

### Medidas de seguridad adicionales implementadas

Más allá de las 4 correcciones principales, la versión segura incluye:

- **Cabeceras HTTP de endurecimiento**: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy y Permissions-Policy.
- **Control de acceso por rol y propietario**: decorador `login_required` y función `is_staff()` para proteger rutas sensibles.
- **Validación de uploads**: `secure_filename`, whitelist de extensiones, nombre único con UUID y límite de 2 MB.
- **Prevención de fijación de sesión**: `session.clear()` antes de autenticar.
- **Validación de entrada**: límite de caracteres en biografía y rango de notas (0–5).

### Pendientes identificados

- **Contraseñas en texto plano**: `models.py` aún almacena contraseñas sin hash (marcado con `# TODO: usar hash.`). Esta mejora queda pendiente para una futura iteración.
- **`.env.example` sin trackear**: existe en el working tree pero aún no ha sido commiteado.

---

## Corrección de almacenamiento de contraseñas

### Contexto

La versión segura seguía almacenando las contraseñas en texto plano en la base de datos, lo que representaba una vulnerabilidad crítica: cualquier acceso a la BD (por ejemplo, mediante SQLi o un backup expuesto) comprometía todas las credenciales de los usuarios. Se implementó un mecanismo de hash seguro para cerrar esta brecha.

### Decisiones tomadas

**1. Hash de contraseñas con werkzeug (pbkdf2:sha256)**

Se utilizó `werkzeug.security.generate_password_hash` con el método `pbkdf2:sha256`, que aplica múltiples iteraciones de derivación de clave con sal automática. Esto garantiza que:

- Las contraseñas nunca se almacenen en texto plano.
- Cada hash sea único incluso para contraseñas idénticas (gracias a la sal aleatoria).
- El costo computacional frente a ataques de fuerza bruta sea elevado.

**2. Replanteamiento de la semilla de datos**

El campo `password` fue renombrado a `password_hash` y la función `seed_data()` se reescribió para crear cada usuario y aplicar `set_password(...)` antes de guardar. Esto asegura que los datos de ejemplo ya nazcan con el formato correcto y no requieran migración manual.

**3. Verificación en el flujo de autenticación**

El login en `app_segura.py` ahora busca al usuario por `username` y verifica la contraseña con `user.check_password(clave)`, comparando contra el hash almacenado en lugar de hacerlo en la consulta SQL.

### Impacto

Con este cambio, la versión segura elimina el almacenamiento de credenciales en cerrado y se alinea con las mejores prácticas de manejo de contraseñas. Si la base de datos es comprometida, los atacantes solo obtendren hashes que requieren un esfuerzo computacional significativo para revertir.

### Nota técnica

El cambio de nombre de columna (`password` → `password_hash`) implica que una base de datos generada con la estructura anterior debe ser regenerada, ya que `db.create_all()` no realiza migraciones sobre tablas existentes.

---

## Implementación de pruebas automatizadas de seguridad

### Contexto

Una vez implementada la versión segura, era necesario verificar de forma sistemática y reproducible que las correcciones funcionan y que no se introducen regresiones. Se creó un directorio `tests/` con una suite de pruebas automatizadas enfocada en validar la **ausencia de vulnerabilidades**, no solo el comportamiento esperado.

### Decisiones tomadas

**1. Enfoque en regresión de seguridad**

Los tests no solo verifican el happy path; validan explícitamente que los ataques conocidos **fallan**. Por ejemplo:

- Se intenta inyectar `' --` en el login y se verifica que no autentica.
- Se intenta un UNION-based SQLi en el buscador y se verifica que no filtra credenciales.
- Se intenta inyectar `<script>` en la biografía y se verifica que se escapa correctamente.

**2. Cobertura de todas las vulnerabilidades corregidas**

Cada vulnerabilidad original tiene tests dedicados:

| Vulnerabilidad | Tests específicos |
|---------------|-------------------|
| SQLi | Login y búsqueda |
| XSS | Escape en perfil y en resultados de búsqueda |
| IDOR | Estudiante no edita recursos ajenos, sí los propios; staff sí puede |
| Uploads | Whitelist de extensiones, límite de tamaño, requiere autenticación |
| Auth | Login correcto/incorrecto, hash de contraseñas, redirección de rutas protegidas |
| Cabeceras | Presencia de CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy |

**3. Aislamiento con fixtures y BD en memoria**

Se configuró `conftest.py` con `APP_ENV=testing` (SQLite en memoria) y fixtures que recrean la BD y la semilla en cada test. Esto garantiza:

- Tests independientes y deterministas.
- Sin estado compartido entre pruebas.
- Ejecución rápida sin tocar la BD de desarrollo.

**4. Verificación explícita del hash de contraseñas**

Se incluyó un test (`test_contrasenas_almacenadas_con_hash`) que verifica que las contraseñas no se almacenan en texto plano, que el hash usa `pbkdf2:sha256:`, y que `check_password` funciona correctamente.

### Impacto

La suite de pruebas sirve como **documentación viva** de las correcciones realizadas y como mecanismo de regresión: cualquier cambio que reintroduzca una vulnerabilidad será detectado automáticamente. Además, proporciona a los estudiantes un ejemplo concreto de cómo se prueban las correcciones de seguridad.

---
