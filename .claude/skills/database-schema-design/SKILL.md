---
name: database-schema-design
description: Design and optimize Snowflake database schemas. Use when creating tables, views, stages, pipes, streams, tasks, or data sharing. Handles Snowflake-specific features like VARIANT, CLUSTER BY, COPY INTO, Time Travel, zero-copy clones, dynamic tables, and data sharing.
metadata:
  tags: database, schema, Snowflake, SQL, VARIANT, stage, pipe, stream, task
---

# Snowflake Database Schema Design

## When to use this skill

- **New Project**: Snowflake database/schema design for a new data pipeline
- **Schema Refactoring**: Redesigning for performance or cost optimization
- **Data Ingestion**: Stage, pipe, file format, COPY INTO design
- **Real-time Processing**: Streams and tasks for CDC (Change Data Capture)
- **Performance Issues**: Clustering keys, materialized views, search optimization

## Input Format

### Required Information
- **Database/Schema**: Target database and schema name
- **Domain Description**: What data will be stored
- **Key Entities**: Core data objects

### Optional Information
- **Data Volume**: Small (<1M rows), Medium (1M-1B), Large (>1B) (default: Medium)
- **Ingestion Pattern**: Batch, micro-batch, streaming (default: Batch)
- **Query Pattern**: Ad-hoc analytics, dashboard, real-time (default: Analytics)
- **Warehouse Size**: XS, S, M, L, XL (default: S)

## Instructions

### Step 1: Define Tables and Data Types

Snowflake data types and best practices:

```sql
CREATE TABLE raw.events (
    event_id        STRING NOT NULL,          -- STRING preferred over VARCHAR for flexibility
    event_timestamp TIMESTAMP_NTZ NOT NULL,   -- NTZ for UTC-normalized data
    user_id         STRING,
    event_type      STRING NOT NULL,
    payload         VARIANT,                  -- Semi-structured data (JSON, Avro, Parquet)
    metadata        OBJECT,                   -- Key-value pairs
    tags            ARRAY,                    -- Array of values
    loaded_at       TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file    STRING,                   -- Audit: source file name
    _load_ts        TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
```

**Snowflake-specific types:**
- `VARIANT` — Semi-structured data (JSON, Avro, Parquet). Max 16MB compressed per value.
- `OBJECT` — Key-value pairs (subset of VARIANT)
- `ARRAY` — Ordered collection (subset of VARIANT)
- `GEOGRAPHY` / `GEOMETRY` — Geospatial data
- `TIMESTAMP_NTZ` — No timezone (for UTC-normalized data)
- `TIMESTAMP_LTZ` — Local timezone (for load timestamps)
- `TIMESTAMP_TZ` — With timezone info preserved

### Step 2: Design Layer Architecture (Bronze/Silver/Gold)

```
RAW (Bronze)     -> STAGING (Silver)    -> ANALYTICS (Gold)
Landing zone        Cleaned/typed          Business-ready
VARIANT columns     Typed columns          Aggregated views
Append-only         Deduped/validated      Star schema
```

```sql
-- Bronze: Raw landing
CREATE SCHEMA raw;
CREATE TABLE raw.events (
    raw_data    VARIANT,
    _source     STRING,
    _loaded_at  TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Silver: Cleaned and typed
CREATE SCHEMA staging;
CREATE TABLE staging.events AS
SELECT
    raw_data:event_id::STRING       AS event_id,
    raw_data:timestamp::TIMESTAMP_NTZ AS event_ts,
    raw_data:user_id::STRING        AS user_id,
    raw_data:event_type::STRING     AS event_type,
    raw_data:payload                AS payload,
    _loaded_at
FROM raw.events;

-- Gold: Business aggregates
CREATE SCHEMA analytics;
CREATE TABLE analytics.daily_active_users AS
SELECT
    DATE_TRUNC('DAY', event_ts)    AS activity_date,
    COUNT(DISTINCT user_id)        AS dau
FROM staging.events
GROUP BY 1;
```

### Step 3: Data Ingestion (Stages, File Formats, COPY INTO)

```sql
-- File format
CREATE FILE FORMAT my_json_format
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE
    COMPRESSION = 'AUTO';

CREATE FILE FORMAT my_parquet_format
    TYPE = 'PARQUET'
    COMPRESSION = 'SNAPPY';

-- External stage (S3)
CREATE STAGE raw_stage
    URL = 's3://my-bucket/data/'
    STORAGE_INTEGRATION = my_s3_integration
    FILE_FORMAT = my_json_format;

-- Internal stage
CREATE STAGE internal_stage
    FILE_FORMAT = my_parquet_format;

-- COPY INTO (batch load)
COPY INTO raw.events
FROM @raw_stage
PATTERN = '.*\.json\.gz'
ON_ERROR = 'CONTINUE'
FILE_FORMAT = my_json_format;

-- Snowpipe (auto-ingest)
CREATE PIPE raw.events_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO raw.events
FROM @raw_stage
FILE_FORMAT = my_json_format;
```

