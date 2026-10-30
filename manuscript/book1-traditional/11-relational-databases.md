# Chapter 11 — Relational Databases

> **Level:** 1–2 · **Track:** A (Traditional) · **Estimated reading time:** 5 h

Almost every system you will design has a relational database somewhere in it. The orders in a shop, the balances in a bank, the users of a social network and the configuration of a cloud platform usually live in PostgreSQL, MySQL or a database that speaks their SQL dialect. Relational databases have been the default for fifty years because they solve three hard problems at once: they let you describe *what* data you want without saying *how* to fetch it, they keep data correct while thousands of clients change it concurrently, and they keep committed data safe through crashes.

This chapter explains how they do it, using one running example: the order system of an online shop. You will learn to model its data, index it, read query plans, choose isolation levels and avoid costly concurrency bugs. On-disk internals (write-ahead logging, buffer pools, LSM trees) are covered in Chapter 13, replication and sharding in Chapter 14, and distributed transactions in Chapter 28.

## 11.1 Learning objectives

After this chapter you should be able to:

- Explain the relational model and choose primary keys (natural or surrogate) and foreign keys.
- Normalize a schema to BCNF using functional dependencies, and justify each deliberate denormalization.
- Write inner, outer, semi- and anti-joins, and estimate the I/O cost of nested-loop, hash and sort-merge joins.
- Design clustered, secondary, composite, covering and partial indexes for a stated query workload.
- Compute B+ tree height and I/Os per lookup from page size, key size and row count.
- Read a PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` plan and diagnose a cardinality misestimate.
- Define ACID precisely and distinguish ACID consistency from consistency in distributed systems.
- Reproduce dirty reads, non-repeatable reads, phantoms, lost updates and write skew, and state which isolation level prevents each in PostgreSQL and MySQL.
- Explain MVCC in PostgreSQL (tuple versions, `xmin`/`xmax`, VACUUM) and InnoDB (undo logs, purge).
- Explain two-phase locking, gap locks and deadlock detection, and avoid deadlocks and hot-row contention.
- Produce an end-to-end schema, DDL and queries for an e-commerce order system.

## 11.2 Prerequisites

- Logarithms and B-tree fan-out — §4.4 (index height is a logarithm with a large base).
- Storage devices and latency numbers — §5.6, §4.17 (a random SSD read costs ~100 µs; RAM ~100 ns).
- Page cache and `fsync` — §6.6, §6.14 (durability depends on forcing the log to disk).
- Race conditions, mutexes and deadlock — §6.9–§6.11 (database locking applies the same ideas to rows).
- Keyset pagination — §8.6.5 (we reuse it in the order-history query).
- Idempotency keys — §8.6.3 and §22.15 (the order API must be safe to retry).

## 11.3 The relational model: tables, rows and columns

### 11.3.1 Relations, tuples and attributes

::: definition
**Definition — Relation.** A **relation** is a named set of **tuples** that share the same **attributes**. Each attribute has a name and a **domain** (the set of allowed values, such as 64-bit integers). In SQL a relation is a **table**, a tuple is a **row** and an attribute is a **column**. The relation's name and attributes together form its **schema**; the set of rows at a moment is its **instance**.
:::

#### First-principles explanation

A table looks like a spreadsheet, but three differences matter. A relation is a *set*: rows have no inherent order and are identified by their values (a key), never by "row 17". Every column has a fixed type, enforced on every write. And relationships are expressed by *values*: an order row stores the customer's ID, not a pointer. These properties let the query optimizer rearrange *how* a question is answered without changing the answer.

#### Why does this exist?

Before 1970, hierarchical (IBM IMS) and network (CODASYL) databases linked records by physical pointers, and programs *navigated* them: "go to customer 42, follow the first-order pointer...". Reorganizing storage broke the programs. Codd's paper "A Relational Model of Data for Large Shared Data Banks" proposed that users should see only relations, and that access paths should be the database's private business [Codd 1970]. This **physical data independence** is why you can add an index to a production table today and every existing query keeps working, only faster.

#### How it works internally

1. You state *what* you want in SQL, a declarative language first built at IBM for System R.
2. The database translates it into **relational algebra**: selection σ (filter rows), projection π (choose columns), join ⋈, union, difference and aggregation.
3. Algebraic equivalences ("filter before joining", "join A with B before C") let the optimizer generate equivalent plans and pick the cheapest (§11.10).
4. The executor runs that plan against physical structures (heap files, B+ trees) that the query never mentions (§11.9).

#### NULL and three-valued logic

SQL adds **NULL**, meaning "unknown or not applicable". Any comparison with NULL yields UNKNOWN, not TRUE or FALSE, and `WHERE` keeps only rows whose condition is TRUE.

::: mistake
**Mistake — `WHERE coupon_code <> 'SPRING'` returns orders without a coupon.** It does not: for rows where `coupon_code` is NULL, the comparison is UNKNOWN and the row is dropped. Write `WHERE coupon_code IS DISTINCT FROM 'SPRING'` (PostgreSQL, SQLite) or add `OR coupon_code IS NULL`. Likewise `NOT IN (subquery)` returns no rows if the subquery yields a single NULL; prefer `NOT EXISTS`.
:::

## 11.4 Keys: primary, foreign, natural and surrogate

### 11.4.1 Superkeys, candidate keys and primary keys

::: definition
**Definition — Keys.** A **superkey** is a set of columns whose values are unique across all rows. A **candidate key** is a minimal superkey: remove any column and it stops being unique. The **primary key** is the candidate key chosen as the row's main identifier; it must be unique and NOT NULL. Other candidate keys are enforced with `UNIQUE` constraints. A **foreign key** is a column (or set) in one table whose values must match a key of another table, a rule called **referential integrity**.
:::

In the shop, `customers` has two candidate keys: `customer_id` and `email`. We choose `customer_id` as the primary key and declare `email` `UNIQUE`. `orders.customer_id` is a foreign key to `customers.customer_id`: the database rejects an order for a customer that does not exist, and rejects deleting a customer who still has orders unless you specify otherwise.

The **referential action** says what happens to child rows when a parent is deleted: `NO ACTION`/`RESTRICT` (reject; the default), `CASCADE`, `SET NULL` or `SET DEFAULT`. Use `CASCADE` for true ownership (an order owns its items) and the default for independent entities (deactivate products rather than delete them).

#### Code example

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
PRAGMA foreign_keys = ON;            -- SQLite enforces FKs only when this is set
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers (customer_id)
);
INSERT INTO customers VALUES (1, 'ana@example.com');
INSERT INTO orders VALUES (100, 1);
""")
for sql in ["INSERT INTO orders VALUES (101, 99)",                    # no customer 99
            "INSERT INTO customers VALUES (2, 'ana@example.com')",   # duplicate candidate key
            "DELETE FROM customers WHERE customer_id = 1"]:          # still has an order
    try:
        db.execute(sql)
    except sqlite3.IntegrityError as e:
        print(f"{sql[:40]:<42} -> {e}")
```

What to notice:

- All three statements fail with `IntegrityError`: the database, not application code, guards the invariants. Output: `FOREIGN KEY constraint failed`, `UNIQUE constraint failed: customers.email`, `FOREIGN KEY constraint failed`.
- SQLite enforces foreign keys only after `PRAGMA foreign_keys = ON`, per connection. PostgreSQL and MySQL (InnoDB) always enforce them.
- Foreign-key checks cost an index lookup on the parent for every child insert. PostgreSQL does **not** automatically index the *child* column (`orders.customer_id`); without that index, deleting a customer scans the whole `orders` table. Index foreign-key columns you join or delete through.

### 11.4.2 Natural versus surrogate keys

::: definition
**Definition — Natural and surrogate keys.** A **natural key** is a candidate key with business meaning (email address, ISBN, country code). A **surrogate key** is a meaningless value generated by the system (an auto-increment integer, a UUID) whose only job is identification.
:::

Business identifiers change (people change email addresses; product codes are reissued), and every foreign key that copied the old value must change too. Surrogate keys never change, are compact and make joins cheap. The common rule: a surrogate primary key, plus a `UNIQUE` constraint on the natural key. Natural keys suit small, stable code tables (ISO country or currency codes).

The *kind* of surrogate matters for B+ tree indexes (§11.8). Sequential integers always insert at the right-most leaf, so pages fill completely and stay hot in cache. Random UUIDv4 values insert into a random leaf, causing page splits, half-empty pages and a working set as large as the whole index. Time-ordered identifiers (UUIDv7, Snowflake-style IDs; §17.10) keep the insert locality of integers while being globally unique without a central counter.

**Table 11.1 — Choosing a primary key.**

| Key type | Size | Insert locality in B+ tree | Globally unique | Leaks information | Choose when |
|---|---|---|---|---|---|
| Natural key (email, SKU) | Variable | Random | Within domain | Yes (it is data) | Small stable code tables |
| `bigint` identity / auto-increment | 8 bytes | Sequential (excellent) | Per table only | Row count, growth rate | Single database, default choice |
| UUIDv4 | 16 bytes | Random (poor) | Yes | No | IDs generated offline by clients; small tables |
| UUIDv7 / Snowflake-style | 16 / 8 bytes | Roughly sequential | Yes | Creation time | Many writers or shards (§17.10) |

::: industry
**Instagram — sharded PostgreSQL with time-ordered 64-bit IDs.** Instagram described generating primary keys inside PostgreSQL with a function that packs 41 bits of milliseconds since a custom epoch, 13 bits of logical shard ID and 10 bits of a per-shard sequence. IDs sort by time (good B+ tree locality, cheap "newest first" queries), fit in a `bigint`, and need no central ID service. The trade-off is that IDs reveal creation time and that the bit budget caps per-shard throughput at 1,024 IDs per millisecond.
*Evidence: Primary* — [Instagram Engineering 2012]
:::

::: mistake
**Mistake — "UUIDs are slow, never use them."** The cost is randomness, not size. A UUIDv4 primary key in InnoDB, where the primary key *is* the storage order (§11.7), scatters inserts across the whole table; a UUIDv7 key does not.
:::

## 11.5 Normalization and denormalization

### 11.5.1 Redundancy and the three anomalies

#### First-principles explanation

Imagine the shop's first version kept one spreadsheet row per order line, with the customer's email and the product's name copied into every row. When Ana changes her email, 40 rows must change; miss one and the database holds two "truths". Normalization's goal is that **every fact is stored exactly once**.

Redundant designs suffer three **anomalies**:

1. **Update anomaly** — changing one fact requires changing many rows; a partial update leaves contradictions.
2. **Insert anomaly** — you cannot record a fact without an unrelated one: a new product cannot be stored until somebody orders it.
3. **Delete anomaly** — deleting one fact destroys another: cancelling and purging the only order of a product loses the product's name and price.

::: definition
**Definition — Functional dependency.** In a relation $R$, the functional dependency $X \to Y$ holds if any two rows that agree on the columns $X$ also agree on the columns $Y$. $X$ is the **determinant**. Example: `product_id → product_name` because one product ID always has one name.
:::

### 11.5.2 The normal forms

::: definition
**Definition — Normal forms (1NF to BCNF).**
**1NF:** every column holds a single atomic value (no lists or repeating groups).
**2NF:** 1NF, and no non-key column depends on only *part* of a composite candidate key.
**3NF:** 2NF, and no non-key column depends on another non-key column (no transitive dependency); formally, for every non-trivial $X \to A$, either $X$ is a superkey or $A$ is part of some candidate key.
**BCNF (Boyce–Codd normal form):** for every non-trivial $X \to A$, $X$ is a superkey. BCNF removes 3NF's exception for key columns.
:::

Kent's one-line summary of 2NF and 3NF is that every non-key column must provide a fact about "the key, the whole key, and nothing but the key" [Kent 1983]. Higher forms (4NF, 5NF) deal with multi-valued and join dependencies and rarely matter in application design.

**Table 11.2 — Normal forms at a glance.**

| Form | Forbids | Typical symptom | Fix |
|---|---|---|---|
| 1NF | Lists or repeating groups in a column | `items = 'MUG-1x2; TEE-1x1'` | One row per item |
| 2NF | Dependency on part of a composite key | Product name repeated on every order line | Move to a table keyed by the part |
| 3NF | Non-key → non-key dependency | Customer email repeated on every order | Move to a table keyed by the determinant |
| BCNF | Any determinant that is not a superkey | Overlapping candidate keys (see below) | Split on the offending dependency |

### 11.5.3 Worked decomposition: from a flat export to BCNF

::: example
**Worked example — Normalizing the shop's order export.** The legacy export has one row per order line:

`order_lines_flat(order_id, order_date, customer_id, customer_email, customer_city, product_id, product_name, list_price_cents, quantity, unit_price_cents)`

*Step 1 — 1NF.* An even older format stored all items of an order in one text cell. Splitting that cell into one row per product makes every value atomic, giving the table above.

*Step 2 — List the functional dependencies.* From the business rules:
- FD1: `order_id → order_date, customer_id`
- FD2: `customer_id → customer_email, customer_city`
- FD3: `customer_email → customer_id` (emails are unique)
- FD4: `product_id → product_name, list_price_cents`
- FD5: `order_id, product_id → quantity, unit_price_cents` (one line per product per order)

The only candidate key is `{order_id, product_id}`: together they determine every column, and neither does alone.

*Step 3 — 2NF.* FD1 and FD4 have determinants that are *part* of the key, so `order_date`, the customer columns and the product columns depend on part of the key. Split each partial dependency into its own table:
- `orders_wide(order_id, order_date, customer_id, customer_email, customer_city)`
- `products(product_id, product_name, list_price_cents)`
- `order_lines(order_id, product_id, quantity, unit_price_cents)`

*Step 4 — 3NF.* In `orders_wide`, `order_id → customer_id → customer_email, customer_city` is a transitive dependency. Split on FD2:
- `orders(order_id, order_date, customer_id)`
- `customers(customer_id, customer_email, customer_city)`

*Step 5 — BCNF check.* In `customers`, the determinants are `customer_id` and `customer_email`, both candidate keys. In every other table the only determinant is the primary key. All five tables are in BCNF.

*Step 6 — Lossless-join check.* A split of $R$ into $R_1$ and $R_2$ is **lossless** (joining them back reproduces exactly the original rows, no more, no fewer) if the shared columns form a key of at least one side. Each split above shares a column that is a key of one side (`order_id`, `product_id`, `customer_id`), so joining the five tables reproduces the export exactly.

**Interpretation.** Ana's email is now stored once, products exist without orders, and deleting an order never loses product data. **Engineering implication.** Notice that `unit_price_cents` stayed in `order_lines` while `list_price_cents` moved to `products`. They are different facts: the price *charged* on that day versus the price *today*. Copying the price into the order line is not redundancy; it is history, and dropping it would make every past invoice change whenever marketing changes a price.
:::

**Figure 11.1 — Decomposing the flat order export into BCNF tables.**

```mermaid
flowchart LR
  F["order_lines_flat<br/>key: order_id + product_id"] -->|"split FD1: 2NF"| OW["orders_wide<br/>key: order_id"]
  F -->|"split FD4: 2NF"| P[("products<br/>key: product_id")]
  F -->|"keep FD5"| OL[("order_lines<br/>key: order_id + product_id")]
  OW -->|"split FD2: 3NF"| O[("orders<br/>key: order_id")]
  OW -->|"split FD2: 3NF"| C[("customers<br/>key: customer_id")]
  OL -.->|"FK order_id"| O
  OL -.->|"FK product_id"| P
  O -.->|"FK customer_id"| C
```

