# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.6.5 (listing 4). Edit the manuscript, not this file.
curl -s 'http://localhost:8000/v1/articles?limit=2'
# {"data":[{"id":83,"title":"Article 83","status":"published","created_at":"2026-01-28T10:00:00Z"},
#          {"id":55,...}],"next_cursor":"WyIyMDI2LTAxLTI4VDEwOjAwOjAwWiIsIDU1XQ"}

curl -s 'http://localhost:8000/v1/articles?limit=2&cursor=WyIyMDI2LTAxLTI4VDEwOjAwOjAwWiIsIDU1XQ'

curl -si 'http://localhost:8000/v1/articles/999'
# HTTP/1.1 404 Not Found
# content-type: application/problem+json
# {"type":"about:blank","title":"Not Found","status":404,
#  "detail":"No article with id 999 exists.","instance":"/v1/articles/999"}
