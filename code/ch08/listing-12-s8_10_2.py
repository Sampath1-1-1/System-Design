# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.10.2 (listing 12). Edit the manuscript, not this file.
from flask import Flask
import os

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["SECRET_KEY"],
    SESSION_COOKIE_SECURE=True,      # only sent over HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # invisible to JavaScript
    SESSION_COOKIE_SAMESITE="Lax",   # not sent on cross-site POSTs
    PERMANENT_SESSION_LIFETIME=3600, # seconds
)
# After login, Flask emits for example:
# Set-Cookie: session=eyJ1aWQiOiJhZGEifQ.auQy5w.2G2C9...; Expires=...; Secure; HttpOnly; Path=/; SameSite=Lax
