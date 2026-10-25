import jwt
import pytest

from app.schemas import cpf_valido
from tests.conftest import GESTOR_EMAIL, GESTOR_SENHA


def test_registro_cria_cliente(client, comprador):
    resposta = client.post("/auth/registro", json=comprador)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == comprador["email"]
    assert corpo["papel"] == "cliente"
    assert "senha" not in corpo and "senha_hash" not in corpo


def test_registro_duplicado_retorna_409(client, comprador):
    client.post("/auth/registro", json=comprador)
    outro = {**comprador, "email": "outro@exemplo.com"}

    assert client.post("/auth/registro", json=outro).status_code == 409


def test_registro_rejeita_cpf_invalido(client, comprador):
    resposta = client.post("/auth/registro", json={**comprador, "cpf": "123.456.789-00"})

    assert resposta.status_code == 422


def test_login_emite_token_rs256_valido_pelo_jwks(client, comprador, config):
    client.post("/auth/registro", json=comprador)

    resposta = client.post("/auth/login", json={"email": comprador["email"], "senha": comprador["senha"]})

    assert resposta.status_code == 200
    token = resposta.json()["access_token"]
    jwks = client.get("/.well-known/jwks.json").json()
    chave = jwt.PyJWK(jwks["keys"][0]).key
    claims = jwt.decode(token, chave, algorithms=["RS256"], audience=config.jwt_audience, issuer=config.jwt_issuer)
    assert claims["papel"] == "cliente"
    assert jwt.get_unverified_header(token)["kid"] == jwks["keys"][0]["kid"]


def test_token_nao_carrega_dados_pessoais(client, comprador):
    client.post("/auth/registro", json=comprador)
    token = client.post("/auth/login", json={"email": comprador["email"], "senha": comprador["senha"]}).json()[
        "access_token"
    ]

    claims = jwt.decode(token, options={"verify_signature": False})

    assert set(claims) == {"iss", "aud", "sub", "papel", "iat", "exp", "jti"}


def test_login_com_senha_errada_retorna_401(client, comprador):
    client.post("/auth/registro", json=comprador)

    resposta = client.post("/auth/login", json={"email": comprador["email"], "senha": "errada"})

    assert resposta.status_code == 401


def test_gestor_criado_na_subida(client):
    resposta = client.post("/auth/login", json={"email": GESTOR_EMAIL, "senha": GESTOR_SENHA})
    token = resposta.json()["access_token"]

    assert jwt.decode(token, options={"verify_signature": False})["papel"] == "gestor"


def test_me_retorna_dados_do_dono_do_token(client, comprador):
    client.post("/auth/registro", json=comprador)
    token = client.post("/auth/login", json={"email": comprador["email"], "senha": comprador["senha"]}).json()[
        "access_token"
    ]

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == comprador["nome"]


def test_me_sem_token_retorna_401(client):
    assert client.get("/auth/me").status_code == 401


def test_chave_persistida_entre_reinicios(config):
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app(config)) as primeiro:
        kid1 = primeiro.get("/.well-known/jwks.json").json()["keys"][0]["kid"]
    with TestClient(create_app(config)) as segundo:
        kid2 = segundo.get("/.well-known/jwks.json").json()["keys"][0]["kid"]

    assert kid1 == kid2


@pytest.mark.parametrize(
    ("cpf", "esperado"),
    [("52998224725", True), ("11144477735", True), ("11111111111", False), ("52998224724", False), ("123", False)],
)
def test_validacao_cpf(cpf, esperado):
    assert cpf_valido(cpf) is esperado
