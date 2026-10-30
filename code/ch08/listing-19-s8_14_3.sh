# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.14.3 (listing 19). Edit the manuscript, not this file.
curl -s https://auth.example.com/oauth/token \
  -d grant_type=authorization_code \
  -d code=SplxlOBeZQQYbYS6WxSbIA \
  -d redirect_uri=https://app.example.com/callback \
  -d client_id=photo-printer \
  -d code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
# {"access_token":"eyJhbGciOi...","token_type":"Bearer","expires_in":900,
#  "refresh_token":"8xLOxBtZp8...","scope":"photos.read"}
