# ADR-001: Serviço de identidade próprio com JWT RS256 e JWKS

Status: Aceita

## Contexto

O registro e a autorização de compradores devem ficar totalmente apartados dos dados transacionais de vendas. O enunciado permite Auth0, Cognito, Keycloak ou implementação própria.

## Decisão

Serviço próprio em FastAPI, com banco PostgreSQL exclusivo, que:

- guarda os dados pessoais e o hash bcrypt da senha;
- emite JWT assinado com RS256 (chave assimétrica), contendo só `sub` e `papel` além dos campos técnicos;
- publica a chave pública em `/.well-known/jwks.json`, para que outros serviços validem os tokens sem segredo compartilhado e sem acesso ao banco.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Keycloak | Pesado para a VM (Java, ~500 MB), e o trabalho seria basicamente configurar a ferramenta |
| Cognito / Auth0 | Dependência e configuração de serviço externo; complica rodar localmente |
| HS256 (segredo compartilhado) | Todo serviço que valida o token também poderia emitir tokens; RS256 separa quem assina de quem verifica |

## Consequências

- Isolamento claro e contrato padrão de mercado (OIDC usa o mesmo mecanismo de JWKS): migrar para Keycloak ou Cognito exigiria só trocar a URL do JWKS e o claim de papel na revenda.
- A chave privada é gerada na primeira subida e persistida em volume; rotação de chaves fica como evolução (o JWKS já suporta várias chaves por `kid`).
- Fora do escopo desta versão: refresh token, recuperação de senha, bloqueio por tentativas, MFA e exclusão de conta (direito do titular na LGPD).
