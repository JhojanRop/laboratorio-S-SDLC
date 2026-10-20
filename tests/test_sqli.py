"""Pruebas de inyeccion SQL."""


def test_login_no_vulnerable_a_sqli(client):
    response = client.post(
        "/login",
        data={"username": "admin' --", "password": "x"},
    )
    assert response.status_code == 200
    assert b"Credenciales invalidas" in response.data
    assert b"admin" not in response.data


def test_busqueda_no_filtra_usuarios(client):
    payload = "' UNION SELECT id, username, password_hash, rol FROM usuarios --"
    response = client.get("/buscar", query_string={"q": payload})
    assert response.status_code == 200
    assert b"Sin resultados" in response.data
    assert b"pbkdf2" not in response.data


def test_busqueda_valida_encuentra_estudiante(client):
    response = client.get("/buscar", query_string={"q": "Ana"})
    assert response.status_code == 200
    assert b"Ana Torres" in response.data
