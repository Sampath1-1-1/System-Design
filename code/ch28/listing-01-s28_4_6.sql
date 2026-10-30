-- Extracted from manuscript/book1-traditional/28-distributed-transactions.md §28.4.6 (listing 1). Edit the manuscript, not this file.
-- On shard A (acct 7 = 50000 cents) and shard B (acct 9 = 0): phase 1
BEGIN;                                            -- shard A
UPDATE accounts SET balance_cents = balance_cents - 10000 WHERE account_id = 7;
PREPARE TRANSACTION 'xfer-42';
BEGIN;                                            -- shard B
UPDATE accounts SET balance_cents = balance_cents + 10000 WHERE account_id = 9;
PREPARE TRANSACTION 'xfer-42';

-- The "coordinator" disappears. On shard A:
SELECT gid, prepared FROM pg_prepared_xacts;
SET lock_timeout = '1s';
UPDATE accounts SET balance_cents = balance_cents - 1 WHERE account_id = 7;

-- Restart shard A (pg_ctl restart), then:
SELECT gid FROM pg_prepared_xacts;
SELECT * FROM accounts;

-- The coordinator's log says COMMIT: phase 2 on both shards
COMMIT PREPARED 'xfer-42';                        -- shard A, then shard B
