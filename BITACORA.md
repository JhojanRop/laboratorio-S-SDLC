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
