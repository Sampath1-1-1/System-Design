-- Extracted from manuscript/book1-traditional/11-relational-databases.md §11.6.2 (listing 2). Edit the manuscript, not this file.
-- Inner join: orders with their customer (orders without a customer cannot exist: FK)
SELECT o.order_id, c.email, o.total_cents
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id;

-- Left outer join: every customer, with order count (0 for customers who never ordered)
SELECT c.customer_id, c.email, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.email;

-- Semi-join: customers who bought product 42 (each customer once, however many orders)
SELECT c.email FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o JOIN order_items i ON i.order_id = o.order_id
              WHERE o.customer_id = c.customer_id AND i.product_id = 42);

-- Anti-join: customers with no orders at all
SELECT c.email FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
