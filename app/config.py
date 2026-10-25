from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./identidade.db"

    jwt_issuer: str = "revenda-identidade"
    jwt_audience: str = "revenda-api"
    jwt_ttl_minutos: int = 60
    # gerada na primeira execução se não existir
    jwt_private_key_path: str = "./keys/jwt-private.pem"

    # sem senha definida, o gestor não é criado
    gestor_nome: str = "Gestor da Loja"
    gestor_email: str = "gestor@revenda.com.br"
    gestor_password: str | None = None

    # prefixo do Kong (/identidade), necessário para o Swagger funcionar atrás do gateway
    root_path: str = ""
