# Contrato publicado para outros serviços

Qualquer serviço que precise autenticar compradores depende apenas deste contrato, nunca do banco de identidade.

| Item | Valor |
|---|---|
| Algoritmo | RS256 |
| JWKS (rede interna) | `http://identidade-api:8000/.well-known/jwks.json` |
| JWKS (pelo gateway) | `http://<gateway>/identidade/.well-known/jwks.json` |
| `iss` | `revenda-identidade` |
| `aud` | `revenda-api` |
| Validade (`exp`) | 60 minutos (`JWT_TTL_MINUTOS`) |
| Header | `kid` = identificador da chave no JWKS |

## Claims

| Claim | Exemplo | Significado |
|---|---|---|
| `sub` | `2826194f-d37c-468c-904b-ac1e8884c0f1` | Id opaco do usuário. É o único dado que outros serviços devem guardar |
| `papel` | `cliente` ou `gestor` | Papel para autorização |
| `iat`, `exp` | timestamps | Emissão e expiração |
| `jti` | uuid | Id único do token |

Nenhum dado pessoal (nome, e-mail, CPF, telefone) é incluído no token.

## Como validar (Python)

```python
import jwt
cliente = jwt.PyJWKClient("http://identidade-api:8000/.well-known/jwks.json")
chave = cliente.get_signing_key_from_jwt(token).key
claims = jwt.decode(token, chave, algorithms=["RS256"], issuer="revenda-identidade", audience="revenda-api")
```
