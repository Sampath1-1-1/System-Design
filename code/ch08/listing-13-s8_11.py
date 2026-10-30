# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.11 (listing 13). Edit the manuscript, not this file.
import hashlib, hmac, os

def hash_password(password: str) -> str:
    salt = os.urandom(16)                                    # unique per user
    dk = hashlib.scrypt(password.encode(), salt=salt, n=2**15, r=8, p=1,
                        maxmem=64 * 1024 * 1024)             # ~32 MiB of memory per guess
    return f"scrypt$32768$8$1${salt.hex()}${dk.hex()}"

def verify_password(password: str, stored: str) -> bool:
    _, n, r, p, salt_hex, dk_hex = stored.split("$")
    dk = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex),
                        n=int(n), r=int(r), p=int(p), maxmem=64 * 1024 * 1024)
    return hmac.compare_digest(dk, bytes.fromhex(dk_hex))