### Step 4: Clustering and Performance

```sql
-- Clustering key (for large tables with predictable query patterns)
ALTER TABLE staging.events
    CLUSTER BY (DATE_TRUNC('DAY', event_ts), event_type);

-- Search optimization (for point lookups on large tables)
ALTER TABLE staging.events
    ADD SEARCH OPTIMIZATION ON EQUALITY(event_id, user_id);

-- Materialized view (auto-refreshed aggregate)
CREATE MATERIALIZED VIEW analytics.mv_hourly_events AS
SELECT
    DATE_TRUNC('HOUR', event_ts) AS hour,
    event_type,
    COUNT(*) AS event_count
FROM staging.events
GROUP BY 1, 2;

-- Dynamic table (declarative pipeline)
CREATE DYNAMIC TABLE analytics.user_summary
    TARGET_LAG = '1 hour'
    WAREHOUSE = MOVING_INTEL_WH
AS
SELECT
    user_id,
    COUNT(*) AS total_events,
    MIN(event_ts) AS first_seen,
    MAX(event_ts) AS last_seen
FROM staging.events
GROUP BY user_id;
```

### Step 5: Streams and Tasks (CDC)

```sql
-- Stream: capture changes on staging table
CREATE STREAM staging.events_stream
    ON TABLE staging.events
    APPEND_ONLY = TRUE;

-- Task: process stream every 5 minutes
CREATE TASK staging.process_events_task
    WAREHOUSE = MOVING_INTEL_WH
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('staging.events_stream')
AS
INSERT INTO analytics.daily_active_users
SELECT
    DATE_TRUNC('DAY', event_ts) AS activity_date,
    COUNT(DISTINCT user_id) AS dau
FROM staging.events_stream
GROUP BY 1;

-- Enable task
ALTER TASK staging.process_events_task RESUME;
```

## Constraints

### Mandatory Rules (MUST)

1. **Use VARIANT for semi-structured data** — Don't flatten JSON into 100+ columns at ingestion
2. **Layer architecture** — Raw -> Staging -> Analytics (Bronze/Silver/Gold)
3. **Audit columns** — `_source_file`, `_load_ts` on all raw tables
4. **TIMESTAMP_NTZ for business timestamps** — Normalize to UTC at ingestion
5. **Clustering keys on large tables** — Only when query patterns are clear and table > 1TB

### Prohibited Actions (MUST NOT)

1. **No UPDATE on raw tables** — Raw layer is append-only
2. **No SELECT * in production views** — Explicit column lists only
3. **No AUTOINCREMENT for distributed keys** — Use UUID or business keys
4. **No excessive clustering** — Only cluster when micro-partition pruning benefit is clear
5. **No plaintext secrets in SQL** — Use STORAGE_INTEGRATION, not inline credentials

### Snowflake-Specific Best Practices

- **Time Travel**: Set `DATA_RETENTION_TIME_IN_DAYS` appropriately (1 for dev, 7-90 for prod)
- **Zero-Copy Clone**: Use for dev/test environments (`CREATE TABLE ... CLONE ...`)
- **Transient tables**: Use for staging/temp data (no Fail-safe, lower cost)
- **Resource monitors**: Set credit limits on warehouses
- **Tags**: Use object tagging for governance (`ALTER TABLE ... SET TAG ...`)

## Common Issues

### Issue 1: VARIANT Query Performance

**Symptom**: Slow queries on VARIANT columns

**Solution**:
```sql
-- Materialize frequently accessed paths
CREATE TABLE staging.events_typed AS
SELECT
    raw_data:event_id::STRING AS event_id,
    raw_data:timestamp::TIMESTAMP_NTZ AS event_ts,
    raw_data
FROM raw.events;

-- Or use search optimization
ALTER TABLE raw.events ADD SEARCH OPTIMIZATION
    ON EQUALITY(raw_data:event_id);
```

### Issue 2: Small File Problem

**Symptom**: Thousands of small files degrade performance

**Solution**:
```sql
-- Consolidate small files
ALTER TABLE raw.events RECLUSTER;

-- Or use COPY with FILE_SIZE option
COPY INTO @stage/output/
FROM staging.events
FILE_FORMAT = my_parquet_format
MAX_FILE_SIZE = 268435456;  -- 256MB
```

### Issue 3: Warehouse Credits Explosion

**Symptom**: Unexpected credit consumption

**Solution**:
```sql
-- Resource monitor
CREATE RESOURCE MONITOR monthly_limit
    WITH CREDIT_QUOTA = 100
    TRIGGERS
        ON 75 PERCENT DO NOTIFY
        ON 90 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

-- Auto-suspend idle warehouses
ALTER WAREHOUSE MOVING_INTEL_WH
    SET AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
```

## References

- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference)
- [Snowflake Best Practices](https://docs.snowflake.com/en/user-guide/best-practices)
- [Snowflake Data Engineering](https://docs.snowflake.com/en/user-guide/data-pipelines-intro)
