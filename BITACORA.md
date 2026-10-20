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
