def test_register(client):
    r = client.post("/auth/register", json={
        "nome": "Davi", "email": "davi@teste.com", "senha": "123456"
    })
    assert r.status_code == 201
    assert r.json()["mensagem"] == "Usuário criado"


def test_register_email_duplicado(client):
    dados = {"nome": "Davi", "email": "davi@teste.com", "senha": "123456"}
    client.post("/auth/register", json=dados)
    r = client.post("/auth/register", json=dados)
    assert r.status_code == 400


def test_login_sucesso(client, usuario_autenticado):
    assert "access_token" in usuario_autenticado
    assert "refresh_token" in usuario_autenticado


def test_login_senha_errada(client):
    client.post("/auth/register", json={
        "nome": "Davi", "email": "davi@teste.com", "senha": "correta"
    })
    r = client.post("/auth/login", json={
        "email": "davi@teste.com", "senha": "errada"
    })
    assert r.status_code == 401


def test_refresh_token(client, usuario_autenticado):
    r = client.post("/auth/refresh", json={
        "refresh_token": usuario_autenticado["refresh_token"]
    })
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert "refresh_token" in r.json()


def test_refresh_token_invalido(client):
    r = client.post("/auth/refresh", json={"refresh_token": "token-invalido"})
    assert r.status_code == 401


def test_logout(client, usuario_autenticado):
    r = client.post("/auth/logout", json={
        "refresh_token": usuario_autenticado["refresh_token"]
    })
    assert r.status_code == 200

    # Após logout, refresh token não pode ser reutilizado
    r2 = client.post("/auth/refresh", json={
        "refresh_token": usuario_autenticado["refresh_token"]
    })
    assert r2.status_code == 401


def test_rota_protegida_sem_token(client):
    r = client.get("/transcricoes")
    assert r.status_code == 403


def test_rota_protegida_com_token(client, usuario_autenticado):
    headers = {"Authorization": f"Bearer {usuario_autenticado['access_token']}"}
    r = client.get("/transcricoes", headers=headers)
    assert r.status_code == 200
