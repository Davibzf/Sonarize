import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(bind=engine_test, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def usuario_autenticado(client):
    client.post("/auth/register", json={
        "nome": "Davi",
        "email": "davi@teste.com",
        "senha": "senha123"
    })
    resp = client.post("/auth/login", json={
        "email": "davi@teste.com",
        "senha": "senha123"
    })
    return resp.json()
