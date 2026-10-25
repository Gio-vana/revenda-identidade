from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.models import Papel, Usuario
from app.schemas import LoginEntrada, RegistroEntrada, TokenSaida, UsuarioSaida
from app.security import gerar_hash_senha, senha_confere

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

SessaoDep = Annotated[Session, Depends(obter_sessao)]


@router.post(
    "/auth/registro",
    response_model=UsuarioSaida,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticação"],
    summary="Cadastrar comprador",
)
def registrar(dados: RegistroEntrada, sessao: SessaoDep) -> Usuario:
    existente = sessao.scalar(
        select(Usuario).where(or_(Usuario.email == dados.email.lower(), Usuario.cpf == dados.cpf))
    )
    if existente:
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail ou CPF já cadastrado")
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email.lower(),
        cpf=dados.cpf,
        telefone=dados.telefone,
        senha_hash=gerar_hash_senha(dados.senha),
        papel=Papel.CLIENTE,
    )
    sessao.add(usuario)
    sessao.commit()
    return usuario


@router.post("/auth/login", response_model=TokenSaida, tags=["Autenticação"], summary="Obter token")
def login(dados: LoginEntrada, sessao: SessaoDep, request: Request) -> TokenSaida:
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == dados.email.lower()))
    if not usuario or not senha_confere(dados.senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
    config = request.app.state.config
    token = request.app.state.chave.emitir(
        sub=usuario.id,
        papel=usuario.papel,
        issuer=config.jwt_issuer,
        audience=config.jwt_audience,
        ttl_minutos=config.jwt_ttl_minutos,
    )
    return TokenSaida(access_token=token, expires_in=config.jwt_ttl_minutos * 60)


@router.get("/auth/me", response_model=UsuarioSaida, tags=["Autenticação"], summary="Meus dados")
def me(
    sessao: SessaoDep,
    request: Request,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Usuario:
    if credenciais is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token ausente")
    config = request.app.state.config
    try:
        claims = request.app.state.chave.validar(
            credenciais.credentials, issuer=config.jwt_issuer, audience=config.jwt_audience
        )
    except jwt.InvalidTokenError as erro:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido") from erro
    usuario = sessao.get(Usuario, claims["sub"])
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado")
    return usuario


@router.get("/.well-known/jwks.json", tags=["Chaves públicas"], summary="JWKS para validar tokens")
def jwks(request: Request) -> dict:
    return request.app.state.chave.jwks()


@router.get("/health", tags=["Saúde"], include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}
