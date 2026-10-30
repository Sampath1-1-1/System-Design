# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.7.1 (listing 6). Edit the manuscript, not this file.
curl -s https://api.example.com/graphql \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOi...' \
  -d '{"query":"query RecentPosts { posts(first: 5) { edges { node { title author { name } } } pageInfo { hasNextPage endCursor } } }"}'