**Reading the diagram.** The rectangle on the left is the unnormalized input, middle rectangles are intermediate tables and cylinders are the final BCNF tables. Solid arrows are decomposition steps labeled with the dependency that justified them; dotted arrows are the foreign keys that make the decomposition lossless. These are join paths, not runtime flows, so there is no synchronous or asynchronous traffic here. The risk a decomposition introduces is a lost dependency (§11.5.4); the scaling cost is one more join per extra table, which denormalization later buys back.

### 11.5.4 When BCNF and 3NF disagree

Most 3NF schemas are already in BCNF; the exception needs overlapping candidate keys. Suppose each delivery depot is run by one carrier (`depot → carrier`) and each carrier serves a postal code from one depot (`postal_code, carrier → depot`). In `coverage(postal_code, carrier, depot)` the candidate keys are `{postal_code, carrier}` and `{postal_code, depot}`, so `depot → carrier` violates BCNF but not 3NF (`carrier` is part of a key). Splitting into `depots(depot, carrier)` and `coverage(postal_code, depot)` reaches BCNF but `postal_code, carrier → depot` can no longer be enforced by a unique constraint. BCNF decomposition is always lossless but not always **dependency-preserving**; 3NF can always achieve both [Ramakrishnan and Gehrke 2003].

### 11.5.5 Denormalization

::: definition
**Definition — Denormalization.** Deliberately storing a fact more than once, or storing a derived value, to make important reads cheaper, while accepting the cost of keeping the copies consistent.
:::

Normalization optimizes for correct, cheap writes; some read paths (a product page with its review count, a revenue dashboard) would then need large joins or aggregations on every request. Common forms of denormalization:

1. **Stored aggregates** — `orders.total_cents`, `products.review_count`, updated in the same transaction as the rows they summarize.
2. **Copied columns** — `order_lines.product_name` kept so invoices render without a join (and, like the unit price, it is also a historical fact).
3. **Materialized views** — a stored query result, refreshed periodically (`REFRESH MATERIALIZED VIEW CONCURRENTLY` in PostgreSQL).
4. **Read models outside the database** — caches (Chapter 20), search indexes (Chapter 16) or CQRS projections fed by change data capture (§32.4, §32.6). These are updated asynchronously and are therefore eventually consistent.

::: recommendation
**Recommendation — Normalize the source of truth; denormalize with an owner.** Add a redundant copy only for a measured read problem, and name what keeps it consistent: the same transaction, a trigger, or an asynchronous pipeline (eventually consistent, needs a reconciliation job). A copy with no owner will drift.
:::

**Table 11.3 — Failure scenarios in schema design.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Two customers rows with the same email | Natural key not declared `UNIQUE` | Duplicate-detection query; login bugs | Merge rows, repoint FKs | `UNIQUE` on every candidate key |
| Denormalized total disagrees with items | Update path forgot the aggregate | Nightly reconciliation query | Recompute from source rows | Update in the same transaction; reconciliation job |
| Old invoices change when prices change | Price stored only in `products` | Customer complaints, audit | Restore from backups or logs | Store price-at-purchase in `order_lines` |
| Orphaned order lines | No FK constraint | Anti-join `NOT EXISTS` check | Delete or repair orphans | Declare FKs; `ON DELETE CASCADE` for owned rows |

## 11.6 SQL and joins

### 11.6.1 SQL as a declarative language

::: definition
**Definition — SQL.** The Structured Query Language, standardized by ANSI/ISO, with sublanguages for defining schema (DDL: `CREATE`, `ALTER`, `DROP`), manipulating data (DML: `SELECT`, `INSERT`, `UPDATE`, `DELETE`) and controlling transactions (`BEGIN`, `COMMIT`, `ROLLBACK`). Every major database implements the core standard plus its own dialect.
:::

A `SELECT` is evaluated, logically, in the order `FROM`/`JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`, which is why a `SELECT` alias cannot be used in `WHERE`. The physical execution order may differ (a filter pushed below a join) as long as the result is identical.

### 11.6.2 Join types

A **join** combines rows from two tables that satisfy a condition. Using the shop tables:

```sql
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
```

What to notice:

- `COUNT(o.order_id)` counts non-NULL values, so customers with no orders get 0; `COUNT(*)` would wrongly give 1, because the outer join produces one row padded with NULLs.
- `EXISTS` expresses "at least one match" without duplicating the customer per matching row; a plain join followed by `DISTINCT` gives the same answer with more work.
- A `RIGHT JOIN` is a left join with the tables swapped; a `FULL OUTER JOIN` keeps unmatched rows from both sides. All four statements run unchanged in SQLite and PostgreSQL.

### 11.6.3 Join algorithms

The SQL says *what* to join; the database picks *how*. There are three families, and every relational engine uses some of them [Ramakrishnan and Gehrke 2003; Graefe 1993].

#### First-principles explanation

To match 1,000 wedding guests to their table assignments, you could read the whole assignment list once per guest (**nested loop**), file the assignments on cards by surname and look each guest up (**hash join**), or sort both lists and walk them together (**sort-merge join**). The fastest choice depends on list sizes, existing order and desk space (memory).

#### How it works internally

1. **Nested-loop join (NLJ).** For each row of the *outer* input, scan the *inner* input and emit matching pairs. **Block NLJ** reads the outer side in memory-sized chunks so the inner side is scanned once per chunk instead of once per row. **Index NLJ** replaces the inner scan with an index lookup: for each outer row, descend the inner table's B+ tree on the join column. Index NLJ is the best algorithm when the outer side is small, which is the case for most OLTP queries ("this customer's orders").
2. **Hash join.** *Build* phase: read the smaller input and insert each row into an in-memory hash table keyed on the join column. *Probe* phase: stream the larger input and look up each row's key. It needs an equality condition. If the build side does not fit in memory, both inputs are first **partitioned** by a hash of the key into spill files on disk so that each partition pair fits (the **Grace hash join**).
3. **Sort-merge join.** Sort both inputs on the join key (or read them in order from an index), then advance two cursors in step, emitting matches. It handles equality and also benefits range conditions; it is attractive when inputs are already sorted or when the output must be sorted anyway.

```python
from collections import defaultdict

customers = [(1, "Berlin"), (2, "Austin"), (3, "Pune")]           # (customer_id, city)
orders = [(10, 1, 2500), (11, 3, 900), (12, 1, 4100), (13, 4, 50)]  # (order_id, customer_id, total)

def nested_loop_join(outer, inner, okey, ikey):
    for o in outer:                      # for every outer row ...
        for i in inner:                  # ... scan the whole inner input
            if o[okey] == i[ikey]:
                yield o + i

def hash_join(build, probe, bkey, pkey):
    table = defaultdict(list)
    for b in build:                      # build phase: hash the smaller input
        table[b[bkey]].append(b)
    for p in probe:                      # probe phase: one lookup per probe row
        for b in table.get(p[pkey], ()):
            yield b + p

def sort_merge_join(left, right, lkey, rkey):
    left, right = sorted(left, key=lambda r: r[lkey]), sorted(right, key=lambda r: r[rkey])
    i = j = 0
    while i < len(left) and j < len(right):
        lv, rv = left[i][lkey], right[j][rkey]
        if lv < rv:
            i += 1
        elif lv > rv:
            j += 1
        else:                            # emit every pair in the matching groups
            j_end = j
            while j_end < len(right) and right[j_end][rkey] == lv:
                j_end += 1
            while i < len(left) and left[i][lkey] == lv:
                for r in right[j:j_end]:
                    yield left[i] + r
                i += 1
            j = j_end

for name, rows in [("nested loop", nested_loop_join(customers, orders, 0, 1)),
                   ("hash", hash_join(customers, orders, 0, 1)),
                   ("sort-merge", sort_merge_join(customers, orders, 0, 1))]:
    print(f"{name:<12}", sorted(rows, key=lambda r: r[2]))
```

What to notice:

- All three print the same three rows: Berlin with orders 10 and 12, Pune with order 11. Order 13 (customer 4) has no match and disappears, as an inner join requires.
- The nested loop performs $3 \times 4 = 12$ comparisons; the hash join performs 3 inserts and 4 probes. With a million rows on each side, that difference is $10^{12}$ versus $2 \times 10^6$ operations.

**Figure 11.2 — Hash join: build on the smaller input, probe with the larger.**

```mermaid
flowchart LR
  subgraph Build["Phase 1: build"]
    C[(customers<br/>100k rows)] -->|"scan, hash customer_id"| H["In-memory hash table<br/>~5.7 MB"]
  end
  subgraph Probe["Phase 2: probe"]
    O[(orders<br/>79k matching rows)] -->|"scan, hash customer_id"| P["Probe each row"]
  end
  H -->|"lookup"| P
  P -->|"joined rows"| OUT["Parent operator<br/>HashAggregate"]
  H -.->|"if memory exceeded: spill partitions"| D[("Temp files")]
```

**Reading the diagram.** Cylinders are tables or temporary files; rectangles are in-memory operator state; every solid arrow is a synchronous in-process data flow. The build phase must finish before probing starts (blocking), while the probe phase passes each `orders` row upward immediately (pipelined). The dotted arrow is the degradation path: if the hash table exceeds the memory budget (`work_mem` in PostgreSQL), both inputs are partitioned to disk and re-read. Sizes come from the real plan in §11.10. Scaling: more memory, an earlier filter on the build side, or parallel probe workers.

#### Mathematical foundations

The classic way to compare join algorithms counts **page I/Os**, because on a disk-resident database they dominate [Ramakrishnan and Gehrke 2003]. Let the outer relation $R$ have $M$ pages and the inner relation $S$ have $N$ pages.

::: formula
**I/O cost of join algorithms**

$$C_{\text{tuple NLJ}} = M + p_R \cdot M \cdot N \qquad C_{\text{block NLJ}} = M + \left\lceil \frac{M}{B-2} \right\rceil N$$

$$C_{\text{index NLJ}} = M + p_R \cdot M \cdot c_{\text{idx}} \qquad C_{\text{Grace hash}} \approx 3(M + N) \qquad C_{\text{sort-merge}} \approx 3(M+N) \text{ to } 5(M+N)$$

| Symbol | Meaning | Units |
|---|---|---|
| $M$, $N$ | Pages in the outer relation $R$ and inner relation $S$ | pages |
| $p_R$ | Rows per page of $R$ | rows/page |
| $B$ | Buffer pages available to the join (one for output, one for the inner scan) | pages |
| $c_{\text{idx}}$ | Page reads to find matching inner rows through an index (descent plus row fetch) | pages/row |
| $C$ | Total page reads and writes | page I/Os |
:::

The hash and sort-merge figures assume enough memory to finish in two passes (roughly $B > \sqrt{\min(M,N)}$ for hash, $B > \sqrt{\max(M,N)}$ for sort); with fewer buffers, more passes are needed. If the build side fits entirely in memory, a hash join reads each input once: $M + N$.

::: example
**Worked example — Joining `orders` with `order_items`.** The PostgreSQL tables of §11.10 have $M = 15{,}385$ pages for `orders` (1,000,000 rows, so $p_R = 65$) and $N = 18{,}383$ pages for `order_items` (2,500,000 rows), with 8 KiB pages. Assume $B = 1{,}002$ buffer pages (about 8 MiB).

1. Tuple NLJ: $15{,}385 + 65 \times 15{,}385 \times 18{,}383 = 15{,}385 + 1.84 \times 10^{10} \approx 1.8 \times 10^{10}$ I/Os. At 100 µs per random read that is $1.8 \times 10^6$ s, about 21 days.
2. Block NLJ: $\lceil 15{,}385 / 1{,}000 \rceil = 16$ chunks; $15{,}385 + 16 \times 18{,}383 = 309{,}513$ I/Os, about 31 s at 100 µs each (much less with sequential reads).
3. Grace hash join: $3 \times (15{,}385 + 18{,}383) = 101{,}304$ I/Os, about 10 s; if `orders` fits in memory, $33{,}768$ I/Os.
4. Index NLJ for **one customer's** 10 orders: the outer side is 10 rows; each needs about 4 page reads in the `order_items` primary-key index plus heap: roughly $10 \times 4 = 40$ I/Os, about 4 ms cold and well under 1 ms when cached (the real plan in §11.10 took 0.43 ms).

**Interpretation.** For a whole-table join, the naive nested loop is impossible, block NLJ is tolerable and the hash join wins. For a selective OLTP query, the index nested loop wins by four orders of magnitude, because it touches only the rows it needs. **Engineering implication.** There is no universally best join algorithm; the optimizer must know *how many rows* each side produces, which is why cardinality estimation (§11.10) decides performance.
:::

**Table 11.4 — Join algorithms compared.**

| Algorithm | Join conditions | Memory | Best when | Weakness |
|---|---|---|---|---|
| Nested loop (block) | Any | Small | Tiny inputs; non-equality conditions | Quadratic on large inputs |
| Index nested loop | Equality or range on indexed inner column | Small | Small outer side, indexed inner (OLTP) | Random I/O per outer row if outer is large |
| Hash join | Equality only | Build side (spills if needed) | Large unsorted inputs, analytics | Blocking build; spills when memory is short |
| Sort-merge join | Equality (and some ranges) | Sort buffers | Inputs already sorted or output needs sorting | Sorting cost if inputs are unsorted |

As of 2026, PostgreSQL implements all three. MySQL implements nested-loop variants (including batched key access) and, since 8.0.18, hash joins; it has no sort-merge join [MySQL Docs: Hash Join].

## 11.7 Indexes

### 11.7.1 What an index is

::: definition
**Definition — Index.** A secondary data structure, kept in sync with a table by the database, that maps values of one or more **key columns** to the locations of the rows holding them, so that rows can be found without scanning the whole table. Most relational indexes are B+ trees (§11.8); others include hash, GiST, GIN and BRIN indexes in PostgreSQL and full-text and spatial indexes in MySQL.
:::

#### First-principles explanation

A book's index finds "isolation levels" without reading 900 pages because it is sorted, small and points to page numbers. It must be updated when the book changes, takes paper, and is useless for a word on every page ("the"). Database indexes behave the same way: fast for selective conditions, extra work on every write, extra storage, no help when a query needs much of the table.

#### Why does this exist?

Without an index, `SELECT * FROM orders WHERE customer_id = 4242` read all 15,385 pages of the table and took 70 ms to find 10 rows (§11.10). With an index it read 16 pages and took 0.14 ms.

### 11.7.2 Clustered and secondary indexes

::: definition
**Definition — Clustered and secondary index.** In a **clustered index** (an index-organized table), the leaf level of the index *is* the table: rows are stored in key order inside the index's leaf pages. A table can have at most one. A **secondary index** stores, for each key, a pointer to the row; the table can have many.
:::

The two most popular open-source databases make opposite choices:

- **InnoDB (MySQL)** stores every table as a B+ tree clustered on the primary key. If you declare none, it uses the first `UNIQUE NOT NULL` index, or else generates a hidden 6-byte row ID. Secondary index leaves store the indexed columns plus the *primary-key value*. A secondary lookup therefore descends two trees: the secondary index to find the primary key, then the clustered index to find the row [MySQL Docs: Clustered and Secondary Indexes].
- **PostgreSQL** stores rows in an unordered **heap** file. Every index, including the primary key, is secondary; its leaves store a **TID** (tuple identifier: page number and slot), so a lookup descends one tree and then reads one heap page. The `CLUSTER` command reorders the heap once, but later inserts are not kept in order.

**Figure 11.3 — Secondary-index lookup paths in InnoDB and PostgreSQL.**

```mermaid
flowchart LR
  Q([Query: WHERE email = x])
  subgraph InnoDB["MySQL InnoDB"]
    S1["Secondary B+ tree<br/>email to customer_id"] -->|"PK value 4242"| CL[("Clustered B+ tree<br/>customer_id to full row")]
  end
  subgraph PG["PostgreSQL"]
    S2["B+ tree index<br/>email to TID"] -->|"TID page 17, slot 3"| HP[("Heap pages<br/>rows in insert order")]
  end
  Q -->|"descend"| S1
  Q -->|"descend"| S2
```

