import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

GESTOR_EMAIL = "gestor@teste.com"
GESTOR_SENHA = "senha-do-gestor"


@pytest.fixture
def config(tmp_path) -> Settings:
    return Settings(
        _env_file=None,
        database_url=f"sqlite:///{tmp_path / 'teste.db'}",
        jwt_private_key_path=str(tmp_path / "chave.pem"),
        gestor_email=GESTOR_EMAIL,
        gestor_password=GESTOR_SENHA,
    )


@pytest.fixture
def client(config):
    with TestClient(create_app(config)) as cliente:
        yield cliente


@pytest.fixture
def comprador() -> dict:
    return {
        "nome": "Maria Silva",
        "email": "maria@exemplo.com",
        "cpf": "529.982.247-25",
        "telefone": "11999998888",
        "senha": "senha-forte-123",
    }
