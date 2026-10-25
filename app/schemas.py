import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def cpf_valido(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(d) * peso for d, peso in zip(cpf[:tamanho], range(tamanho + 1, 1, -1), strict=True))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[tamanho]):
            return False
    return True


class RegistroEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120, examples=["Maria Silva"])
    email: EmailStr = Field(examples=["maria@exemplo.com"])
    cpf: str = Field(examples=["52998224725"], description="Somente números ou com pontuação")
    telefone: str | None = Field(default=None, max_length=20, examples=["11999998888"])
    senha: str = Field(min_length=8, max_length=64)

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, valor: str) -> str:
        digitos = re.sub(r"\D", "", valor)
        if not cpf_valido(digitos):
            raise ValueError("CPF inválido")
        return digitos


class LoginEntrada(BaseModel):
    email: EmailStr = Field(examples=["maria@exemplo.com"])
    senha: str = Field(min_length=1, max_length=64)


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int


class UsuarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    email: str
    papel: str