**Reading the diagram.** The same query descends two storage designs; all arrows are synchronous reads inside one database process. InnoDB's secondary index yields a primary-key *value*, which drives a second descent of the clustered index; PostgreSQL's index yields a physical TID, followed by one heap-page read. The logical pointer survives row moves, so clustered-index splits never touch secondary indexes; the physical pointer is cheaper to follow but must be updated in every index when an update moves a row (§11.14). Failure point: a long InnoDB primary key is copied into every secondary index. Scaling: keep InnoDB keys short and monotonic; leave free space in PostgreSQL heap pages (`fillfactor`).

### 11.7.3 Composite indexes and the leftmost-prefix rule

A **composite index** on `(customer_id, created_at)` sorts entries by `customer_id`, and within equal `customer_id` by `created_at`, like a phone book sorted by surname and then first name. You can use it to find everyone named "Rao" (leftmost column), or "Rao, Priya" (both columns), but not everyone named "Priya": those entries are scattered across the whole book. This is the **leftmost-prefix rule**: a B+ tree index can seek on a prefix of its columns, with equality on all but possibly the last column used, which may be a range.

The index on `(customer_id, created_at)` serves:

- `WHERE customer_id = ?`
- `WHERE customer_id = ? AND created_at >= ?`
- `WHERE customer_id = ? ORDER BY created_at DESC LIMIT 20` (no sort needed: entries are already in order)

and does *not* efficiently serve `WHERE created_at >= ?`. Some engines can **skip-scan** (seek once per distinct leading value), which helps only when the leading column has few distinct values: MySQL since 8.0.13, and PostgreSQL from version 18 (as of 2026).

::: recommendation
**Recommendation — Column order in composite indexes.** Put columns compared with equality first, then the column used for a range or `ORDER BY`. Selectivity of the leading column matters less than whether queries can use the prefix at all. One well-ordered composite index often replaces two or three single-column indexes.
:::

### 11.7.4 Covering, partial and expression indexes

