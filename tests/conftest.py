"""Fixtures compartidas para las pruebas de app_segura.py."""

# ruff: noqa: E402

import os

os.environ["APP_ENV"] = "testing"

import pytest

from app_segura import app
from models import db, seed_data


@pytest.fixture()
def client(tmp_path):
    """Cliente de pruebas con base de datos limpia y subidas temporales."""
    app.config["UPLOAD_FOLDER"] = str(tmp_path / "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        seed_data()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()


@pytest.fixture()
def logged_client(client):
    """Cliente autenticado como estudiante (estudiante_id=1)."""
    client.post("/login", data={"username": "estudiante", "password": "1234"})
    return client


@pytest.fixture()
def staff_client(client):
    """Cliente autenticado como docente."""
    client.post("/login", data={"username": "profesor", "password": "clave456"})
    return client
