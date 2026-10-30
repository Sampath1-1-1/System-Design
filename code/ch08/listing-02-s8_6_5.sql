-- Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.6.5 (listing 2). Edit the manuscript, not this file.
-- Supporting index: the sort order, with id as a unique tie-breaker
CREATE INDEX idx_articles_created_id ON articles (created_at DESC, id DESC);

-- First page
SELECT id, title, created_at
FROM articles
ORDER BY created_at DESC, id DESC
LIMIT 21;                       -- one extra row tells us whether a next page exists

-- Next page: $1, $2 = created_at and id of the last row of the previous page
SELECT id, title, created_at
FROM articles
WHERE (created_at, id) < ($1, $2)    -- row-value comparison: seek, don't skip
ORDER BY created_at DESC, id DESC
LIMIT 21;
