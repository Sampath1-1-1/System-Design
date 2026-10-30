# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.10.2 (listing 11). Edit the manuscript, not this file.
import base64, hashlib, hmac, json, time

SECRET_KEY = b"load-me-from-a-secrets-manager-32+bytes"   # never hard-code in production


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign_session(data: dict, ttl_s: int = 3600) -> str:
    body = _b64(json.dumps({**data, "exp": int(time.time()) + ttl_s}).encode())
    mac = hmac.new(SECRET_KEY, body.encode(), hashlib.sha256).digest()
    return f"{body}.{_b64(mac)}"


def verify_session(cookie: str) -> dict | None:
    try:
        body, mac = cookie.split(".")
    except ValueError:
        return None
    expected = hmac.new(SECRET_KEY, body.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _unb64(mac)):    # constant-time compare
        return None
    data = json.loads(_unb64(body))
    return data if data["exp"] >= time.time() else None
