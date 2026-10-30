-- Extracted from manuscript/book1-traditional/11-relational-databases.md §11.14.2 (listing 9). Edit the manuscript, not this file.
INSERT INTO stock VALUES (42, 10);                          -- transaction 993
UPDATE stock SET on_hand = 9 WHERE product_id = 42;         -- transaction 994
UPDATE stock SET on_hand = 8 WHERE product_id = 42;         -- transaction 995
SELECT xmin, xmax, ctid, * FROM stock;                      -- only the visible version
--  xmin | xmax | ctid  | product_id | on_hand
--   995 |    0 | (0,3) |         42 |       8
SELECT lp, t_xmin, t_xmax, t_ctid FROM heap_page_items(get_raw_page('stock', 0));
--  lp | t_xmin | t_xmax | t_ctid
--   1 |    993 |    994 | (0,2)
--   2 |    994 |    995 | (0,3)
--   3 |    995 |      0 | (0,3)
