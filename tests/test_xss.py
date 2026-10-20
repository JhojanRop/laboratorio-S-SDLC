"""Pruebas de Cross-Site Scripting."""


def test_biografia_escapada_en_perfil(staff_client):
    payload = "<script>alert('xss')</script>"
    response = staff_client.post(
        "/perfil/1/editar",
        data={"biografia": payload},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<script>alert" not in response.data
    assert b"&lt;script&gt;" in response.data
    assert b"alert(&#39;xss&#39;)" in response.data


def test_busqueda_escapa_biografia(staff_client):
    payload = "<img src=x onerror=alert(1)>"
    staff_client.post(
        "/perfil/1/editar",
        data={"biografia": payload},
        follow_redirects=True,
    )

    response = staff_client.get("/buscar", query_string={"q": "Ana"})
    assert response.status_code == 200
    assert b"<img src=x" not in response.data
    assert b"&lt;img src=x" in response.data
