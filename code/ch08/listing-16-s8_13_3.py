# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.13.3 (listing 16). Edit the manuscript, not this file.
import time, uuid
import jwt                                   # pip install "pyjwt[crypto]"
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ISSUER, AUDIENCE = "https://auth.example.com", "https://api.example.com"

# Authorization server: holds the private key.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_pem = private_key.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

def issue_access_token(user_id: str, scopes: list[str], ttl_s: int = 900) -> str:
    now = int(time.time())
    claims = {"iss": ISSUER, "aud": AUDIENCE, "sub": user_id, "iat": now, "nbf": now,
              "exp": now + ttl_s, "jti": str(uuid.uuid4()), "scope": " ".join(scopes)}
    return jwt.encode(claims, private_key, algorithm="RS256",
                      headers={"kid": "2026-10-key-1"})

# Resource server: holds only the public key.
def validate_access_token(token: str) -> dict:
    return jwt.decode(
        token, public_pem,
        algorithms=["RS256"],               # pin the algorithm; never trust the header
        audience=AUDIENCE, issuer=ISSUER,
        leeway=30,                          # tolerate 30 s of clock skew
        options={"require": ["exp", "iat", "sub", "aud", "iss"]},
    )

token = issue_access_token("user-123", ["articles:read", "articles:write"])
print(len(token), validate_access_token(token)["scope"])   # ~700 articles:read articles:write