- A **covering index** contains every column a query needs, so it can be answered from the index alone (an **index-only scan**). PostgreSQL 11+ adds payload columns with `INCLUDE`; InnoDB secondary indexes always cover the primary key. PostgreSQL still visits heap pages not marked all-visible in the **visibility map**, which VACUUM maintains (§11.14).
- A **partial index** indexes only rows matching a predicate: `CREATE INDEX ... ON orders (created_at) WHERE status = 'pending'`. If 1% of orders are pending, the index is 1% of the size. PostgreSQL and SQLite support partial indexes; MySQL does not (as of 8.4).
- An **expression index** indexes a computed value such as `lower(email)` (MySQL 8.0.13+: functional key parts).

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,          -- rowid alias: the table's clustered key
  customer_id INTEGER NOT NULL,
  status      TEXT    NOT NULL,
  total_cents INTEGER NOT NULL,
  created_at  TEXT    NOT NULL
);
CREATE INDEX orders_cust_created ON orders (customer_id, created_at);
CREATE INDEX orders_pending ON orders (created_at) WHERE status = 'pending';
""")
db.executemany(
    "INSERT INTO orders (customer_id, status, total_cents, created_at) VALUES (?,?,?,?)",
    [(i % 1000, "pending" if i % 100 == 0 else "shipped", i, f"2026-10-{1 + i % 28:02d}")
     for i in range(50_000)])

queries = {
    "both columns":        "SELECT * FROM orders WHERE customer_id = 7 AND created_at >= '2026-10-15'",
    "leftmost column only": "SELECT * FROM orders WHERE customer_id = 7",
    "second column only":  "SELECT * FROM orders WHERE created_at >= '2026-10-15'",
    "covering":            "SELECT created_at FROM orders WHERE customer_id = 7",
    "partial index":       "SELECT order_id FROM orders WHERE status = 'pending' AND created_at < '2026-10-03'",
}
for label, sql in queries.items():
    plan = db.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    print(f"{label:<21} -> {plan[0][3]}")
```

Output (SQLite 3.45):

```text
both columns          -> SEARCH orders USING INDEX orders_cust_created (customer_id=? AND created_at>?)
leftmost column only  -> SEARCH orders USING INDEX orders_cust_created (customer_id=?)
second column only    -> SCAN orders
covering              -> SEARCH orders USING COVERING INDEX orders_cust_created (customer_id=?)
partial index         -> SEARCH orders USING COVERING INDEX orders_pending (created_at<?)
```

What to notice:

- `SEARCH` means an index seek; `SCAN` means reading the whole table. Filtering on the second column alone falls back to a scan: the leftmost-prefix rule in action.
- The covering query asks only for `created_at`, which is in the index, so the table is never read.
- The partial-index query is covering too, because SQLite stores the rowid (`order_id`) in every index entry, just as InnoDB stores the primary key.

### 11.7.5 When an index does not help

#### Mathematical foundations

An index lookup through a secondary index costs roughly one *random* page read per matching row (when the rows are scattered across the table), while a full scan costs one *sequential* page read per table page. Above some fraction of matching rows, the scan wins.

::: formula
**Break-even selectivity for a secondary-index scan**

$$s^{*} = \frac{P \cdot c_{\text{seq}}}{n \cdot c_{\text{rand}}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $s^{*}$ | Fraction of rows matched above which a full scan is cheaper | dimensionless |
| $P$ | Pages in the table | pages |
| $n$ | Rows in the table | rows |
| $c_{\text{seq}}$ | Cost of a sequential page read | cost units/page |
| $c_{\text{rand}}$ | Cost of a random page read | cost units/page |
:::

::: example
**Worked example — When does PostgreSQL stop using the index on `orders`?** $P = 15{,}385$ pages, $n = 1{,}000{,}000$ rows, and PostgreSQL's default cost parameters are `seq_page_cost` = 1 and `random_page_cost` = 4.

1. Full scan cost: $15{,}385 \times 1 = 15{,}385$ units.
2. Index cost for fraction $s$: $s \times 10^6 \times 4$ units (ignoring the small index-page cost).
3. Break-even: $s^{*} = 15{,}385 / (4 \times 10^6) = 0.0038$, about 0.4% of rows, or 3,800 rows.

**Interpretation.** A query matching 10 rows uses the index; one matching 50% of rows (`customer_id > 50000` in §11.10) is planned as a sequential scan, which is exactly what PostgreSQL chose. **Engineering implication.** Indexes serve *selective* predicates. PostgreSQL softens the cliff with **bitmap scans**, which collect matching TIDs, sort them by page and read each heap page once; and correlation statistics lower the estimated cost when the table is physically ordered by the indexed column. On SSDs, many teams lower `random_page_cost` to about 1.1–2 because random and sequential reads cost nearly the same.
:::

**Table 11.5 — Index variants.**

| Variant | What it stores | Speeds up | Costs | Engine support |
|---|---|---|---|---|
| Clustered (primary) | Full rows in key order | PK lookups and PK range scans | Wide secondary indexes (InnoDB) | InnoDB, SQL Server, SQLite rowid tables |
| Secondary | Key + row pointer (TID or PK) | Selective lookups on other columns | One extra structure to update per write | All |
| Composite | Several columns, lexicographic order | Prefix equality + range/sort | Useless without the leading column | All |
| Covering / `INCLUDE` | Extra payload columns | Index-only scans | Larger index | PostgreSQL 11+, SQL Server; InnoDB via PK |
| Partial | Only rows matching a predicate | Queries on a small, hot subset | Query must imply the predicate | PostgreSQL, SQLite (not MySQL) |
| Expression / functional | Computed values | Queries on the same expression | Expression evaluated on write | PostgreSQL, MySQL 8.0.13+, SQLite |

::: mistake
**Mistake — "Add an index on every column to be safe."** A table with eight indexes turns one row insert into nine B+ tree insertions, inflates storage and the buffer pool's working set, and in PostgreSQL prevents heap-only-tuple updates of indexed columns (§11.14). Index the queries you run; drop indexes whose `pg_stat_user_indexes.idx_scan` stays at zero.
:::

::: mistake
**Mistake — Wrapping the indexed column in a function.** `WHERE date(created_at) = '2026-10-30'` cannot use an index on `created_at`, because the index is sorted by `created_at`, not by `date(created_at)`. Rewrite as a range: `WHERE created_at >= '2026-10-30' AND created_at < '2026-10-31'`. The same applies to implicit type casts, such as comparing a text column with a number in MySQL.
:::

## 11.8 B-trees and B+ trees

### 11.8.1 Structure and operations

::: definition
**Definition — B-tree and B+ tree.** A **B-tree** is a balanced search tree whose nodes are disk pages holding many sorted keys; every leaf is at the same depth, and nodes split and merge to stay between half-full and full [Bayer and McCreight 1972]. A **B+ tree** is the variant used by almost every relational database: internal nodes hold only separator keys and child pointers, all keys and values (or row pointers) live in the leaves, and leaves are linked to their siblings so range scans can walk sideways [Comer 1979; Petrov 2019].
:::

#### Why does this exist?

A binary search tree needs about 30 levels for a billion keys (§4.4.2): 30 dependent disk reads. The B-tree makes each node one page holding hundreds of keys, so the tree is wide and shallow. Keeping values only in leaves (the B+ variant) makes internal nodes denser, so more of the tree fits in memory, and sibling links turn range predicates into a sequential walk.

#### How it works internally

1. **Search.** Start at the root page. Binary-search its separator keys in memory to choose a child pointer. Repeat until a leaf; binary-search the leaf.
2. **Range scan.** Search for the lower bound, then follow leaf sibling links until the upper bound.
3. **Insert.** Search for the target leaf and insert the key in order. If the leaf overflows, **split** it into two half-full leaves and insert a separator key into the parent; if the parent overflows, split it too. A split of the root creates a new root, which is the only way the tree grows taller, so all leaves stay at the same depth.
4. **Delete.** Remove the key; if a node becomes too empty, borrow from or merge with a sibling (many engines merge lazily or not at all, leaving reclaimable space).
5. **Concurrency and crash safety.** Splits modify several pages, so engines latch pages briefly and log every change in the write-ahead log; PostgreSQL uses Lehman and Yao's right-links so readers never block on a concurrent split [Lehman and Yao 1981]. Details are in §13.5–§13.6.

**Figure 11.4 — A B+ tree on `order_id` with three levels.**

```mermaid
flowchart TD
  R["Root page<br/>separators 400 · 800"] --> I1["Internal page<br/>100 · 250"]
  R --> I2["Internal page<br/>520 · 650"]
  R --> I3["Internal page<br/>900 · 1100"]
  I1 --> L1["Leaf: 1 … 99"]
  I1 --> L2["Leaf: 100 … 249"]
  I1 --> L3["Leaf: 250 … 399"]
  I2 --> L4["Leaf: 400 … 519"]
  L1 -->|"next leaf"| L2
  L2 -->|"next leaf"| L3
  L3 -->|"next leaf"| L4
  L2 --> H[("Heap rows or<br/>clustered row data")]
```

**Reading the diagram.** Each rectangle is one fixed-size page (8 KiB in PostgreSQL, 16 KiB in InnoDB). A search follows child pointers synchronously, one page per level: for `order_id` 180 the root goes left (180 < 400) and the internal page picks the second leaf. The "next leaf" arrows are sibling links that range scans walk. The cylinder is the storage boundary below the leaves: a heap row (PostgreSQL) or the row itself (InnoDB clustered index). Failure points: a split changes several pages atomically, hence WAL logging (§13.5), and a cold cache makes every level an I/O. Scaling: multiplying the data by the fan-out adds one level.

### 11.8.2 Fan-out, height and I/Os per lookup

§4.4.3 derived $h = \lceil \log_f n \rceil$ for a tree whose leaves hold one key each. In a real B+ tree each leaf holds $L$ entries, so only the internal levels need the logarithm.

::: formula
**Height of a B+ tree with $L$ entries per leaf**

$$h = 1 + \left\lceil \log_f \left\lceil \frac{n}{L} \right\rceil \right\rceil, \qquad f = \left\lfloor \frac{u \cdot P}{e_{\text{int}}} \right\rfloor, \qquad L = \left\lfloor \frac{u \cdot P}{e_{\text{leaf}}} \right\rfloor$$

| Symbol | Meaning | Units |
|---|---|---|
| $h$ | Levels from root to leaf (page reads per lookup with a cold cache) | levels |
| $n$ | Entries (rows) indexed | rows |
| $P$ | Page size | bytes |
| $u$ | Average fraction of each page holding entries (fill factor minus headers) | dimensionless |
| $e_{\text{int}}$ | Bytes per internal entry (separator key + child pointer + overhead) | bytes |
| $e_{\text{leaf}}$ | Bytes per leaf entry (full row for a clustered index; key + pointer for a secondary index) | bytes |
| $f$ | Fan-out of internal pages | children/page |
| $L$ | Entries per leaf page | entries/page |
:::

::: example
**Worked example — A billion-row `orders` table in InnoDB with 16 KiB pages.** Assume $u = 0.8$, a `bigint` primary key with 16-byte internal entries (as in §4.4.3), and 200-byte rows.

1. Usable bytes per page: $0.8 \times 16{,}384 = 13{,}107$ bytes.
2. Fan-out: $f = \lfloor 13{,}107 / 16 \rfloor = 819$. Rows per leaf: $L = \lfloor 13{,}107 / 200 \rfloor = 65$.
3. Leaf pages: $\lceil 10^9 / 65 \rceil = 15{,}384{,}616$ (about 235 GiB of row data).
4. Internal levels: $\lceil 15{,}384{,}616 / 819 \rceil = 18{,}785$ pages, then $\lceil 18{,}785 / 819 \rceil = 23$, then 1 root. Check with the formula: $\log_{819}(15{,}384{,}616) = 16.55 / 6.71 = 2.47$, rounded up to 3, plus the leaf level: $h = 4$.
5. Memory for all internal pages: $(1 + 23 + 18{,}785) \times 16$ KiB $= 18{,}809 \times 16$ KiB $\approx 294$ MiB.
6. A secondary index on `customer_id` (8-byte key + 8-byte primary key per leaf entry, $L = 819$) has $\lceil 10^9/819 \rceil = 1{,}221{,}002$ leaves (about 18.6 GiB), then 1,491, 2 and 1 pages: also 4 levels, with only 23 MiB of internal pages.

I/Os per lookup:

- Cold cache: 4 page reads for a primary-key lookup.
- Internal pages cached (294 MiB is trivial for a database server): **1 random read** per primary-key lookup, about 0.1 ms on NVMe (§4.17).
- Secondary-index lookup in InnoDB: 1 read for the secondary leaf + 1 for the clustered leaf = **2 reads**. In PostgreSQL: index leaf + heap page = 2 reads, similarly.

**Interpretation.** A billion rows cost only one more level than a million rows (a million rows needs $1 + \lceil \log_{819} 15{,}385 \rceil = 3$ levels). **Engineering implication.** Index lookups stay fast at any table size you will meet in one database; what grows is the *leaf* working set. If the hot rows' leaves (here up to 235 GiB) do not fit in the buffer pool, every lookup pays a real I/O, and that, not tree height, is the scaling limit. Wide keys shrink $f$ and $L$; random keys spread the hot set across all leaves.
:::

```python
import math

def bplus_tree(n_rows, page_bytes=16 * 1024, fill=0.8, internal_entry=16, leaf_entry=200):
    """Return (fan-out, entries per leaf, pages per level from root to leaves)."""
    usable = page_bytes * fill
    fanout = int(usable // internal_entry)          # child pointers per internal page
    per_leaf = int(usable // leaf_entry)            # entries per leaf page
    levels = [math.ceil(n_rows / per_leaf)]         # leaf level first
    while levels[-1] > 1:
        levels.append(math.ceil(levels[-1] / fanout))
    return fanout, per_leaf, levels[::-1]

for label, leaf_entry in [("clustered, 200-byte rows", 200), ("secondary, 8-byte key + 8-byte PK", 16)]:
    f, L, pages = bplus_tree(10**9, leaf_entry=leaf_entry)
    internal_mib = sum(pages[:-1]) * 16 / 1024
    leaf_gib = pages[-1] * 16 / 1024**2
    print(f"{label}: fan-out={f}, entries/leaf={L}, height={len(pages)}")
    print(f"  pages per level (root..leaf) = {pages}")
    print(f"  internal levels = {internal_mib:,.0f} MiB, leaf level = {leaf_gib:,.1f} GiB")
```

What to notice:

- Output: the clustered tree has pages per level `[1, 23, 18785, 15384616]` and the secondary tree `[1, 2, 1491, 1221002]`; both have height 4, matching the hand calculation.
- Change `leaf_entry` to 1,000 (wide rows) and the leaf level grows fivefold while the height stays 4: width costs memory before it costs levels.

::: mistake
**Mistake — "B-tree and B+ tree are the same thing."** In a classic B-tree, values can live in internal nodes, so a range scan must move up and down the tree. Database "B-tree" indexes are B+ trees (PostgreSQL's `btree`, InnoDB's indexes): values only in leaves, leaves linked. In interviews, say "B+ tree" and explain the leaf links.
:::

## 11.9 Query execution and plans

### 11.9.1 From SQL text to rows

Every statement passes through the same pipeline:

1. **Parse** — check syntax and build a parse tree.
2. **Analyze and rewrite** — resolve table and column names against the catalog, check permissions, expand views, and apply rewrite rules (for example, flattening a subquery into a join).
3. **Plan (optimize)** — enumerate alternative physical plans, estimate the cost of each using table statistics, and choose the cheapest (§11.10).
4. **Execute** — run the plan's operators against the storage engine, which reads pages through the buffer pool (§13.4).

### 11.9.2 The Volcano (iterator) model

::: definition
**Definition — Volcano (iterator) model.** An execution model in which a query plan is a tree of operators, each implementing the same interface — `open()`, `next()` and `close()` — and each `next()` call pulls one row from the operator's children on demand [Graefe 1994].
:::

#### First-principles explanation

In a kitchen line, the waiter asks plating for the next dish, plating asks the grill, the grill asks the fridge; nobody cooks a thousand steaks in advance. This **pull model** lets operators compose freely, keeps memory small for streaming operators, and lets a `LIMIT 20` stop the scans below after 20 rows.

Sort, hash aggregation and the build side of a hash join cannot emit a row until they have consumed all input. These **blocking** operators need memory proportional to their input and spill to disk when it runs out; in `EXPLAIN`, their startup cost is close to their total cost.

```python
class Operator:
    """Volcano iterator: every operator exposes open(), next() and close()."""
    def open(self): pass
    def next(self): raise NotImplementedError   # returns one row, or None when exhausted
    def close(self): pass

class SeqScan(Operator):
    def __init__(self, rows): self.rows = rows
    def open(self): self.pos = 0
    def next(self):
        if self.pos == len(self.rows): return None
        self.pos += 1
        return self.rows[self.pos - 1]

class Filter(Operator):
    def __init__(self, child, pred): self.child, self.pred = child, pred
    def open(self): self.child.open()
    def next(self):
        while (row := self.child.next()) is not None:
            if self.pred(row): return row
        return None
    def close(self): self.child.close()

class HashJoin(Operator):
    def __init__(self, build, probe, bkey, pkey):
        self.build, self.probe, self.bkey, self.pkey = build, probe, bkey, pkey
    def open(self):                       # blocking: consumes the whole build side
        self.table, self.pending = {}, []
        self.build.open()
        while (b := self.build.next()) is not None:
            self.table.setdefault(b[self.bkey], []).append(b)
        self.build.close()
        self.probe.open()
    def next(self):                       # pipelined: one probe row at a time
        while not self.pending:
            p = self.probe.next()
            if p is None: return None
            self.pending = [b + p for b in self.table.get(p[self.pkey], [])]
        return self.pending.pop()
    def close(self): self.probe.close()

class Project(Operator):
    def __init__(self, child, cols): self.child, self.cols = child, cols
    def open(self): self.child.open()
    def next(self):
        row = self.child.next()
        return None if row is None else tuple(row[c] for c in self.cols)
    def close(self): self.child.close()

class Limit(Operator):
    def __init__(self, child, n): self.child, self.n = child, n
    def open(self): self.child.open(); self.seen = 0
    def next(self):
        if self.seen == self.n: return None   # stop pulling: the scan below never finishes
        self.seen += 1
        return self.child.next()
    def close(self): self.child.close()

# SELECT c.city, o.total FROM customers c JOIN orders o ON c.id = o.customer_id
# WHERE o.total > 1000 LIMIT 2
customers = [(1, "Berlin"), (2, "Austin"), (3, "Pune")]
orders = [(10, 1, 2500), (11, 3, 900), (12, 1, 4100), (13, 2, 1800)]
plan = Limit(Project(HashJoin(SeqScan(customers),
                              Filter(SeqScan(orders), lambda r: r[2] > 1000), 0, 1),
                     cols=[1, 4]), 2)
plan.open()
while (row := plan.next()) is not None:
    print(row)
plan.close()
```

What to notice:

- The output is `('Berlin', 2500)` and `('Berlin', 4100)`. Order 13 (Austin, 1800) also qualifies but is never produced: `Limit` stopped pulling after two rows, so the orders scan stopped early.
- `HashJoin.open()` drains its build child completely (blocking); `next()` handles one probe row at a time (pipelined).
- Every row costs several virtual function calls. Modern analytic engines reduce that overhead with **vectorized** execution (each `next()` returns a batch of about a thousand values) [Boncz et al. 2005] or by **compiling** the plan into machine code [Neumann 2011]. PostgreSQL remains a Volcano-style executor, with optional JIT compilation of expressions.

**Figure 11.5 — The executed plan tree for "revenue by city over the last day".**

```mermaid
flowchart BT
  SO["Seq Scan on orders<br/>filter: last day, not cancelled<br/>78,515 rows"] -->|"rows"| HJ["Hash Join<br/>o.customer_id = c.customer_id"]
  SC["Seq Scan on customers<br/>100,000 rows"] -->|"rows"| H["Hash<br/>build, 5.7 MB"]
  H -->|"hash table"| HJ
  HJ -->|"78,515 joined rows"| AG["HashAggregate<br/>group by city: 5 groups"]
  AG -->|"5 rows"| S["Sort<br/>by revenue desc"]
  S -->|"5 rows"| R([Client])
```

**Reading the diagram.** This is the real plan PostgreSQL 16 chose for the revenue query of §11.10, drawn bottom-up: rows flow upward while `next()` calls flow down, all synchronously inside one backend process. The scans are the storage boundary; `Hash`, `HashAggregate` and `Sort` are blocking and spill to temporary files if they exceed `work_mem`. The main failure point is a misestimated row count, which can make this plan win when an index-driven plan would be better. Scaling: an index on `orders(created_at)` would replace the million-row scan, and parallel workers could split it.

## 11.10 Query optimization

### 11.10.1 The cost-based optimizer

::: definition
**Definition — Cost-based optimizer.** The component that enumerates equivalent physical plans for a query (access paths, join orders, join algorithms), estimates each plan's cost from **statistics** about the data using a **cost model**, and returns the plan with the lowest estimated cost.
:::

The design dates from IBM's System R. Selinger and colleagues introduced the three ideas every optimizer still uses: estimate the **selectivity** of each predicate from catalog statistics; cost plans in a weighted mix of page I/O and CPU; and find the best join order by **dynamic programming**, building the best plan for every subset of tables from the best plans of smaller subsets, while remembering plans that produce **interesting orders** (sorted output that a later merge join or `ORDER BY` can reuse) [Selinger et al. 1979].

#### Mathematical foundations

::: formula
**Size of the join-order search space**

$$N_{\text{left-deep}} = n! \qquad N_{\text{bushy}} = \frac{(2(n-1))!}{(n-1)!} \qquad W_{\text{DP}} \approx n \cdot 2^{\,n-1}$$

| Symbol | Meaning | Units |
|---|---|---|
| $n$ | Number of tables joined | tables |
| $N_{\text{left-deep}}$ | Join orders where every join's inner input is a base table | plans |
| $N_{\text{bushy}}$ | All binary join trees, including joins of two intermediate results | plans |
| $W_{\text{DP}}$ | Approximate subproblems examined by Selinger-style dynamic programming over left-deep plans | subproblems |
:::

::: example
**Worked example — Ten tables.** For $n = 10$: left-deep orders $10! = 3{,}628{,}800$; bushy trees $18!/9! \approx 1.76 \times 10^{10}$; dynamic programming examines about $10 \times 2^9 = 5{,}120$ subset extensions. **Interpretation.** Dynamic programming makes ten-way joins tractable, but $2^n$ still explodes: at $n = 20$ it is about 10 million. **Engineering implication.** PostgreSQL switches to a genetic (randomized) search at 12 `FROM` items by default (`geqo_threshold`), and stops reordering explicit joins beyond 8 (`join_collapse_limit`); very wide joins generated by ORMs or reporting tools can therefore get poor plans.
:::

### 11.10.2 Cost model and statistics in PostgreSQL

PostgreSQL's costs are in arbitrary units anchored on one sequential page read. The defaults (verified on PostgreSQL 16) are `seq_page_cost` = 1, `random_page_cost` = 4, `cpu_tuple_cost` = 0.01, `cpu_index_tuple_cost` = 0.005 and `cpu_operator_cost` = 0.0025 [PostgreSQL Docs: Using EXPLAIN].

::: formula
**Cost of a sequential scan with one filter (PostgreSQL)**

$$C_{\text{seq}} = P \cdot c_{\text{seq}} + n \cdot c_{\text{tuple}} + n \cdot k \cdot c_{\text{op}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $P$ | Heap pages (`pg_class.relpages`) | pages |
| $n$ | Rows (`pg_class.reltuples`) | rows |
| $k$ | Operators evaluated per row in the filter | operators |
| $c_{\text{seq}}$, $c_{\text{tuple}}$, $c_{\text{op}}$ | `seq_page_cost`, `cpu_tuple_cost`, `cpu_operator_cost` | cost units |
:::

To estimate how many rows survive a filter, the planner uses per-column statistics collected by `ANALYZE` from a random sample (visible in `pg_stats`): the number of distinct values, the **most common values** with their frequencies, a histogram of the rest, the null fraction and the physical **correlation** between column order and heap order.

::: formula
**Cardinality estimate under the independence assumption**

$$\hat{r} = n \cdot \prod_{i=1}^{k} s_i, \qquad s_i \approx \text{freq}(v_i) \text{ or } \frac{1}{d_i}$$

| Symbol | Meaning | Units |
|---|---|---|
| $\hat{r}$ | Estimated rows satisfying all $k$ predicates | rows |
| $n$ | Rows in the table | rows |
| $s_i$ | Selectivity of predicate $i$ (fraction of rows passing it) | dimensionless |
| $\text{freq}(v_i)$ | Sampled frequency of value $v_i$ if it is a most-common value | dimensionless |
| $d_i$ | Number of distinct values in the column | values |
:::

::: example
**Worked example — Checking the planner's arithmetic on real plans.** On the 1,000,000-row `orders` table (15,385 pages):

1. `EXPLAIN SELECT * FROM orders WHERE customer_id = 4242` reported `cost=0.00..27885.00`. By the formula: $15{,}385 \times 1 + 10^6 \times 0.01 + 10^6 \times 1 \times 0.0025 = 15{,}385 + 10{,}000 + 2{,}500 = 27{,}885$. Exact match.
2. Its row estimate was 10: with 100,000 distinct customers, $s = 1/100{,}000$ and $\hat{r} = 10^6 / 10^5 = 10$. Actual: 10.
3. Now a table `addr` of 1,000,000 rows where `city` determines `country` (every Pune row is in India). Each column has 5 values at about 20% each. For `WHERE city = 'Pune' AND country = 'IN'` the independence assumption gives $\hat{r} = 10^6 \times 0.2 \times 0.2 = 40{,}000$. PostgreSQL estimated 39,960; the actual count was 200,000, an underestimate of 5×.

**Interpretation.** The formulas are simple and exact for single predicates on well-sampled columns; the error comes from *correlation*, which the independence assumption ignores. **Engineering implication.** Errors multiply through joins: an estimate that is 5× too low feeding a join whose own estimate is 5× too low is 25× off, which is enough to choose a nested loop over a million rows. For correlated columns, PostgreSQL 10+ supports extended statistics: after `CREATE STATISTICS addr_city_country (dependencies) ON city, country FROM addr; ANALYZE addr;` the estimate became 198,500.
:::

::: industry
**Research evidence — How good are query optimizers?** Leis and colleagues built the Join Order Benchmark on the real IMDB dataset (queries with many joins over correlated data) and measured PostgreSQL and several commercial systems. Cardinality estimates were routinely wrong by orders of magnitude, errors grew with the number of joins, and estimation errors mattered far more for plan quality than the cost model did [Leis et al. 2015].
*Evidence: Primary* — [Leis et al. 2015]
:::

### 11.10.3 Reading EXPLAIN and EXPLAIN ANALYZE

`EXPLAIN` shows the chosen plan with estimates; `EXPLAIN ANALYZE` actually runs the query and adds measured times and row counts; `BUFFERS` adds page counts. (MySQL 8.0.18+ has `EXPLAIN ANALYZE` with a different format.) The following is real PostgreSQL 16 output for the order-history query after creating an index on `orders (customer_id, created_at DESC)`, with parallel query disabled for readability:

```text
Limit  (cost=44.03..44.05 rows=10 width=32) (actual time=0.110..0.112 rows=10 loops=1)
  Buffers: shared hit=3 read=13
  ->  Sort  (cost=44.03..44.05 rows=10 width=32) (actual time=0.109..0.110 rows=10 loops=1)
        Sort Key: created_at DESC
        Sort Method: quicksort  Memory: 25kB
        ->  Bitmap Heap Scan on orders  (cost=4.50..43.86 rows=10 width=32) (actual time=0.042..0.099 rows=10 loops=1)
              Recheck Cond: (customer_id = 4242)
              Heap Blocks: exact=10
              ->  Bitmap Index Scan on orders_customer_created_idx  (cost=0.00..4.50 rows=10 width=0) (actual time=0.028..0.028 rows=10 loops=1)
                    Index Cond: (customer_id = 4242)
Planning Time: 0.219 ms
Execution Time: 0.135 ms
```

How to read it:

1. Read from the most indented node outward: the bitmap index scan finds 10 TIDs, the heap scan fetches 10 pages, the sort orders them, the limit returns them.
2. `cost=startup..total` and `rows` are estimates; `actual time=first..last` is in milliseconds *per loop* (multiply by `loops`).
3. **Compare estimated and actual `rows` at every node.** A gap above about 10× points to stale statistics (`ANALYZE`), correlated columns (`CREATE STATISTICS`) or an unestimatable predicate (functions, casts).
4. `Buffers: shared hit=3 read=13`: 3 pages from the buffer pool, 13 from the OS or disk.

With only 10 orders per customer, sorting 10 rows was estimated cheaper than walking the index in `created_at` order; for a customer with thousands of orders the plan switches to an index scan that needs no sort.

::: warning
**Warning — `EXPLAIN ANALYZE` executes the statement.** For `INSERT`, `UPDATE` or `DELETE`, wrap it: `BEGIN; EXPLAIN ANALYZE UPDATE ...; ROLLBACK;`. Also remember that the first run may read from disk and the second from cache; compare `Buffers` before comparing times.
:::

**Table 11.6 — Failure scenarios in query planning.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Query suddenly 100× slower after a data load | Stale statistics; plan flipped | `pg_stat_statements` latency jump; estimate vs actual gap | `ANALYZE` the table | Autovacuum/analyze tuning; analyze after bulk loads |
| Nested loop over millions of rows | Underestimated cardinality from correlated predicates | `rows=` estimate far below actual | Extended statistics; rewrite query | `CREATE STATISTICS` on correlated columns |
| Index ignored | Function or cast on column; low selectivity | `Seq Scan` with selective filter | Expression index or rewritten predicate | Code review of predicates |
| Hash join or sort spills to disk | Memory budget too small for build side | `Batches: >1`, `Sort Method: external merge` | Raise `work_mem` for that session | Filter earlier; size memory per query |

## 11.11 Transactions

### 11.11.1 Commit, rollback and savepoints

::: definition
**Definition — Transaction.** A sequence of reads and writes that the database treats as one logical unit: either all of its effects become permanent together (**commit**) or none of them do (**abort** or **rollback**), and concurrently running transactions are isolated from each other's intermediate states.
:::

#### First-principles explanation

Moving money between two accounts is two writes: debit one, credit the other. If the server crashes between them, or a constraint fails on the second, money is created or destroyed. Without transactions, every application would need its own crash-recovery and concurrency logic for every multi-step operation, and most would get it wrong. A transaction lets you write the steps as if nothing else were happening and nothing could fail, and makes the database responsible for the rest [Gray and Reuter 1993].

#### How it works internally

1. `BEGIN` starts a transaction (many drivers start one implicitly; with **autocommit**, every statement is its own transaction).
2. Each write is recorded in the write-ahead log and applied to pages in memory; concurrency control (MVCC and locks, §11.14–§11.15) decides what other transactions may see and do.
3. `COMMIT` forces the log records to durable storage, then makes the changes visible. `ROLLBACK`, an error or a crash before the commit record is durable undoes them.
4. `SAVEPOINT name` / `ROLLBACK TO name` undo part of a transaction without abandoning it.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE accounts (
  account_id    INTEGER PRIMARY KEY,
  balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0)   -- invariant: no overdraft
);
INSERT INTO accounts VALUES (1, 10000), (2, 0);
""")

