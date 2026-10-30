-- Extracted from manuscript/book1-traditional/12-nosql-databases.md §12.6.3 (listing 3). Edit the manuscript, not this file.
-- Q1: one partition per sensor per day (the "bucket")
CREATE TABLE readings_by_sensor_day (
    sensor_id   uuid,
    day         date,
    ts          timestamp,
    temperature float,
    humidity    float,
    battery     float,
    PRIMARY KEY ((sensor_id, day), ts)
) WITH CLUSTERING ORDER BY (ts DESC)
  AND default_time_to_live = 7776000;      -- 90 days

-- Q2: one partition per site; one row per sensor, overwritten on each reading
CREATE TABLE latest_by_site (
    site_id     text,
    sensor_id   uuid,
    ts          timestamp,
    temperature float,
    PRIMARY KEY ((site_id), sensor_id)
);

SELECT ts, temperature FROM readings_by_sensor_day
 WHERE sensor_id = 5b6e0f6a-1c1e-4a51-9a52-0c2f7f0b7d11 AND day = '2026-10-30'
 LIMIT 100;
