import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select

from app.config import Settings
from app.db import Base, criar_fabrica_sessoes
from app.models import Papel, Usuario
from app.routes import router
from app.security import ChaveAssinatura, gerar_hash_senha

logger = logging.getLogger("identidade")


def _criar_gestor(app: FastAPI) -> None:
    config: Settings = app.state.config
    if not config.gestor_password:
        return
    with app.state.sessoes() as sessao:
        if sessao.scalar(select(Usuario).where(Usuario.email == config.gestor_email)):
            return
        sessao.add(
            Usuario(
                nome=config.gestor_nome,
                email=config.gestor_email,
                senha_hash=gerar_hash_senha(config.gestor_password),
                papel=Papel.GESTOR,
            )
        )
        sessao.commit()
        logger.info("Usuário gestor criado: %s", config.gestor_email)


def create_app(config: Settings | None = None) -> FastAPI:
    config = config or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(app.state.sessoes.kw["bind"])
        _criar_gestor(app)
        yield

    app = FastAPI(
        title="Revenda de Veículos - Identidade",
        description="Cadastro e autenticação de compradores. Emite JWT (RS256) e publica o JWKS.",
        version="1.0.0",
        root_path=config.root_path,
        lifespan=lifespan,
    )
    app.state.config = config
    app.state.sessoes = criar_fabrica_sessoes(config.database_url)
    app.state.chave = ChaveAssinatura(Path(config.jwt_private_key_path))
    app.include_router(router)
    Instrumentator().instrument(app).expose(app, include_in_schema=False)
    return app