def transfer(src, dst, cents):
    try:
        with db:                                   # BEGIN; ... COMMIT (or ROLLBACK on error)
            db.execute("UPDATE accounts SET balance_cents = balance_cents + ? "
                       "WHERE account_id = ?", (cents, dst))          # credit first, on purpose
            db.execute("UPDATE accounts SET balance_cents = balance_cents - ? "
                       "WHERE account_id = ?", (cents, src))          # may violate the CHECK
        return "committed"
    except sqlite3.IntegrityError as e:
        return f"rolled back ({e})"

print(transfer(1, 2, 7000), db.execute("SELECT * FROM accounts").fetchall())
print(transfer(1, 2, 7000), db.execute("SELECT * FROM accounts").fetchall())
```

What to notice:

- Output: `committed [(1, 3000), (2, 7000)]`, then `rolled back (CHECK constraint failed: balance_cents >= 0) [(1, 3000), (2, 7000)]`. The second transfer's credit had already been applied when the debit failed, yet it vanished: atomicity.
- The invariant lives in the schema (`CHECK`), so no code path can violate it, including ones written next year.

::: warning
**Warning — Keep transactions short, and never wait on the network inside one.** An open transaction holds row locks and pins old row versions (§11.14). Do slow external work, such as payment calls, before or after the transaction, and make it idempotent (§22.15).
:::

## 11.12 ACID

::: definition
**Definition — ACID.** The four guarantees of a database transaction, named by Härder and Reuter [Härder and Reuter 1983]:
**Atomicity** — all of a transaction's writes take effect, or none do.
**Consistency** — a transaction takes the database from one state satisfying all declared invariants (constraints) to another.
**Isolation** — concurrently executing transactions do not see each other's partial effects; at the strongest level, the outcome equals some serial execution.
**Durability** — once a commit is acknowledged, its effects survive crashes.
:::

How each is implemented:

- **Atomicity** — undo information (InnoDB undo records; in PostgreSQL, uncommitted versions are never marked visible).
- **Consistency** — constraints (`PRIMARY KEY`, `UNIQUE`, `FOREIGN KEY`, `CHECK`, `NOT NULL`). Invariants the schema cannot express ("at least one doctor on call") are the application's job, helped by isolation.
- **Isolation** — MVCC and locking (§11.13–§11.15).
- **Durability** — **write-ahead logging**: the commit record is flushed with `fsync` before "committed" is returned, with many commits sharing one flush (**group commit**). `synchronous_commit = off` (PostgreSQL) or `innodb_flush_log_at_trx_commit = 2` trade recent commits for throughput (§13.5). Surviving machine loss needs replication (Chapter 14).

### 11.12.1 The "C" in ACID is not the "C" in CAP

The word *consistency* is used for at least three unrelated ideas. Mixing them up is a classic interview mistake.

**Table 11.7 — Three meanings of "consistency".**

| Term | Question it answers | Scope | Where in this book |
|---|---|---|---|
| ACID consistency | Do committed states satisfy the declared invariants? | One database, constraints | §11.12 |
| Strong consistency (linearizability), the "C" in CAP | Does every read see the latest completed write, as if there were one copy? | Replicated data | §25.3, §25.8 |
| Eventual consistency | Will replicas converge if writes stop? | Replicated data | §25.7 |

A single PostgreSQL server is ACID-consistent and, for reads on that server, linearizable. Add an asynchronous read replica and a client can commit a write on the primary and then read the old value from the replica: the system is still ACID at the primary, but reads are no longer linearizable (§14.4). Kleppmann notes that the C in ACID is really a property of the application's use of transactions, not something the database provides by itself [Kleppmann 2017].

## 11.13 Isolation levels and anomalies

### 11.13.1 The anomalies

Perfect isolation, called **serializability**, means the result of running transactions concurrently equals the result of running them one at a time in *some* order. It costs throughput, so databases offer weaker **isolation levels** that permit specific **anomalies**. Berenson and colleagues showed that the SQL standard's definitions were ambiguous and catalogued the anomalies precisely [Berenson et al. 1995]:

::: definition
**Definition — Isolation anomalies.**
**Dirty write:** a transaction overwrites another's uncommitted write.
**Dirty read:** a transaction reads another's uncommitted write (which may later roll back).
**Non-repeatable (fuzzy) read:** a transaction reads a row twice and sees different committed values because another transaction updated it in between.
**Phantom:** a transaction runs the same *predicate* query twice (`WHERE status = 'pending'`) and gets a different set of rows because another transaction inserted or deleted matching rows.
**Lost update:** two transactions read the same value, both compute a new value from it and write; the second write silently overwrites the first.
**Read skew:** a transaction sees part of another transaction's effects (reads account A before a transfer commits and account B after it).
**Write skew:** two transactions read an overlapping set of rows, each checks an invariant, then each writes a *different* row; each write is valid alone but together they violate the invariant.
:::

**Figure 11.6 — Non-repeatable read under READ COMMITTED.**

```mermaid
sequenceDiagram
  participant A as Txn A - report
  participant DB as Database
  participant B as Txn B - restock
  A->>DB: SELECT on_hand WHERE product 42
  DB-->>A: 10
  B->>DB: UPDATE on_hand = on_hand - 3
  B->>DB: COMMIT
  A->>DB: SELECT on_hand WHERE product 42
  DB-->>A: 7 under READ COMMITTED
  Note over A,DB: REPEATABLE READ returns 10 again: same snapshot
```

**Reading the diagram.** Two clients on separate connections send synchronous SQL; time runs downward. Under READ COMMITTED each *statement* takes a new snapshot, so A's second read sees B's committed change; under PostgreSQL REPEATABLE READ the *transaction* keeps its first snapshot and sees 10 twice. Both outcomes were reproduced on PostgreSQL 16. Both row versions exist inside the database at once (§11.14); the failure is any logic in A that combines the two reads, such as a report whose totals do not add up.

**Figure 11.7 — Lost update from an application-side read-modify-write.**

```mermaid
sequenceDiagram
  participant A as Txn A - checkout 1
  participant DB as Database
  participant B as Txn B - checkout 2
  A->>DB: SELECT on_hand - returns 10
  B->>DB: SELECT on_hand - returns 10
  A->>DB: UPDATE SET on_hand = 9
  A->>DB: COMMIT
  B->>DB: UPDATE SET on_hand = 9
  Note over B,DB: READ COMMITTED: succeeds, one sale lost
  Note over B,DB: PostgreSQL REPEATABLE READ: error, retry
  B->>DB: COMMIT or ROLLBACK
```

**Reading the diagram.** Each checkout reads 10 and writes the literal 9 computed *in the application*. Under READ COMMITTED (and MySQL REPEATABLE READ) B silently overwrites A: two units sold, one decremented. Under PostgreSQL REPEATABLE READ, B's `UPDATE` fails with `could not serialize access due to concurrent update` and B must retry. The fix at any level is to let the database do the arithmetic, `UPDATE inventory SET on_hand = on_hand - 1 WHERE product_id = 42 AND on_hand >= 1`, or to lock first with `SELECT ... FOR UPDATE`, or to check a version (§11.15.3).

**Figure 11.8 — Write skew: both doctors go off call.**

```mermaid
sequenceDiagram
  participant A as Txn A - Alice
  participant DB as Database
  participant B as Txn B - Bob
  A->>DB: SELECT count WHERE on_call - returns 2
  B->>DB: SELECT count WHERE on_call - returns 2
  A->>DB: UPDATE alice SET on_call = false
  B->>DB: UPDATE bob SET on_call = false
  A->>DB: COMMIT - ok
  B->>DB: COMMIT
  Note over B,DB: REPEATABLE READ: ok, nobody on call
  Note over B,DB: SERIALIZABLE: aborted, retry sees 1
```

**Reading the diagram.** The invariant "at least one doctor on call" is checked by a read and protected by nothing: the transactions write *different* rows, so neither snapshot isolation nor row locks see a conflict, and both commit at REPEATABLE READ. PostgreSQL SERIALIZABLE tracks what each transaction *read*, detects the dangerous dependency pattern and aborts one with `could not serialize access due to read/write dependencies among transactions`; its retry sees one doctor on call. In the shop the same pattern double-redeems a limited coupon. Below SERIALIZABLE, materialize the conflict by locking a shared row with `FOR UPDATE`.

### 11.13.2 The standard levels and what databases actually do

**Table 11.8 — ANSI SQL isolation levels as defined by the three phenomena.**

| Level | Dirty read | Non-repeatable read | Phantom |
|---|---|---|---|
| READ UNCOMMITTED | Possible | Possible | Possible |
| READ COMMITTED | Prevented | Possible | Possible |
| REPEATABLE READ | Prevented | Prevented | Possible |
| SERIALIZABLE | Prevented | Prevented | Prevented |

Berenson and colleagues pointed out that this table misses lost update, read skew and write skew, and that **snapshot isolation** (each transaction reads from a consistent snapshot taken at its start, and a transaction aborts if it tries to write a row that another transaction changed after its snapshot) fits nowhere: it prevents all three standard phenomena yet permits write skew, so it is not serializable [Berenson et al. 1995]. Real databases implement the levels differently, so the level *name* tells you little; check the behavior.

**Table 11.9 — Anomalies permitted in practice (PostgreSQL 16, MySQL 8.0 InnoDB).**

| Anomaly | PG READ COMMITTED (default) | PG REPEATABLE READ (snapshot isolation) | PG SERIALIZABLE (SSI) | MySQL READ COMMITTED | MySQL REPEATABLE READ (default) | MySQL SERIALIZABLE |
|---|---|---|---|---|---|---|
| Dirty read | No | No | No | No | No | No |
| Non-repeatable read | Yes | No | No | Yes | No | No |
| Phantom | Yes | No | No | Yes | No for plain reads | No |
| Lost update | Yes | No (error) | No | Yes | **Yes** | No |
| Read skew | Yes | No | No | Yes | No | No |
| Write skew | Yes | Yes | No | Yes | Yes | No |

Key facts behind the table:

- **PostgreSQL** accepts `READ UNCOMMITTED` but runs it as READ COMMITTED. REPEATABLE READ is snapshot isolation. SERIALIZABLE (since 9.1) is **Serializable Snapshot Isolation (SSI)**: snapshot isolation plus tracking of read–write dependencies, aborting a transaction when a cycle is possible [Cahill et al. 2008; Ports and Grittner 2012]. It takes no extra blocking locks, but applications must retry on serialization failures (SQLSTATE `40001`).
- **MySQL InnoDB** defaults to REPEATABLE READ. Plain `SELECT`s read a snapshot, but `UPDATE`, `DELETE` and locking reads (`SELECT ... FOR UPDATE`) read the *latest committed* row and do not check whether it changed since the snapshot, which is why lost updates and write skew get through. Locking reads take next-key locks that block phantom inserts (§11.15). SERIALIZABLE converts plain `SELECT`s into `SELECT ... FOR SHARE` when autocommit is off, i.e., two-phase locking [MySQL Docs: Transaction Isolation Levels].
- Kleppmann's Hermitage project collects independent tests of these behaviors [Kleppmann 2014].

The following program reproduced two rows of Table 11.9 against PostgreSQL 16:

```python
# PostgreSQL-specific: needs a running PostgreSQL and `pip install psycopg2-binary`.
import psycopg2

DSN = "dbname=shop user=postgres host=localhost"   # adjust to your server

def session(level):
    conn = psycopg2.connect(DSN)
    conn.set_session(isolation_level=level)
    return conn, conn.cursor()

def reset():
    conn = psycopg2.connect(DSN); conn.autocommit = True
    conn.cursor().execute("""
        DROP TABLE IF EXISTS stock, doctors;
        CREATE TABLE stock (product_id int PRIMARY KEY, on_hand int NOT NULL);
        INSERT INTO stock VALUES (42, 10);
        CREATE TABLE doctors (name text PRIMARY KEY, on_call bool NOT NULL);
        INSERT INTO doctors VALUES ('alice', true), ('bob', true);""")
    conn.close()

def try_commit(conn):
    try:
        conn.commit(); return "commit"
    except psycopg2.Error as e:
        conn.rollback(); return "abort: " + e.pgerror.splitlines()[0]

def lost_update(level):           # read-modify-write computed in the application
    reset(); (a, ca), (b, cb) = session(level), session(level)
    ca.execute("SELECT on_hand FROM stock WHERE product_id = 42"); va = ca.fetchone()[0]
    cb.execute("SELECT on_hand FROM stock WHERE product_id = 42"); vb = cb.fetchone()[0]
    ca.execute("UPDATE stock SET on_hand = %s WHERE product_id = 42", (va - 1,)); a.commit()
    try:
        cb.execute("UPDATE stock SET on_hand = %s WHERE product_id = 42", (vb - 1,))
        result = try_commit(b)
    except psycopg2.Error as e:
        b.rollback(); result = "abort: " + e.pgerror.splitlines()[0]
    print(f"lost update, {level}: B {result}")

def write_skew(level):            # invariant: at least one doctor on call
    reset(); (a, ca), (b, cb) = session(level), session(level)
    for cur, me in ((ca, "alice"), (cb, "bob")):
        cur.execute("SELECT count(*) FROM doctors WHERE on_call")
        if cur.fetchone()[0] >= 2:
            cur.execute("UPDATE doctors SET on_call = false WHERE name = %s", (me,))
    print(f"write skew, {level}: A {try_commit(a)}; B {try_commit(b)}")

