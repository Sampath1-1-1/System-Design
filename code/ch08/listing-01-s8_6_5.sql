-- Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.6.5 (listing 1). Edit the manuscript, not this file.
-- Page 3 of 20 items, newest first (PostgreSQL)
SELECT id, title, created_at
FROM articles
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 40;
