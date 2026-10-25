import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Papel(StrEnum):
    CLIENTE = "cliente"
    GESTOR = "gestor"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    cpf: Mapped[str | None] = mapped_column(String(11), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(20))
    senha_hash: Mapped[str] = mapped_column(String(100))
    papel: Mapped[str] = mapped_column(String(20), default=Papel.CLIENTE)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