for level in ("READ COMMITTED", "REPEATABLE READ"):
    lost_update(level)
for level in ("REPEATABLE READ", "SERIALIZABLE"):
    write_skew(level)
```

Output on PostgreSQL 16.15:

```text
lost update, READ COMMITTED: B commit
lost update, REPEATABLE READ: B abort: ERROR:  could not serialize access due to concurrent update
write skew, REPEATABLE READ: A commit; B commit
write skew, SERIALIZABLE: A commit; B abort: ERROR:  could not serialize access due to read/write dependencies among transactions
```

What to notice:

- Two sessions are interleaved by hand in one thread; nothing blocks, because PostgreSQL readers never wait for writers.
- At REPEATABLE READ and SERIALIZABLE, an abort is *normal* behavior, not a bug. Production code wraps such transactions in a retry loop with a bounded number of attempts.

::: recommendation
**Recommendation — Choosing an isolation level.** Default to READ COMMITTED (PostgreSQL) and make every read-modify-write atomic in SQL (`SET x = x - 1 WHERE ... AND x >= 1`) or explicitly locked (`FOR UPDATE`). Use SERIALIZABLE, with retries, for transactions that check an invariant across several rows and then write. In MySQL, do not assume REPEATABLE READ protects read-modify-write cycles; use locking reads.
:::

## 11.14 Multi-version concurrency control (MVCC)

### 11.14.1 The idea

::: definition
**Definition — MVCC.** A concurrency-control technique in which a write creates a new **version** of a row instead of overwriting it in place, and each transaction reads the versions visible in its **snapshot**: the set of transactions that had committed when the snapshot was taken. Readers therefore never block writers and writers never block readers; only writers of the same row wait for each other.
:::

#### First-principles explanation

A library keeps every edition of a reference book; a reader arriving at 10:00 gets the edition current at 10:00, even if a new one is shelved at 10:05. Editors never wait for readers. The costs are shelf space and a librarian who discards editions nobody can still be reading. PostgreSQL and InnoDB differ in *where* they keep old editions and *who* discards them.

### 11.14.2 PostgreSQL: versions in the heap, cleaned by VACUUM

Each heap tuple carries a header with **`xmin`** (the ID of the transaction that created this version), **`xmax`** (the ID of the transaction that deleted or replaced it, or 0) and **`ctid`** (the location of this version, or of its successor). An `UPDATE` sets `xmax` on the old version and inserts a complete new version. A snapshot records the oldest still-running transaction ID, the next unassigned ID and the list of IDs in progress; a version is visible if its `xmin` committed before the snapshot and its `xmax` is empty, aborted or not yet visible to the snapshot [PostgreSQL Docs: Concurrency Control].

Real output from PostgreSQL 16 after inserting a stock row and updating it twice (the `pageinspect` extension shows raw page contents):

```sql
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
```

**Figure 11.9 — PostgreSQL version chain for product 42.**

```mermaid
flowchart LR
  IX["B+ tree index entry<br/>product_id 42 to TID 0,1"] --> V1["lp 1: on_hand 10<br/>xmin 993, xmax 994"]
  V1 -->|"t_ctid"| V2["lp 2: on_hand 9<br/>xmin 994, xmax 995"]
  V2 -->|"t_ctid"| V3["lp 3: on_hand 8<br/>xmin 995, xmax 0"]
  S1(["Snapshot taken before 994 commits"]) -.->|"sees"| V1
  S2(["Snapshot taken after 995 commits"]) -.->|"sees"| V3
  VAC["VACUUM"] -->|"reclaims lp 2,<br/>redirects lp 1 to lp 3"| V1
```

**Reading the diagram.** All three versions sit in heap page 0. The updates changed no indexed column and the page had room, so they were **heap-only tuple (HOT)** updates: the index still points to line pointer 1 and readers follow `t_ctid` links to the version their snapshot can see (dotted arrows show visibility, not messages). On the real page, VACUUM turned line pointer 1 into a redirect to 3 and freed 2. Failure point: a long-running transaction pins an old snapshot, so VACUUM cannot clean dead versions in any table and tables bloat. Scaling: an update that changes an indexed column or finds the page full is not HOT, and every index gets a new entry.

**VACUUM** (run automatically by **autovacuum**) removes dead versions, records free space for reuse, updates the **visibility map** that index-only scans rely on (§11.7.4), and **freezes** old tuples. Freezing matters because transaction IDs are 32-bit counters compared with wrap-around arithmetic: only about $2^{31}$ IDs are "in the past" at any moment. A tuple must be frozen (marked as visible to everyone) before its `xmin` becomes 2 billion transactions old, or it would appear to be in the future [PostgreSQL Docs: Routine Vacuuming].

::: formula
**Time until transaction-ID wraparound**

$$T_{\text{wrap}} = \frac{2^{31} - A}{\lambda_{\text{xid}}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $T_{\text{wrap}}$ | Time until PostgreSQL must stop assigning transaction IDs | seconds |
| $A$ | Current age of the oldest unfrozen transaction ID in the database | transactions |
| $\lambda_{\text{xid}}$ | Rate of transactions that write (read-only transactions consume no ID) | transactions/second |
:::

::: example
**Worked example — How long can freezing be blocked?** A shop database commits $\lambda_{\text{xid}} = 5{,}000$ writing transactions per second. Autovacuum normally forces an anti-wraparound vacuum once a table's oldest ID reaches `autovacuum_freeze_max_age` = 200 million (the default).

1. Time to reach the forced-vacuum threshold from zero: $2 \times 10^8 / 5{,}000 = 40{,}000$ s, about 11 hours.
2. Suppose a forgotten idle transaction blocks freezing at age $A = 2 \times 10^8$. Remaining headroom: $2^{31} - 2 \times 10^8 = 2{,}147{,}483{,}648 - 200{,}000{,}000 \approx 1.95 \times 10^9$.
3. $T_{\text{wrap}} = 1.95 \times 10^9 / 5{,}000 = 389{,}497$ s, about 4.5 days.

**Interpretation.** A busy database burns through its safety margin in days, not years. As it approaches the limit PostgreSQL emits warnings and eventually refuses new writing transactions until a vacuum completes. **Engineering implication.** Alert on `age(datfrozenxid)` and on transactions open longer than a few minutes (`pg_stat_activity.xact_start`), and never leave sessions "idle in transaction" (`idle_in_transaction_session_timeout`).
:::

::: industry
**Sentry — transaction ID wraparound outage.** Sentry published a postmortem of an outage in which its PostgreSQL database stopped accepting writes to prevent transaction ID wraparound, and service returned only after vacuuming. The lesson: in PostgreSQL, vacuum is part of the write path's capacity budget, not optional maintenance.
*Evidence: Primary* — [Sentry 2015]
:::

### 11.14.3 InnoDB: update in place, old versions in the undo log

InnoDB updates the row *in place* in the clustered index and writes the *previous* values to an **undo log** record. Each clustered-index record has hidden columns `DB_TRX_ID` (the last transaction to modify it, 6 bytes) and `DB_ROLL_PTR` (a pointer to the undo record holding the previous version, 7 bytes). A consistent read creates a **read view** (the set of transactions it must not see); if the current row is too new, InnoDB follows the roll pointers backwards, reconstructing older versions until it reaches a visible one. A background **purge** thread discards undo records no read view needs; the backlog appears as the **history list length** in `SHOW ENGINE INNODB STATUS` [MySQL Docs: InnoDB Multi-Versioning].

**Figure 11.10 — InnoDB current row and undo chain for product 42.**

```mermaid
flowchart LR
  CI[("Clustered index leaf<br/>on_hand 8, DB_TRX_ID 995")] -->|"DB_ROLL_PTR"| U2[["Undo record<br/>on_hand 9, trx 994"]]
  U2 -->|"roll pointer"| U1[["Undo record<br/>on_hand 10, trx 993"]]
  RV(["Read view that cannot see 995"]) -.->|"reconstructs"| U2
  PU["Purge thread"] -->|"discards when no read view needs"| U1
```

**Reading the diagram.** The cylinder is the one current version in the clustered index; the subroutine shapes are undo records, linked newest to oldest. A reader whose read view excludes transaction 995 applies undo backwards until it reaches a visible version (dotted arrow: a visibility decision). Purge is asynchronous background work. Failure point: a long transaction blocks purge, the history list grows and hot-row reads walk ever-longer chains. Scaling benefit: updates do not bloat the table, and secondary indexes change only when their columns change.

**Table 11.10 — MVCC in PostgreSQL and InnoDB.**

| Aspect | PostgreSQL | MySQL InnoDB |
|---|---|---|
| Where old versions live | In the table heap, next to current ones | In undo logs, outside the table |
| What an update writes | A complete new tuple (and index entries unless HOT) | In-place change plus an undo record |
| Version metadata | `xmin`, `xmax`, `ctid` in each tuple header | `DB_TRX_ID`, `DB_ROLL_PTR` hidden columns |
| Reading an old version | Scan to the visible tuple; cheap | Reconstruct by applying undo; cost grows with chain length |
| Garbage collection | VACUUM / autovacuum; must also freeze XIDs | Purge threads |
| Rollback cost | Nearly free (versions never become visible) | Must apply undo to restore rows |
| Symptom of a long transaction | Table and index bloat; wraparound risk | Growing history list; slower reads |

## 11.15 Locking

### 11.15.1 Two-phase locking and lock granularity

::: definition
**Definition — Two-phase locking (2PL).** A protocol in which each transaction acquires locks (shared **S** for reading, exclusive **X** for writing) before accessing data and, once it releases any lock, acquires no new ones: a *growing* phase followed by a *shrinking* phase. **Strict 2PL** holds all X locks until commit or abort. Any schedule produced by 2PL is serializable [Eswaran et al. 1976].
:::

S locks are compatible with each other; X locks conflict with everything. MVCC databases lock mainly for *writes*: two updates of one row serialize on its row lock, while plain reads take no row locks. Granularities:

- **Row locks** — taken by `UPDATE`, `DELETE` and explicit `SELECT ... FOR UPDATE` / `FOR SHARE`. PostgreSQL also has weaker `FOR NO KEY UPDATE` and `FOR KEY SHARE` modes so that foreign-key checks do not block updates of non-key columns.
- **Table locks** — PostgreSQL has eight table-lock modes from `ACCESS SHARE` (taken by every `SELECT`) to `ACCESS EXCLUSIVE` (taken by most `ALTER TABLE` forms) [PostgreSQL Docs: Explicit Locking]. InnoDB uses **intention locks** (IS, IX) on the table to signal row locks below.
- **Gap and next-key locks (InnoDB)** — at REPEATABLE READ, a locking read or update over a range locks the index records it scans *and the gaps between them* (a **next-key lock** is a record lock plus the gap before it). This blocks inserts into the range, preventing phantoms, at the price of extra blocking [MySQL Docs: InnoDB Locking]. READ COMMITTED disables most gap locking.

`SELECT ... FOR UPDATE SKIP LOCKED` (PostgreSQL 9.5+, MySQL 8.0+) lets many workers pull different rows from a job table without blocking on each other, a common way to build a simple, transactional work queue.

::: warning
**Warning — A schema change can stop all traffic.** `ALTER TABLE orders ADD COLUMN ...` needs PostgreSQL's `ACCESS EXCLUSIVE` lock for at least a moment. If a long report query holds `ACCESS SHARE`, the `ALTER` waits, and every new query on `orders` queues *behind the waiting `ALTER`*. Set `lock_timeout` (for example 2 s) on migrations and retry; use online schema-change tools for MySQL (such as GitHub's gh-ost [GitHub gh-ost]).
:::

### 11.15.2 Deadlocks

A **deadlock** occurs when transactions wait for each other's locks in a cycle (§6.11). Databases detect cycles in the **wait-for graph** and abort one transaction, the **victim**. PostgreSQL checks for a cycle after a waiter has been blocked for `deadlock_timeout` (default 1 s); InnoDB detects them immediately by default (`innodb_deadlock_detect`), and otherwise relies on `innodb_lock_wait_timeout` (default 50 s) [MySQL Docs: Deadlock Detection].

**Figure 11.11 — A deadlock between two checkouts, as reproduced on PostgreSQL 16.**

```mermaid
sequenceDiagram
  participant A as Txn A - cart 42 then 43
  participant DB as PostgreSQL
  participant B as Txn B - cart 43 then 42
  A->>DB: UPDATE inventory product 42
  B->>DB: UPDATE inventory product 43
  A->>DB: UPDATE inventory product 43
  Note over A,DB: A waits for B
  B->>DB: UPDATE inventory product 42
  Note over B,DB: B waits for A - cycle
  DB-->>A: ERROR deadlock detected after about 1 s
  DB-->>B: UPDATE 1, then COMMIT succeeds
```

**Reading the diagram.** Each checkout updates inventory rows in cart order with synchronous, blocking statements. A holds 42 and waits for 43; B holds 43 and waits for 42: a cycle in the wait-for graph. After A had waited `deadlock_timeout`, PostgreSQL aborted it with `deadlock detected` (SQLSTATE `40P01`) and B's update proceeded. The cost is a retried transaction and up to a second of latency, and deadlocks become more frequent as concurrency grows. **Prevention:** acquire locks in a canonical order, for example by sorting cart lines by `product_id`, as the code in §11.17 does.

### 11.15.3 Hot rows and optimistic concurrency

::: formula
**Throughput ceiling of a single hot row**

$$X_{\max} = \frac{1}{t_{\text{hold}}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $X_{\max}$ | Maximum transactions per second that can update the same row | transactions/second |
| $t_{\text{hold}}$ | Time each transaction holds the row's X lock (from its update to commit) | seconds |
:::

::: example
**Worked example — A flash sale on one product.** Each checkout updates the product's `inventory` row, then (wrongly) calls a payment provider inside the transaction before committing.

1. With a 200 ms payment call inside the transaction: $X_{\max} = 1/0.2 = 5$ checkouts per second, however many servers you add.
2. Payment moved outside the transaction; update and commit take 2 ms including a commit flush and one network round trip: $X_{\max} = 1/0.002 = 500$ per second.
3. Stock split into 10 bucket rows (each holding a tenth of the units, chosen at random per checkout): about $10 \times 500 = 5{,}000$ per second.

**Interpretation.** Lock hold time, not CPU, bounds a hot row: this is Little's Law (§4.11) applied to a lock with capacity one. **Engineering implication.** Keep slow work out of transactions, update hot rows last (just before commit) so the lock is held briefly, and split hot counters when one row cannot keep up.
:::

When conflicts are rare, **optimistic concurrency control** avoids holding locks across user think time: write only if the row's version is unchanged since you read it.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE products (
  product_id  INTEGER PRIMARY KEY,
  description TEXT    NOT NULL,
  version     INTEGER NOT NULL DEFAULT 1
);
INSERT INTO products (product_id, description) VALUES (7, 'Blue mug');
""")

def save(product_id, new_description, version_read):
    """Optimistic concurrency control: the write succeeds only if nobody wrote since we read."""
    with db:
        cur = db.execute(
            "UPDATE products SET description = ?, version = version + 1 "
            "WHERE product_id = ? AND version = ?",
            (new_description, product_id, version_read))
    return cur.rowcount == 1          # 0 rows updated means a concurrent edit won

# Two editors load the same row (version 1), then both try to save.
_, _, v_alice = db.execute("SELECT * FROM products WHERE product_id = 7").fetchone()
_, _, v_bob = db.execute("SELECT * FROM products WHERE product_id = 7").fetchone()
print("alice saved:", save(7, "Blue ceramic mug", v_alice))
print("bob saved:  ", save(7, "Navy mug", v_bob))       # rejected: must re-read and retry
print(db.execute("SELECT * FROM products").fetchall())
```

