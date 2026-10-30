# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.14.3 (listing 18). Edit the manuscript, not this file.
import base64, hashlib, secrets

def make_pkce_pair() -> tuple[str, str]:
    # 32 random bytes -> 43-character base64url verifier (RFC 7636 allows 43-128 chars)
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    return verifier, challenge_for(verifier)

def challenge_for(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

# Test vector from RFC 7636 Appendix B:
assert challenge_for("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk") == \
    "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
