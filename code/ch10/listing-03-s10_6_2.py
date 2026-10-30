# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.6.2 (listing 3). Edit the manuscript, not this file.
"""Password hashing with scrypt (standard library) and Argon2id (cryptography >= 44)."""
import base64
import hashlib
import hmac
import os
import time

# ---------- scrypt (stdlib) ----------
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2**17, 8, 1   # OWASP minimum: N=2^17, r=8, p=1
SCRYPT_MAXMEM = 256 * 1024 * 1024            # memory needed is ~128*N*r = 128 MiB

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode().rstrip("=")

def unb64(s: str) -> bytes:
    return base64.b64decode(s + "=" * (-len(s) % 4))

def scrypt_hash(password: str) -> str:
    salt = os.urandom(16)                                   # unique per password
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt,
                        n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P,
                        maxmem=SCRYPT_MAXMEM, dklen=32)
    # Store algorithm, parameters, salt and hash together so they can evolve.
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${b64(salt)}${b64(dk)}"

def scrypt_verify(password: str, stored: str) -> bool:
    alg, n, r, p, salt_s, dk_s = stored.split("$")
    if alg != "scrypt":
        raise ValueError("unknown algorithm")
    n, r, p = int(n), int(r), int(p)
    candidate = hashlib.scrypt(password.encode("utf-8"), salt=unb64(salt_s),
                               n=n, r=r, p=p,
                               maxmem=max(SCRYPT_MAXMEM, 256 * n * r), dklen=32)
    return hmac.compare_digest(candidate, unb64(dk_s))      # constant-time compare

def needs_rehash(stored: str) -> bool:
    _, n, r, p, *_ = stored.split("$")
    return (int(n), int(r), int(p)) != (SCRYPT_N, SCRYPT_R, SCRYPT_P)

# ---------- Argon2id (cryptography library) ----------
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.exceptions import InvalidKey

ARGON_T, ARGON_M_KIB, ARGON_P = 2, 19 * 1024, 1   # OWASP minimum: m=19 MiB, t=2, p=1

def argon2id_hash(password: str) -> str:
    salt = os.urandom(16)
    kdf = Argon2id(salt=salt, length=32, iterations=ARGON_T,
                   lanes=ARGON_P, memory_cost=ARGON_M_KIB)
    tag = kdf.derive(password.encode("utf-8"))
    return f"argon2id${ARGON_M_KIB}${ARGON_T}${ARGON_P}${b64(salt)}${b64(tag)}"

def argon2id_verify(password: str, stored: str) -> bool:
    alg, m, t, p, salt_s, tag_s = stored.split("$")
    if alg != "argon2id":
        raise ValueError("unknown algorithm")
    kdf = Argon2id(salt=unb64(salt_s), length=32, iterations=int(t),
                   lanes=int(p), memory_cost=int(m))
    try:
        kdf.verify(password.encode("utf-8"), unb64(tag_s))  # constant-time inside
        return True
    except InvalidKey:
        return False