What to notice:

- Output: Alice's save returns `True`, Bob's `False`, and the row is `(7, 'Blue ceramic mug', 2)`: Bob's stale edit is rejected instead of silently overwriting Alice's (a lost update prevented without locks).
- The check-and-write is one atomic `UPDATE`; HTTP APIs expose the same idea with `ETag` and `If-Match` headers.

## 11.16 PostgreSQL versus MySQL

### 11.16.1 Comparison

Both are mature, open-source ACID databases that handle most transactional workloads well; the differences decide edge cases, operations and ecosystem fit.

**Table 11.11 — PostgreSQL and MySQL (InnoDB) compared, as of PostgreSQL 16–18 and MySQL 8.0–8.4.**

| Row | PostgreSQL | MySQL (InnoDB) |
|---|---|---|
| What it is | Extensible object-relational database; PostgreSQL License | Relational database; GPLv2 community edition plus commercial editions (Oracle) |
| How it works | Heap tables, all indexes secondary (TID pointers); MVCC versions in heap; VACUUM; process per connection; 8 KiB pages | Index-organized tables clustered on PK; secondary indexes store PK; MVCC via undo logs; purge; thread per connection; 16 KiB pages |
| Advantages | Rich SQL (CTEs, window functions, `JSONB`, partial/expression indexes, GIN/GiST/BRIN), transactional DDL, SSI serializable, extensions (PostGIS, pgvector) | Fast PK lookups and PK range scans, compact secondary-index updates, mature replication tooling, very wide hosting and operator familiarity |
| Disadvantages | Vacuum tuning and XID wraparound; non-HOT updates touch every index; connections are costly (needs a pooler, §14.13) | No partial indexes; DDL not transactional (atomic since 8.0, but commits implicitly); REPEATABLE READ allows lost updates; gap-lock surprises |
| Performance | Strong on complex queries, joins and analytics-style SQL; good write throughput when HOT applies | Strong on simple PK-centric OLTP and high connection counts; secondary lookups cost two tree descents |
| Operational complexity | Autovacuum, bloat and freeze monitoring; major-version upgrades via `pg_upgrade` or logical replication | Purge lag and undo growth; online schema change tools for large tables |
| Cost | Free; managed offerings on all major clouds | Free community edition; managed offerings on all major clouds; commercial support from Oracle |
| Use cases | Complex domains, geospatial, JSON-heavy data, mixed OLTP and reporting | High-volume web OLTP with simple access patterns; large existing MySQL ecosystems |
| Choose when | You need advanced SQL, data types, extensions or serializable isolation | Your team and tooling know MySQL, or the workload is dominated by PK access and you rely on its replication ecosystem |

**Table 11.12 — Defaults and behaviors that change application code.**

| Behavior | PostgreSQL | MySQL InnoDB |
|---|---|---|
| Default isolation level | READ COMMITTED | REPEATABLE READ |
| Serializable implementation | SSI (optimistic, aborts) | 2PL with shared locks (blocking) |
| Phantom protection at REPEATABLE READ | Snapshot | Snapshot for reads; next-key locks for locking reads |
| Join algorithms | Nested loop, hash, merge | Nested loop, hash (8.0.18+) |
| Partial indexes | Yes | No |
| `INCLUDE` covering columns | Yes (11+) | Implicit PK only |
| Deadlock detection | After `deadlock_timeout` (1 s) | Immediate by default |

::: industry
**Uber — moving a core datastore from PostgreSQL to MySQL (2016).** Uber's engineering blog attributed the move to PostgreSQL's physical design at its scale: non-HOT updates write new entries in every index (write amplification), physical WAL replication shipped those amplified changes across data centers, and MVCC on replicas interacted badly with long queries. InnoDB's PK-pointer secondary indexes and row-based replication fit its write pattern better. PostgreSQL practitioners responded with mitigations (HOT-friendly schemas, `fillfactor`, logical replication). The lesson is to match storage design to workload.
*Evidence: Primary* — [Klitzke 2016]
:::

## 11.17 Data modeling for a real application

### 11.17.1 Requirements to schema

The order service must reserve stock and create an order atomically, never oversell, accept retries without duplicates, record payments, show order history newest first and report best sellers. We model it in five steps:

1. **Entities and relationships** from nouns and verbs: customers *place* orders; orders *contain* items; items *reference* products; products *have* inventory; orders are *paid by* payments.
2. **Keys**: `bigint` identity surrogates; natural keys (`email`, `sku`, `provider_ref`, `idempotency_key`) as `UNIQUE`.
3. **Normalize** to BCNF (§11.5), keeping historical facts (`unit_price_cents`, `ship_to`) on the order.
4. **Invariants as constraints**: `CHECK (on_hand >= 0)` makes overselling impossible.
5. **Indexes from queries**: one per access path, and no others.

**Figure 11.12 — Entity–relationship diagram of the order system.**

```mermaid
erDiagram
  CUSTOMERS ||--o{ ORDERS : places
  ORDERS ||--|{ ORDER_ITEMS : contains
  PRODUCTS ||--o{ ORDER_ITEMS : "appears in"
  PRODUCTS ||--|| INVENTORY : "stocked as"
  ORDERS ||--o{ PAYMENTS : "paid by"
  CUSTOMERS {
    bigint customer_id PK
    text email UK
    text full_name
    text city
  }
  PRODUCTS {
    bigint product_id PK
    text sku UK
    text name
    int price_cents
  }
  INVENTORY {
    bigint product_id PK, FK
    int on_hand
  }
  ORDERS {
    bigint order_id PK
    bigint customer_id FK
    text status
    text ship_to
    bigint total_cents
    text idempotency_key UK
    timestamptz created_at
  }
  ORDER_ITEMS {
    bigint order_id PK, FK
    smallint line_no PK
    bigint product_id FK
    int quantity
    int unit_price_cents
  }
  PAYMENTS {
    bigint payment_id PK
    bigint order_id FK
    bigint amount_cents
    text provider_ref UK
    text status
  }
```

**Reading the diagram.** Each box is a table with key markers (PK, FK, UK); crow's-foot lines give cardinality: a customer places zero or more orders, an order has one or more items, a product has exactly one inventory row, an order has zero or more payment attempts. Every line is a foreign key enforced synchronously inside one database, the single storage boundary. Failure points are rows many transactions touch: the `inventory` rows of popular products (§11.15.3). Scaling: read replicas for history and reports (§14.3), then partitioning orders and items by `customer_id` (§14.7).

### 11.17.2 DDL (PostgreSQL)

The following DDL was run on PostgreSQL 16:

```sql
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
```

What to notice:

- Money is stored as integer cents (or `numeric`), never floating point. Timestamps use `timestamptz`.
- `order_items` has a composite primary key `(order_id, line_no)`: its leading column serves "items of this order" and the foreign-key check, so no separate index on `order_items.order_id` is needed.
- `total_cents` is a stored aggregate (a denormalization, §11.5.5) written in the same transaction as the items; it is also the amount charged, a fact worth keeping.
- `status` uses `CHECK` rather than a separate lookup table or PostgreSQL `ENUM` type; adding a status later is a one-line constraint change.

### 11.17.3 The place-order transaction and core queries

The order service runs this transaction (shown with literal values; the application binds parameters). The decrements are atomic conditional updates, sorted by `product_id` to avoid deadlocks; the idempotency key makes retries safe (§22.15):

```sql
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
```

The complete model also runs on SQLite through Python's standard library; this script creates the schema, places an order, retries it with the same idempotency key, attempts an order that would oversell, and runs the history, best-seller and anti-join queries:

```python
"""E-commerce order schema and queries (Section 11.17), runnable with Python's sqlite3.
The PostgreSQL DDL in the chapter differs only in types (bigint identity, timestamptz)."""
import sqlite3

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  full_name   TEXT NOT NULL,
  city        TEXT NOT NULL,
  created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE products (
  product_id  INTEGER PRIMARY KEY,
  sku         TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);
CREATE TABLE inventory (
  product_id INTEGER PRIMARY KEY REFERENCES products,
  on_hand    INTEGER NOT NULL CHECK (on_hand >= 0)
);
CREATE TABLE orders (
  order_id        INTEGER PRIMARY KEY,
  customer_id     INTEGER NOT NULL REFERENCES customers,
  status          TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','paid','shipped','cancelled')),
  ship_to         TEXT NOT NULL,
  total_cents     INTEGER NOT NULL DEFAULT 0 CHECK (total_cents >= 0),
  idempotency_key TEXT NOT NULL UNIQUE,
  created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE order_items (
  order_id         INTEGER NOT NULL REFERENCES orders ON DELETE CASCADE,
  line_no          INTEGER NOT NULL,
  product_id       INTEGER NOT NULL REFERENCES products,
  quantity         INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
  PRIMARY KEY (order_id, line_no)
);
CREATE TABLE payments (
  payment_id   INTEGER PRIMARY KEY,
  order_id     INTEGER NOT NULL REFERENCES orders,
  amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
  provider_ref TEXT UNIQUE,
  status       TEXT NOT NULL CHECK (status IN ('authorized','captured','failed','refunded')),
  created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX orders_customer_created ON orders (customer_id, created_at DESC, order_id DESC);
CREATE INDEX order_items_product     ON order_items (product_id);
CREATE INDEX payments_order          ON payments (order_id);
CREATE INDEX orders_pending_created  ON orders (created_at) WHERE status = 'pending';
"""

class OutOfStock(Exception):
    pass

def place_order(db, customer_id, ship_to, items, idempotency_key):
    """items: list of (product_id, quantity). Returns order_id. All-or-nothing."""
    with db:  # BEGIN ... COMMIT, or ROLLBACK if an exception escapes
        row = db.execute(
            "INSERT INTO orders (customer_id, ship_to, idempotency_key) VALUES (?, ?, ?) "
            "ON CONFLICT (idempotency_key) DO NOTHING RETURNING order_id",
            (customer_id, ship_to, idempotency_key)).fetchone()
        if row is None:  # a retry of a request we already processed
            return db.execute("SELECT order_id FROM orders WHERE idempotency_key = ?",
                              (idempotency_key,)).fetchone()[0]
        order_id, total = row[0], 0
        for line_no, (product_id, qty) in enumerate(sorted(items), start=1):  # fixed lock order
            cur = db.execute(
                "UPDATE inventory SET on_hand = on_hand - ? WHERE product_id = ? AND on_hand >= ?",
                (qty, product_id, qty))
            if cur.rowcount != 1:
                raise OutOfStock(product_id)  # aborts the whole transaction
            price = db.execute("SELECT price_cents FROM products WHERE product_id = ?",
                               (product_id,)).fetchone()[0]
            db.execute("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)",
                       (order_id, line_no, product_id, qty, price))
            total += qty * price
        db.execute("UPDATE orders SET total_cents = ? WHERE order_id = ?", (total, order_id))
        return order_id

ORDER_HISTORY = """
SELECT order_id, status, total_cents, created_at
FROM orders
WHERE customer_id = :cid
  AND (created_at, order_id) < (:after_created, :after_id)   -- keyset cursor
ORDER BY created_at DESC, order_id DESC
LIMIT 20"""

TOP_PRODUCTS = """
SELECT p.sku, SUM(i.quantity) AS units, SUM(i.quantity * i.unit_price_cents) AS revenue_cents
FROM order_items i
JOIN orders   o ON o.order_id   = i.order_id
JOIN products p ON p.product_id = i.product_id
WHERE o.status <> 'cancelled'
GROUP BY p.sku
ORDER BY revenue_cents DESC
LIMIT 3"""

NO_ORDERS = """
SELECT c.email FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)"""

db = sqlite3.connect(":memory:")  # default mode: BEGIN issued implicitly before DML
db.executescript(SCHEMA)
db.executemany("INSERT INTO customers (email, full_name, city) VALUES (?, ?, ?)",
               [("ana@example.com", "Ana", "Pune"), ("bo@example.com", "Bo", "Lima")])
db.executemany("INSERT INTO products (sku, name, price_cents) VALUES (?, ?, ?)",
               [("MUG-1", "Mug", 1200), ("TEE-1", "T-shirt", 2500), ("CAP-1", "Cap", 1800)])
db.execute("INSERT INTO inventory SELECT product_id, 5 FROM products")

o1 = place_order(db, 1, "1 Main St", [(2, 1), (1, 2)], "key-001")
o1_retry = place_order(db, 1, "1 Main St", [(2, 1), (1, 2)], "key-001")
print("order", o1, "retry returns", o1_retry)
try:
    place_order(db, 1, "1 Main St", [(3, 99), (1, 1)], "key-002")
except OutOfStock as e:
    print("out of stock: product", e.args[0])
print("inventory:", db.execute("SELECT product_id, on_hand FROM inventory").fetchall())
print("orders:", db.execute("SELECT order_id, total_cents FROM orders").fetchall())
print("history:", db.execute(ORDER_HISTORY, {"cid": 1, "after_created": "9999", "after_id": 0}).fetchall())
print("top products:", db.execute(TOP_PRODUCTS).fetchall())
print("no orders:", db.execute(NO_ORDERS).fetchall())
print("plan:", db.execute("EXPLAIN QUERY PLAN " + ORDER_HISTORY,
                          {"cid": 1, "after_created": "9999", "after_id": 0}).fetchall()[0][3])
try:
    db.execute("INSERT INTO orders (customer_id, ship_to, idempotency_key) VALUES (99, 'x', 'k')")
except sqlite3.IntegrityError as e:
    print("foreign key enforced:", e)
```

What to notice:

- Output: the retry returns the same order (1); the oversell attempt raises `OutOfStock` for product 3 and leaves inventory at `[(1, 3), (2, 4), (3, 5)]`. Product 1 had already been decremented (lines are processed in `product_id` order) when product 3 failed, and the rollback restored it. Only one order exists, with total 4,900 cents.
- The history query uses a keyset cursor (§8.6.5); the first page passes a cursor greater than any real value. Its plan is `SEARCH orders USING INDEX orders_customer_created (customer_id=? AND created_at<?)`: the composite index serves both the filter and the sort.
- Best sellers: `TEE-1` (2,500 cents) then `MUG-1` (2,400 cents); the anti-join finds `bo@example.com`, who never ordered.

**Table 11.13 — Failure scenarios in the order system.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Overselling | Read-then-write stock check in the application | Negative-stock or oversold reports | Cancel and refund | Conditional `UPDATE ... AND on_hand >= q` plus `CHECK (on_hand >= 0)` |
| Duplicate orders on client retry | Timeout after commit; client retries | Two orders with identical items seconds apart | Refund duplicate | `UNIQUE` idempotency key; `ON CONFLICT DO NOTHING` |
| Deadlocks at peak | Carts lock inventory rows in different orders | `deadlock detected` errors in logs | Automatic retry | Sort lines by `product_id` before updating |
| Checkout stalls during a sale | Payment call inside the transaction holds a hot row lock | Lock waits in `pg_stat_activity`; p99 latency | Kill long transactions | Pay outside the transaction; short transactions; split hot counters |
| Order history slows over time | Missing or wrong composite index; offset pagination | `EXPLAIN` shows sort or scan | Add index | Index `(customer_id, created_at DESC, order_id DESC)`; keyset pagination |

## 11.18 Summary and revision notes

