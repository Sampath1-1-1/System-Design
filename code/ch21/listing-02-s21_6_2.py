# Extracted from manuscript/book1-traditional/21-content-delivery-networks.md §21.6.2 (listing 2). Edit the manuscript, not this file.
# Cache-key normalization: map many equivalent requests to one cache key.
from urllib.parse import parse_qsl, urlencode, urlsplit

KEEP_PARAMS = {"v", "lang"}   # allow-list: only params that change the bytes


def cache_key(url, accept_encoding=""):
    parts = urlsplit(url)
    host = parts.hostname.lower()             # hostnames are case-insensitive
    path = parts.path or "/"                  # paths are case-sensitive: keep
    params = sorted((k.lower(), v) for k, v in parse_qsl(parts.query)
                    if k.lower() in KEEP_PARAMS)
    # Collapse Accept-Encoding to the few variants the edge actually stores.
    enc = accept_encoding.lower()
    enc = "br" if "br" in enc else "gzip" if "gzip" in enc else "identity"
    query = urlencode(params)
    return f"{host}{path}" + (f"?{query}" if query else "") + f"|{enc}"


if __name__ == "__main__":
    requests = [
        ("https://CDN.example.com/js/app.js?v=7&lang=en", "gzip, deflate, br"),
        ("https://cdn.example.com/js/app.js?lang=en&v=7&utm_source=mail", "br;q=1.0, gzip;q=0.8"),
        ("https://cdn.example.com/js/app.js?LANG=en&v=7&sessionid=abc123", "br"),
        ("https://cdn.example.com/js/app.js?v=7&lang=en", "gzip, deflate"),
        ("https://cdn.example.com/js/app.js?v=7&lang=en", ""),
    ]
    keys = [cache_key(u, ae) for u, ae in requests]
    for k in keys:
        print(k)
    print("distinct keys:", len(set(keys)), "of", len(keys), "requests")
