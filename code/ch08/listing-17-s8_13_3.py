# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.13.3 (listing 17). Edit the manuscript, not this file.
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
bearer = HTTPBearer(auto_error=False)

def current_claims(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if creds is None:
        raise HTTPException(401, "Missing bearer token",
                            headers={"WWW-Authenticate": 'Bearer realm="api"'})
    try:
        return validate_access_token(creds.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid or expired token",
                            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'})

def require_scope(scope: str):
    def checker(claims: dict = Depends(current_claims)) -> dict:
        if scope not in claims.get("scope", "").split():
            raise HTTPException(403, f"Requires scope {scope}", headers={
                "WWW-Authenticate": f'Bearer error="insufficient_scope", scope="{scope}"'})
        return claims
    return checker

@app.delete("/v1/articles/{article_id}", status_code=204)
def delete_article(article_id: int, claims: dict = Depends(require_scope("articles:delete"))):
    ...   # delete, recording claims["sub"] in the audit log