::: summary
- Relations are typed sets related by values; physical data independence lets the database choose access paths [Codd 1970].
- Use surrogate primary keys, `UNIQUE` natural keys and foreign keys; index the child columns you join or delete through.
- Normalize the source of truth to 3NF/BCNF on functional dependencies, with lossless splits; denormalize only for measured reads, with a named consistency mechanism. Prices at purchase time are history, not redundancy.
- Join algorithms: index nested loop for small outer inputs (OLTP), hash join for large unsorted equality joins, sort-merge when inputs are sorted. The right choice depends on row counts, so cardinality estimation drives performance.
- Composite indexes follow the leftmost-prefix rule (equality columns first, then range/sort). Covering indexes avoid table reads; partial indexes index only hot subsets. A secondary index pays off only below a break-even selectivity, about 0.4% of rows in our example.
- A B+ tree with 16 KiB pages indexes $10^9$ rows in 4 levels; with internal pages cached, a lookup costs about one random I/O (two for an InnoDB secondary index). The leaf working set, not height, limits scale.
- Plans are trees of Volcano iterators; blocking operators need memory and can spill. In `EXPLAIN ANALYZE`, compare estimated and actual rows at each node.
- ACID: atomicity (undo), consistency (constraints), isolation (concurrency control), durability (WAL + fsync, §13.5). ACID consistency is unrelated to linearizability or CAP consistency.
- Isolation-level names differ by database. PostgreSQL: READ COMMITTED default, REPEATABLE READ = snapshot isolation (prevents lost update by aborting, allows write skew), SERIALIZABLE = SSI. MySQL: REPEATABLE READ default, allows lost updates and write skew for read-modify-write cycles.
- MVCC keeps old versions so readers never block writers: PostgreSQL in the heap (VACUUM, freezing, wraparound), InnoDB in undo logs (purge). Long-running transactions hurt both.
- Writers still lock rows (strict 2PL for writes); InnoDB adds gap/next-key locks. Avoid deadlocks with a canonical lock order; a hot row's throughput is at most $1/t_{\text{hold}}$, so keep slow work out of transactions.
:::

## 11.19 Knowledge checkpoint

1. Why does `WHERE coupon_code <> 'SPRING'` not return rows where `coupon_code` is NULL?
2. A table `enrollment(student_id, course_id, course_title, grade)` has key `(student_id, course_id)`. Which normal form does it violate, and how do you fix it?
3. Why is storing `unit_price_cents` in `order_items` not a normalization violation?
4. Estimate the I/O cost of a block nested-loop join with $M = 1{,}000$, $N = 5{,}000$ and $B = 102$ buffer pages.
5. Which of these queries can use an index on `(customer_id, created_at)`: (a) `customer_id = 5`, (b) `created_at > X`, (c) `customer_id = 5 ORDER BY created_at`?
6. How many levels does a B+ tree need for $10^8$ rows with $f = 500$ and $L = 100$?
7. What makes an operator "blocking" in the Volcano model? Name three.
8. Distinguish the C in ACID from the C in CAP.
9. Which anomaly does PostgreSQL REPEATABLE READ allow that SERIALIZABLE prevents? Give an example.
10. Does MySQL InnoDB REPEATABLE READ prevent lost updates from `SELECT` then `UPDATE ... SET x = <computed value>`?
11. Why does a long-running idle transaction cause table bloat in PostgreSQL?
12. A transaction holds a hot row's lock for 10 ms. What is the maximum update rate on that row?

<details><summary>Answers</summary>

1. Comparisons with NULL evaluate to UNKNOWN, and `WHERE` keeps only TRUE rows. Use `IS DISTINCT FROM` or add `OR coupon_code IS NULL`.
2. 2NF: `course_title` depends only on `course_id`, part of the key. Move it to `courses(course_id, course_title)`.
3. It records the price charged at purchase time, a different fact from the product's current price; it is determined by the order line, not by `product_id`.
4. $1{,}000 + \lceil 1{,}000/100 \rceil \times 5{,}000 = 1{,}000 + 50{,}000 = 51{,}000$ I/Os.
5. (a) and (c). (b) cannot seek because `created_at` is not a leftmost prefix (only a full index scan or skip scan is possible).
6. Leaves: $10^8/100 = 10^6$. $\lceil \log_{500} 10^6 \rceil = \lceil 2.22 \rceil = 3$. Height $= 1 + 3 = 4$.
7. It must consume all input before producing its first output row: sort, hash aggregate, hash-join build side (also materialize).
8. ACID consistency: transactions preserve declared invariants in one database. CAP consistency: linearizability, i.e., every read of replicated data sees the latest completed write.
9. Write skew. Two doctors each check that two are on call and each sets themselves off call; both commit under REPEATABLE READ.
10. No. The `UPDATE` reads the latest committed row without checking it against the snapshot. Use `SELECT ... FOR UPDATE`, an atomic `SET x = x - 1`, or a version check.
11. Its snapshot may still need old row versions, so VACUUM cannot remove any version that became dead after the snapshot was taken, in any table.
12. $1/0.010 = 100$ updates per second.

</details>

## 11.20 Interview questions

### Basic

**Q1. What is a database index, and what does it cost?**
**Answer.** A sorted structure, usually a B+ tree, mapping key values to row locations, so a selective lookup costs a few page reads instead of a full scan (about 4 levels at $10^9$ rows, roughly 1 I/O with internal pages cached). Costs: every write to indexed columns updates the index, extra storage and memory, and no benefit for low-selectivity predicates. Index the real workload: composite indexes with the leftmost-prefix rule, covering indexes for hot paths, drop unused ones.

**Q2. Explain ACID with an example.**
**Answer.** Transferring \$70 from A to B: atomicity, both debit and credit happen or neither; consistency, declared invariants (no negative balance, valid references) hold after commit; isolation, a concurrent report never sees money in flight; durability, once "committed" is returned a crash cannot lose it, because the WAL was flushed. Note that ACID consistency differs from distributed "strong consistency".

### Intermediate

**Q3. Two users buy the last unit of a product at the same moment. How do you guarantee you do not oversell?**
**Answer.** Make check and decrement one atomic statement, `UPDATE inventory SET on_hand = on_hand - 1 WHERE product_id = ? AND on_hand >= 1`, treat 0 rows updated as out of stock, and back it with `CHECK (on_hand >= 0)`. The row lock serializes the updates; the second finds 0. Alternatives: `SELECT ... FOR UPDATE`, or SERIALIZABLE with retries. Application read-modify-write loses updates at READ COMMITTED and at MySQL REPEATABLE READ. For a flash sale, discuss hot-row throughput ($1/t_{\text{hold}}$), payment outside the transaction and stock buckets.

**Q4. A query that took 5 ms now takes 4 s after a large data import. How do you investigate?**
**Answer.** Capture `EXPLAIN (ANALYZE, BUFFERS)` and find nodes where estimated and actual rows differ by an order of magnitude; after an import, stale statistics are likely, so run `ANALYZE`. If correlated predicates keep estimates wrong, add extended statistics. Check for unusable indexes (functions, casts), spills (`external merge`, `Batches > 1`) and cold caches (`Buffers read`). Then guard with analyze settings and `pg_stat_statements` monitoring.

### Advanced

**Q5. Compare PostgreSQL's and InnoDB's MVCC, and explain how each fails under a long-running analytics query on the primary.**
**Answer.** PostgreSQL writes a new heap tuple per update (`xmin`/`xmax`), adds index entries for non-HOT updates, and relies on VACUUM to remove dead versions and freeze XIDs. InnoDB updates in place, keeps prior versions in undo logs and purges them in the background. A multi-hour query holds an old snapshot: in PostgreSQL, VACUUM cannot remove newer dead versions, so hot tables bloat, index-only scans degrade and freezing stalls; in InnoDB, purge stalls, the history list grows and hot-row reads walk longer undo chains. Mitigations: run analytics on a replica or warehouse, set statement and idle-in-transaction timeouts, monitor `age(datfrozenxid)` and history list length.

**Q6. Design the concurrency control for an "at least one admin per organization" rule.**
**Answer.** This is write skew: each demotion checks a count, then writes a different row. Options: (1) SERIALIZABLE (PostgreSQL SSI) with a retry loop; simplest, with occasional aborts. (2) Materialize the conflict: `SELECT ... FROM organizations WHERE org_id = ? FOR UPDATE` before counting, so changes in one organization serialize; works at READ COMMITTED and in MySQL. (3) A stored `admin_count` with `CHECK (admin_count >= 1)` updated in the same transaction. REPEATABLE READ alone is insufficient in both databases; across shards the invariant needs a single owner (Chapter 28).

## 11.21 Practical exercises

1. Load the §11.17 schema into PostgreSQL with one million orders (use `generate_series`). Run the order-history query before and after creating `orders_customer_created_idx` with `EXPLAIN (ANALYZE, BUFFERS)`; record pages read and time.
2. Reproduce the correlated-columns misestimate of §11.10 and fix it with `CREATE STATISTICS`. Then build a three-table join where the misestimate changes the join algorithm.
3. Run the isolation program of §11.13 at all four PostgreSQL levels and, if you have MySQL, adapt it to MySQL 8; fill in Table 11.9 from your own results.
4. Install `pageinspect`, update one row 10 times with and without an index on the updated column, and observe HOT chains, `n_tup_hot_upd` and the effect of `VACUUM`.
5. Write a load test with 50 concurrent clients buying from 5 products in random cart order. Count deadlocks, then sort cart lines by `product_id` and count again.

## 11.22 Design challenges

1. **Seat reservation.** Model a cinema with seats, showings and bookings so that a seat can never be double-booked, even under concurrent requests and client retries. Choose constraints, isolation level and indexes, and justify each.
2. **Ledger.** Design a double-entry ledger (accounts, journal entries, postings) in which every entry balances to zero and balances can be read in O(1). Decide what is normalized, what is a stored aggregate, and how the aggregate stays correct.
3. **Multi-tenant SaaS schema.** One PostgreSQL cluster hosts 5,000 tenants of very different sizes. Compare a shared schema with a `tenant_id` column, schema-per-tenant and database-per-tenant on index design, isolation, migrations and noisy neighbors; prepare the move of large tenants to shards (Chapter 14).

## 11.23 References

1. Codd, E. F. "A Relational Model of Data for Large Shared Data Banks." *Communications of the ACM* 13(6), 1970.
2. Ramakrishnan, R., Gehrke, J. *Database Management Systems*, 3rd ed. McGraw-Hill, 2003.
3. Bayer, R., McCreight, E. "Organization and Maintenance of Large Ordered Indexes." *Acta Informatica* 1(3), 1972.
4. Comer, D. "The Ubiquitous B-Tree." *ACM Computing Surveys* 11(2), 1979.
5. Lehman, P. L., Yao, S. B. "Efficient Locking for Concurrent Operations on B-Trees." *ACM Transactions on Database Systems* 6(4), 1981.
6. Kent, W. "A Simple Guide to Five Normal Forms in Relational Database Theory." *Communications of the ACM* 26(2), 1983.
7. Selinger, P. G., Astrahan, M. M., Chamberlin, D. D., Lorie, R. A., Price, T. G. "Access Path Selection in a Relational Database Management System." *Proceedings of ACM SIGMOD*, 1979.
8. Graefe, G. "Volcano — An Extensible and Parallel Query Evaluation System." *IEEE Transactions on Knowledge and Data Engineering* 6(1), 1994.
9. Graefe, G. "Query Evaluation Techniques for Large Databases." *ACM Computing Surveys* 25(2), 1993.
10. Boncz, P., Zukowski, M., Nes, N. "MonetDB/X100: Hyper-Pipelining Query Execution." *CIDR*, 2005.
11. Neumann, T. "Efficiently Compiling Efficient Query Plans for Modern Hardware." *Proceedings of the VLDB Endowment* 4(9), 2011.
12. Leis, V., Gubichev, A., Mirchev, A., Boncz, P., Kemper, A., Neumann, T. "How Good Are Query Optimizers, Really?" *Proceedings of the VLDB Endowment* 9(3), 2015.
13. Eswaran, K. P., Gray, J. N., Lorie, R. A., Traiger, I. L. "The Notions of Consistency and Predicate Locks in a Database System." *Communications of the ACM* 19(11), 1976.
14. Härder, T., Reuter, A. "Principles of Transaction-Oriented Database Recovery." *ACM Computing Surveys* 15(4), 1983.
15. Gray, J., Reuter, A. *Transaction Processing: Concepts and Techniques*. Morgan Kaufmann, 1993.
16. Berenson, H., Bernstein, P., Gray, J., Melton, J., O'Neil, E., O'Neil, P. "A Critique of ANSI SQL Isolation Levels." *Proceedings of ACM SIGMOD*, 1995.
17. Cahill, M. J., Röhm, U., Fekete, A. D. "Serializable Isolation for Snapshot Databases." *Proceedings of ACM SIGMOD*, 2008.
18. Ports, D. R. K., Grittner, K. "Serializable Snapshot Isolation in PostgreSQL." *Proceedings of the VLDB Endowment* 5(12), 2012.
19. Kleppmann, M. *Designing Data-Intensive Applications*. O'Reilly, 2017 (chapters 3 and 7).
20. Kleppmann, M. *Hermitage: Testing Transaction Isolation Levels*. 2014. https://github.com/ept/hermitage
21. Petrov, A. *Database Internals*. O'Reilly, 2019.
22. PostgreSQL Global Development Group. *PostgreSQL 16 Documentation: Concurrency Control*. https://www.postgresql.org/docs/16/mvcc.html
23. PostgreSQL Global Development Group. *PostgreSQL 16 Documentation: Using EXPLAIN*. https://www.postgresql.org/docs/16/using-explain.html
24. PostgreSQL Global Development Group. *PostgreSQL 16 Documentation: Routine Vacuuming*. https://www.postgresql.org/docs/16/routine-vacuuming.html
25. PostgreSQL Global Development Group. *PostgreSQL 16 Documentation: Explicit Locking*. https://www.postgresql.org/docs/16/explicit-locking.html
26. Oracle. *MySQL 8.0 Reference Manual: Transaction Isolation Levels*. https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html
27. Oracle. *MySQL 8.0 Reference Manual: InnoDB Locking*. https://dev.mysql.com/doc/refman/8.0/en/innodb-locking.html
28. Oracle. *MySQL 8.0 Reference Manual: InnoDB Multi-Versioning*. https://dev.mysql.com/doc/refman/8.0/en/innodb-multi-versioning.html
29. Oracle. *MySQL 8.0 Reference Manual: Clustered and Secondary Indexes*. https://dev.mysql.com/doc/refman/8.0/en/innodb-index-types.html
30. Oracle. *MySQL 8.0 Reference Manual: Deadlock Detection*. https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlock-detection.html
31. Oracle. *MySQL 8.0 Reference Manual: Hash Join Optimization*. https://dev.mysql.com/doc/refman/8.0/en/hash-joins.html
32. Instagram Engineering. "Sharding & IDs at Instagram." Instagram Engineering Blog, 2012.
33. Klitzke, E. "Why Uber Engineering Switched from Postgres to MySQL." Uber Engineering Blog, 2016.
34. Sentry. "Transaction ID Wraparound in Postgres." Sentry Blog, 2015.
35. GitHub. *gh-ost: GitHub's Online Schema-migration Tool for MySQL*. https://github.com/github/gh-ost

## 11.24 Open verification items

- PostgreSQL 18 B-tree skip scan (stated as available from version 18, released 2025) and MySQL 8.4 still lacking partial indexes: confirm against current release notes.
- Sentry 2015 wraparound postmortem: title, date and details are from memory; confirm URL and wording.
- Uber 2016 blog post URL (moved from eng.uber.com); Instagram 2012 post URL.
- Exact PostgreSQL 16 thresholds for wraparound warnings and write refusal (stated qualitatively here).
- Claim that MySQL 8.0/8.4 has no sort-merge join.
