import io


def headers(usuario_autenticado):
    return {"Authorization": f"Bearer {usuario_autenticado['access_token']}"}


def test_listar_transcricoes_vazio(client, usuario_autenticado):
    r = client.get("/transcricoes", headers=headers(usuario_autenticado))
    assert r.status_code == 200
    assert r.json()["total"] == 0
    assert r.json()["items"] == []


def test_upload_formato_invalido(client, usuario_autenticado):
    arquivo_falso = io.BytesIO(b"conteudo qualquer")
    r = client.post(
        "/transcricoes",
        files={"arquivo": ("teste.txt", arquivo_falso, "text/plain")},
        headers=headers(usuario_autenticado)
    )
    assert r.status_code == 400


def test_status_nao_encontrado(client, usuario_autenticado):
    r = client.get("/transcricoes/9999/status", headers=headers(usuario_autenticado))
    assert r.status_code == 404


def test_resumo_nao_encontrado(client, usuario_autenticado):
    r = client.get("/transcricoes/9999/resumo", headers=headers(usuario_autenticado))
    assert r.status_code == 404
