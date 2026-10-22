FROM python:3.12-slim

# uv, el mismo gestor de dependencias que usa el proyecto.
COPY --from=ghcr.io/astral-sh/uv:0.11.0 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    APP_ENV=production \
    PORT=5000 \
    FLASK_DEBUG=false

WORKDIR /app

# Instala solo dependencias de produccion (sin pytest, bandit ni ruff).
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project && uv cache clean

# Copia unicamente la version segura. app.py y database.py quedan fuera.
COPY app_segura.py models.py config.py ./
COPY templates_seguras ./templates_seguras
COPY static ./static

# Usuario sin privilegios y directorios persistentes.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/uploads_seguras /data \
    && chown appuser:appuser /app/uploads_seguras /data

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/login')"]

# Un worker con hilos evita problemas de concurrencia al inicializar SQLite.
CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "app_segura:app"]
