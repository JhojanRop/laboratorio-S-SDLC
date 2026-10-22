"""Pruebas de control de acceso (IDOR)."""


def test_estudiante_no_edita_nota_ajena(logged_client):
    response = logged_client.get("/nota/editar/3")
    assert response.status_code == 403


def test_estudiante_edita_su_propia_nota(logged_client):
    response = logged_client.get("/nota/editar/1")
    assert response.status_code == 200


def test_docente_edita_nota_ajena(staff_client):
    response = staff_client.get("/nota/editar/3")
    assert response.status_code == 200


def test_estudiante_no_edita_biografia_ajena(logged_client):
    response = logged_client.get("/perfil/2/editar")
    assert response.status_code == 403


def test_estudiante_edita_su_propia_biografia(logged_client):
    response = logged_client.get("/perfil/1/editar")
    assert response.status_code == 200
