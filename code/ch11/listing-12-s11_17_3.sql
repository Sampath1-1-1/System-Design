-- Extracted from manuscript/book1-traditional/11-relational-databases.md §11.17.3 (listing 12). Edit the manuscript, not this file.
BEGIN;
INSERT INTO orders (customer_id, ship_to, total_cents, idempotency_key)
VALUES (1, '1 Main St', 0, '7f1c9a52-key')
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING order_id;                       -- no row returned: a retry; fetch and return the existing order
UPDATE inventory SET on_hand = on_hand - 2 WHERE product_id = 1 AND on_hand >= 2;  -- expect 1 row
UPDATE inventory SET on_hand = on_hand - 1 WHERE product_id = 2 AND on_hand >= 1;  -- 0 rows: out of stock, ROLLBACK
INSERT INTO order_items (order_id, line_no, product_id, quantity, unit_price_cents)
SELECT 1, row_number() OVER (ORDER BY v.product_id), v.product_id, v.qty, p.price_cents
FROM (VALUES (1, 2), (2, 1)) AS v(product_id, qty) JOIN products p USING (product_id);
UPDATE orders SET total_cents = (SELECT sum(quantity * unit_price_cents)
                                 FROM order_items WHERE order_id = 1)
WHERE order_id = 1;
COMMIT;
