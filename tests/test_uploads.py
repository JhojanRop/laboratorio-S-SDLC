"""Pruebas de carga de archivos."""

import io

from app_segura import app


def test_upload_extension_no_permitida(logged_client):
    response = logged_client.post(
        "/subir",
        data={"archivo": (io.BytesIO(b"<?php echo 1; ?>"), "shell.php")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Extension no permitida" in response.data


def test_upload_extension_permitida(logged_client, tmp_path):
    response = logged_client.post(
        "/subir",
        data={"archivo": (io.BytesIO(b"contenido"), "nota.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"subido correctamente" in response.data

    archivos = list((tmp_path / "uploads").iterdir())
    assert len(archivos) == 1
    assert archivos[0].suffix == ".txt"


def test_upload_tamano_excedido(logged_client):
    max_original = app.config["MAX_CONTENT_LENGTH"]
    app.config["MAX_CONTENT_LENGTH"] = 1024
    try:
        response = logged_client.post(
            "/subir",
            data={"archivo": (io.BytesIO(b"x" * 2048), "grande.txt")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 413
    finally:
        app.config["MAX_CONTENT_LENGTH"] = max_original


def test_upload_requiere_login(client):
    response = client.get("/subir")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
