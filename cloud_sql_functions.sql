-- ============================================================
-- EJTech CRM — Custom PostgreSQL Functions for Cloud SQL
-- Run this file ONCE against your Cloud SQL database AFTER
-- importing the data dump:
--
--   psql "host=<CLOUD_SQL_IP> dbname=ejtech user=ejtech password=<PW>" \
--        -f cloud_sql_functions.sql
--
-- These functions replicate SQLite built-ins used by the app.
-- ============================================================

-- ------------------------------------------------------------
-- 1. public.date(text)  →  date
--    Converts 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' text to date.
--    Uses to_date() internally to avoid circular dependency with
--    the implicit TEXT→DATE cast created below.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.date(txt text)
 RETURNS date
 LANGUAGE plpgsql
 STABLE
AS $function$
DECLARE
    result date;
BEGIN
    IF txt IS NULL OR txt = '' THEN
        RETURN NULL;
    END IF;
    BEGIN
        result := to_date(substring(txt FROM 1 FOR 10), 'YYYY-MM-DD');
        RETURN result;
    EXCEPTION WHEN OTHERS THEN
        RETURN NULL;
    END;
END;
$function$;

-- ------------------------------------------------------------
-- 2. public.datetime(text, text)  →  timestamptz
--    public.datetime(timestamp)   →  timestamptz
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.datetime(what text, modifier text DEFAULT '')
 RETURNS timestamp with time zone
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
DECLARE
    base_ts TIMESTAMPTZ;
BEGIN
    IF lower(what) = 'now' THEN
        base_ts := NOW();
    ELSE
        BEGIN
            base_ts := what::TIMESTAMPTZ;
        EXCEPTION WHEN OTHERS THEN
            RETURN NULL;
        END;
    END IF;
    IF modifier = '' OR lower(modifier) IN ('localtime','utc') THEN
        RETURN base_ts;
    END IF;
    BEGIN
        RETURN base_ts + trim(modifier)::INTERVAL;
    EXCEPTION WHEN OTHERS THEN
        RETURN base_ts;
    END;
END;
$function$;

CREATE OR REPLACE FUNCTION public.datetime(ts timestamp without time zone)
 RETURNS timestamp with time zone
 LANGUAGE sql
 IMMUTABLE
AS $function$ SELECT ts AT TIME ZONE 'UTC'; $function$;

CREATE OR REPLACE FUNCTION public.datetime(ts timestamp without time zone, modifier text)
 RETURNS timestamp with time zone
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
BEGIN
    IF modifier = '' OR lower(modifier) IN ('localtime','utc') THEN
        RETURN ts AT TIME ZONE 'UTC';
    END IF;
    BEGIN
        RETURN (ts AT TIME ZONE 'UTC') + trim(modifier)::INTERVAL;
    EXCEPTION WHEN OTHERS THEN
        RETURN ts AT TIME ZONE 'UTC';
    END;
END;
$function$;

-- ------------------------------------------------------------
-- 3. public.strftime(fmt text, dt text|timestamp)  →  text
--    Replicates SQLite strftime() format codes.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.strftime(fmt text, dt text)
 RETURNS text
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
DECLARE
    pg_fmt TEXT;
    ts TIMESTAMP;
BEGIN
    IF dt IS NULL OR dt = '' THEN
        RETURN NULL;
    END IF;
    BEGIN
        ts := dt::TIMESTAMP;
    EXCEPTION WHEN OTHERS THEN
        RETURN NULL;
    END;
    pg_fmt := replace(fmt, '%Y', 'YYYY');
    pg_fmt := replace(pg_fmt, '%m', 'MM');
    pg_fmt := replace(pg_fmt, '%d', 'DD');
    pg_fmt := replace(pg_fmt, '%H', 'HH24');
    pg_fmt := replace(pg_fmt, '%M', 'MI');
    pg_fmt := replace(pg_fmt, '%S', 'SS');
    RETURN TO_CHAR(ts, pg_fmt);
END;
$function$;

CREATE OR REPLACE FUNCTION public.strftime(fmt text, dt timestamp without time zone)
 RETURNS text
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
DECLARE
    pg_fmt TEXT;
BEGIN
    IF dt IS NULL THEN RETURN NULL; END IF;
    pg_fmt := replace(fmt, '%Y', 'YYYY');
    pg_fmt := replace(pg_fmt, '%m', 'MM');
    pg_fmt := replace(pg_fmt, '%d', 'DD');
    pg_fmt := replace(pg_fmt, '%H', 'HH24');
    pg_fmt := replace(pg_fmt, '%M', 'MI');
    pg_fmt := replace(pg_fmt, '%S', 'SS');
    RETURN TO_CHAR(dt, pg_fmt);
END;
$function$;

-- ------------------------------------------------------------
-- 4. public.printf(fmt text, val anyelement)  →  text
--    Replicates SQLite printf() for common format strings.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.printf(fmt text, val anyelement)
 RETURNS text
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
BEGIN
    IF fmt = '%,.2f' OR fmt = '%.2f' THEN
        RETURN TO_CHAR(val::NUMERIC, 'FM999,999,999,990.00');
    ELSIF fmt = '%d' THEN
        RETURN TRUNC(val::NUMERIC)::TEXT;
    ELSE
        RETURN val::TEXT;
    END IF;
END;
$function$;

-- ------------------------------------------------------------
-- 5. public.group_concat(text) / group_concat(text, text)
--    Replicates SQLite GROUP_CONCAT() aggregate.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public._gc_sfn(state text, val text)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
AS $function$
    SELECT CASE
        WHEN val IS NULL THEN state
        WHEN state IS NULL OR state = '' THEN val
        ELSE state || ',' || val
    END;
$function$;

CREATE OR REPLACE FUNCTION public._gc2_sfn(state text, val text, sep text)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
AS $function$
    SELECT CASE
        WHEN val IS NULL THEN state
        WHEN state IS NULL OR state = '' THEN val
        ELSE state || sep || val
    END;
$function$;

DROP AGGREGATE IF EXISTS public.group_concat(text);
CREATE AGGREGATE public.group_concat(text) (
    SFUNC     = public._gc_sfn,
    STYPE     = text,
    INITCOND  = ''
);

DROP AGGREGATE IF EXISTS public.group_concat(text, text);
CREATE AGGREGATE public.group_concat(text, text) (
    SFUNC     = public._gc2_sfn,
    STYPE     = text,
    INITCOND  = ''
);

-- ------------------------------------------------------------
-- 6. Implicit cast: TEXT → DATE (via public.date)
--    Allows cross-type comparisons like:
--      registered_date_text_col <= deadline_date_col
--    NOTE: uses public.date() which uses to_date() internally,
--    NOT ::date cast, to avoid circular recursion.
-- ------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_cast c
        JOIN pg_type src ON c.castsource = src.oid
        JOIN pg_type tgt ON c.casttarget = tgt.oid
        WHERE src.typname = 'text' AND tgt.typname = 'date'
    ) THEN
        CREATE CAST (text AS date)
            WITH FUNCTION public.date(text)
            AS IMPLICIT;
    END IF;
END
$$;

-- Done
SELECT 'Custom functions and casts installed successfully.' AS status;
