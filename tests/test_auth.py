"""Pruebas de autenticacion y manejo de contrasenas."""

from app_segura import app
from models import Usuario


def test_login_correcto(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_login_password_incorrecta(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "incorrecta"},
    )
    assert response.status_code == 200
    assert b"Credenciales invalidas" in response.data


def test_login_usuario_inexistente(client):
    response = client.post(
        "/login",
        data={"username": "no-existe", "password": "x"},
    )
    assert response.status_code == 200
    assert b"Credenciales invalidas" in response.data


def test_contrasenas_almacenadas_con_hash(client):
    with app.app_context():
        for username, password in [
            ("admin", "admin123"),
            ("profesor", "clave456"),
            ("estudiante", "1234"),
        ]:
            usuario = Usuario.query.filter_by(username=username).one()
            assert usuario.password_hash != password
            assert usuario.password_hash.startswith("pbkdf2:sha256:")
            assert usuario.check_password(password)
            assert not usuario.check_password(password + "-incorrecta")


def test_rutas_protegidas_redirigen_al_login(client):
    for ruta in ["/subir", "/perfil/1/editar", "/nota/editar/1"]:
        response = client.get(ruta)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]
