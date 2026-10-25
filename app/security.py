import base64
import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# bcrypt considera no máximo 72 bytes da senha
_LIMITE_BCRYPT = 72


def gerar_hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode()[:_LIMITE_BCRYPT], bcrypt.gensalt()).decode()


def senha_confere(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode()[:_LIMITE_BCRYPT], senha_hash.encode())


def _b64url(valor: bytes) -> str:
    return base64.urlsafe_b64encode(valor).rstrip(b"=").decode()


def _int_b64url(numero: int) -> str:
    return _b64url(numero.to_bytes((numero.bit_length() + 7) // 8, "big"))


class ChaveAssinatura:
    def __init__(self, caminho: Path) -> None:
        if caminho.exists():
            self._privada = serialization.load_pem_private_key(caminho.read_bytes(), password=None)
        else:
            self._privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_bytes(
                self._privada.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
            caminho.chmod(0o600)
        publica_der = self._privada.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.kid = _b64url(hashlib.sha256(publica_der).digest())[:16]

    @property
    def publica(self) -> rsa.RSAPublicKey:
        return self._privada.public_key()

    def jwks(self) -> dict:
        numeros = self.publica.public_numbers()
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": "RS256",
                    "kid": self.kid,
                    "n": _int_b64url(numeros.n),
                    "e": _int_b64url(numeros.e),
                }
            ]
        }

    def emitir(self, *, sub: str, papel: str, issuer: str, audience: str, ttl_minutos: int) -> str:
        agora = datetime.now(UTC)
        claims = {
            "iss": issuer,
            "aud": audience,
            "sub": sub,
            "papel": papel,
            "iat": agora,
            "exp": agora + timedelta(minutes=ttl_minutos),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(claims, self._privada, algorithm="RS256", headers={"kid": self.kid})

    def validar(self, token: str, *, issuer: str, audience: str) -> dict:
        return jwt.decode(token, self.publica, algorithms=["RS256"], issuer=issuer, audience=audience)
