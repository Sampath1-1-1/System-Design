# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.14.4 (listing 20). Edit the manuscript, not this file.
curl -s -u billing-service:$CLIENT_SECRET https://auth.example.com/oauth/token \
  -d grant_type=client_credentials -d scope=invoices.write
