-- Extracted from manuscript/book1-traditional/11-relational-databases.md §11.17.2 (listing 11). Edit the manuscript, not this file.
CREATE TABLE customers (
  customer_id  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email        text NOT NULL UNIQUE,
  full_name    text NOT NULL,
  city         text NOT NULL,
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE products (
  product_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sku          text NOT NULL UNIQUE,
  name         text NOT NULL,
  price_cents  integer NOT NULL CHECK (price_cents >= 0)
);
CREATE TABLE inventory (
  product_id   bigint PRIMARY KEY REFERENCES products,
  on_hand      integer NOT NULL CHECK (on_hand >= 0)
);
CREATE TABLE orders (
  order_id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id      bigint NOT NULL REFERENCES customers,
  status           text NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','paid','shipped','cancelled')),
  ship_to          text NOT NULL,
  total_cents      bigint NOT NULL CHECK (total_cents >= 0),
  idempotency_key  text NOT NULL UNIQUE,
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE order_items (
  order_id          bigint NOT NULL REFERENCES orders ON DELETE CASCADE,
  line_no           smallint NOT NULL,
  product_id        bigint NOT NULL REFERENCES products,
  quantity          integer NOT NULL CHECK (quantity > 0),
  unit_price_cents  integer NOT NULL CHECK (unit_price_cents >= 0),
  PRIMARY KEY (order_id, line_no)
);
CREATE TABLE payments (
  payment_id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id      bigint NOT NULL REFERENCES orders,
  amount_cents  bigint NOT NULL CHECK (amount_cents > 0),
  provider_ref  text UNIQUE,
  status        text NOT NULL CHECK (status IN ('authorized','captured','failed','refunded')),
  created_at    timestamptz NOT NULL DEFAULT now()
);
-- One index per access path
CREATE INDEX orders_customer_created_idx ON orders (customer_id, created_at DESC, order_id DESC); -- history
CREATE INDEX order_items_product_idx     ON order_items (product_id);       -- FK checks, sales by product
CREATE INDEX payments_order_idx          ON payments (order_id);            -- payments of an order
CREATE INDEX orders_pending_created_idx  ON orders (created_at) WHERE status = 'pending'; -- sweeper
