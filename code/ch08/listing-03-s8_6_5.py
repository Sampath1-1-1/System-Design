# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.6.5 (listing 3). Edit the manuscript, not this file.
# articles_api.py — run with:  pip install fastapi uvicorn  &&  uvicorn articles_api:app
import base64
import json
import sqlite3

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Articles API", version="1.0.0")

# In-memory database so the example is self-contained.
db = sqlite3.connect(":memory:", check_same_thread=False)
db.row_factory = sqlite3.Row
db.executescript("""
CREATE TABLE articles (
    id         INTEGER PRIMARY KEY,
    title      TEXT    NOT NULL,
    status     TEXT    NOT NULL,
    created_at TEXT    NOT NULL           -- ISO-8601 UTC timestamp
);
CREATE INDEX idx_articles_created_id ON articles (created_at DESC, id DESC);
""")
db.executemany(
    "INSERT INTO articles (id, title, status, created_at) VALUES (?, ?, ?, ?)",
    [(i, f"Article {i}", "draft" if i % 3 == 0 else "published",
      f"2026-01-{i % 28 + 1:02d}T10:00:00Z") for i in range(1, 101)],
)


class Problem(Exception):
    """An error that is rendered as RFC 9457 problem details."""
    def __init__(self, status: int, title: str, detail: str,
                 type_: str = "about:blank"):
        self.status, self.title, self.detail, self.type_ = status, title, detail, type_


@app.exception_handler(Problem)
async def problem_handler(request: Request, exc: Problem) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        media_type="application/problem+json",
        content={"type": exc.type_, "title": exc.title, "status": exc.status,
                 "detail": exc.detail, "instance": request.url.path},
    )


def encode_cursor(created_at: str, row_id: int) -> str:
    raw = json.dumps([created_at, row_id]).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[str, int]:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        created_at, row_id = json.loads(base64.urlsafe_b64decode(padded))
        return str(created_at), int(row_id)
    except Exception:
        raise Problem(400, "Invalid cursor",
                      "The cursor parameter is malformed or expired.",
                      "https://api.example.com/problems/invalid-cursor")


@app.get("/v1/articles")
def list_articles(
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
    status: str | None = Query(None, pattern="^(draft|published)$"),
):
    where, params = [], []
    if status is not None:
        where.append("status = ?")
        params.append(status)
    if cursor is not None:
        created_at, last_id = decode_cursor(cursor)
        where.append("(created_at, id) < (?, ?)")      # keyset predicate
        params += [created_at, last_id]

    sql = "SELECT id, title, status, created_at FROM articles"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
    params.append(limit + 1)                            # fetch one extra row

    rows = db.execute(sql, params).fetchall()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = (encode_cursor(rows[-1]["created_at"], rows[-1]["id"])
                   if has_more else None)
    return {"data": [dict(r) for r in rows], "next_cursor": next_cursor}


@app.get("/v1/articles/{article_id}")
def get_article(article_id: int):
    row = db.execute("SELECT id, title, status, created_at FROM articles WHERE id = ?",
                     (article_id,)).fetchone()
    if row is None:
        raise Problem(404, "Not Found", f"No article with id {article_id} exists.")
    return dict(row)
