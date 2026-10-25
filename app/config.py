from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração lida de variáveis de ambiente (ou do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./identidade.db"

    # Contrato do token consumido pela API da revenda
    jwt_issuer: str = "revenda-identidade"
    jwt_audience: str = "revenda-api"
    jwt_ttl_minutos: int = 60
    # Chave privada RSA; é gerada no primeiro start se não existir
    jwt_private_key_path: str = "./keys/jwt-private.pem"

    # Usuário gestor criado na subida (sem senha, nenhum gestor é criado)
    gestor_nome: str = "Gestor da Loja"
    gestor_email: str = "gestor@revenda.com.br"
    gestor_password: str | None = None

    # Prefixo publicado pelo API Gateway (ex.: /identidade), usado pelo Swagger
    root_path: str = ""
