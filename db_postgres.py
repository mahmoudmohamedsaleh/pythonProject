"""
PostgreSQL compatibility adapter for code originally written for sqlite3.

Drop-in replacement:
    import db_postgres as sqlite3
    conn = sqlite3.connect('ProjectStatus.db')   # arg ignored

Handles:
- ? → %s placeholder translation
- row_factory = sqlite3.Row  (returns dict-like rows)
- cursor.lastrowid            (via SELECT lastval())
- sqlite3.IntegrityError / sqlite3.OperationalError aliases
- AUTOINCREMENT in inline SQL  (skipped at DDL level by migrate script)
"""

import os
import re
import datetime
import decimal
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from psycopg2 import IntegrityError, OperationalError, DatabaseError, ProgrammingError


def _sqlite_val(v):
    """Convert PostgreSQL Python types to SQLite-compatible equivalents.

    SQLite returns everything as str/int/float/None/bytes.
    PostgreSQL returns typed objects (datetime, Decimal, bool, etc.).
    Templates written for SQLite expect string-slicing, string methods, etc.
    """
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(v, datetime.date):
        return v.strftime('%Y-%m-%d')
    if isinstance(v, datetime.timedelta):
        total = int(v.total_seconds())
        h, rem = divmod(abs(total), 3600)
        m, s = divmod(rem, 60)
        return f'{h:02d}:{m:02d}:{s:02d}'
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, memoryview):
        return bytes(v)
    return v

_PLACEHOLDER_RE = re.compile(r'\?')
_INSERT_OR_IGNORE_RE = re.compile(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', re.IGNORECASE)
_INSERT_OR_REPLACE_RE = re.compile(r'\bINSERT\s+OR\s+REPLACE\s+INTO\b', re.IGNORECASE)
_PERCENT_LITERAL_RE = re.compile(r'%([^s%])')
_DATETIME_NOW_RE = re.compile(
    r"\bdatetime\s*\(\s*'now'\s*(?:,\s*'(?:localtime|utc)'\s*)?\)", re.IGNORECASE
)
_DATE_NOW_RE = re.compile(r"\bdate\s*\(\s*'now'\s*\)", re.IGNORECASE)
_ALTER_ADD_COL_RE = re.compile(
    r'(ALTER\s+TABLE\s+\S+\s+ADD\s+COLUMN\s+)(?!IF\s+NOT\s+EXISTS)',
    re.IGNORECASE
)
_AUTOINCREMENT_RE = re.compile(r'\bAUTOINCREMENT\b', re.IGNORECASE)
_BLOB_RE = re.compile(r'\bBLOB\b', re.IGNORECASE)
_DATETIME_DEFAULT_NOW_RE = re.compile(
    r"DEFAULT\s+\(?\s*datetime\s*\(\s*'now'[^)]*\)\s*\)?", re.IGNORECASE
)
_EMPTY_STRING_DEFAULT_RE = re.compile(r'DEFAULT\s+""', re.IGNORECASE)
_PRAGMA_TABLE_INFO_RE = re.compile(
    r'^\s*PRAGMA\s+table_info\s*\(\s*(\w+)\s*\)\s*$', re.IGNORECASE
)


def _to_pg(sql):
    """Replace SQLite ? placeholders with PostgreSQL %s and fix SQLite DML."""
    sql = _PLACEHOLDER_RE.sub('%s', sql)
    sql = _DATETIME_NOW_RE.sub('CURRENT_TIMESTAMP', sql)
    sql = _DATE_NOW_RE.sub('CURRENT_DATE', sql)
    stripped = sql.strip()
    if _INSERT_OR_IGNORE_RE.search(stripped):
        sql = _INSERT_OR_IGNORE_RE.sub('INSERT INTO', sql)
        sql = sql.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'
    elif _INSERT_OR_REPLACE_RE.search(stripped):
        sql = _INSERT_OR_REPLACE_RE.sub('INSERT INTO', sql)
        sql = sql.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'
    return sql


def _patch_ddl(sql):
    """Fix SQLite-specific DDL so PostgreSQL can parse it."""
    stripped = sql.strip().upper()

    if stripped.startswith('ALTER TABLE') and 'ADD COLUMN' in stripped:
        sql = _ALTER_ADD_COL_RE.sub(r'\1IF NOT EXISTS ', sql)

    if stripped.startswith('CREATE TABLE') or stripped.startswith('ALTER TABLE'):
        sql = _AUTOINCREMENT_RE.sub('', sql)
        sql = _BLOB_RE.sub('BYTEA', sql)
        sql = _DATETIME_DEFAULT_NOW_RE.sub("DEFAULT CURRENT_TIMESTAMP", sql)
        sql = _EMPTY_STRING_DEFAULT_RE.sub("DEFAULT ''", sql)

    return sql


def _get_dsn():
    url = os.getenv('DATABASE_URL')
    if url:
        return url
    return {
        'host': os.getenv('PGHOST', 'localhost'),
        'port': int(os.getenv('PGPORT', 5432)),
        'user': os.getenv('PGUSER'),
        'password': os.getenv('PGPASSWORD'),
        'dbname': os.getenv('PGDATABASE'),
    }


class Row(dict):
    """sqlite3.Row-compatible dict that also supports index access."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

    def keys(self):
        return list(super().keys())

    def get(self, key, default=None):
        return super().get(key, default)


def _convert_row_dict(row):
    """Convert a psycopg2 dict row to a Row with SQLite-compatible value types."""
    return Row({k: _sqlite_val(v) for k, v in row.items()})


def _convert_row_tuple(row):
    """Convert a psycopg2 tuple row to a tuple with SQLite-compatible value types."""
    return tuple(_sqlite_val(v) for v in row)


class Cursor:
    def __init__(self, pg_cursor, use_dict=False):
        self._cur = pg_cursor
        self._use_dict = use_dict
        self.lastrowid = None
        self.rowcount = -1

    def execute(self, sql, params=None):
        pragma_match = _PRAGMA_TABLE_INFO_RE.match(sql.strip())
        if pragma_match:
            table_name = pragma_match.group(1).lower()
            pg_sql = """
                SELECT ordinal_position - 1 AS cid,
                       column_name AS name,
                       data_type AS type,
                       CASE is_nullable WHEN 'NO' THEN 1 ELSE 0 END AS notnull,
                       column_default AS dflt_value,
                       0 AS pk
                FROM information_schema.columns
                WHERE table_name = %s
                  AND table_schema = current_schema()
                ORDER BY ordinal_position
            """
            self._cur.execute(pg_sql, (table_name,))
            self.rowcount = self._cur.rowcount
            self.lastrowid = None
            return
        sql = _to_pg(sql)
        sql = _patch_ddl(sql)
        if params is not None:
            sql = _PERCENT_LITERAL_RE.sub(r'%%\1', sql)
        try:
            if params is not None:
                self._cur.execute(sql, params)
            else:
                self._cur.execute(sql)
        except psycopg2.errors.DuplicateColumn:
            return
        except psycopg2.errors.DuplicateTable:
            return
        self.rowcount = self._cur.rowcount
        self.lastrowid = None
        if sql.strip().upper().startswith('INSERT'):
            try:
                self._cur.execute('SELECT lastval()')
                row = self._cur.fetchone()
                self.lastrowid = row[0] if row else None
            except Exception:
                self.lastrowid = None

    def executemany(self, sql, seq):
        sql = _to_pg(sql)
        sql = _PERCENT_LITERAL_RE.sub(r'%%\1', sql)
        self._cur.executemany(sql, seq)
        self.rowcount = self._cur.rowcount

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        if self._use_dict and isinstance(row, dict):
            return _convert_row_dict(row)
        return _convert_row_tuple(row)

    def fetchall(self):
        rows = self._cur.fetchall()
        if not rows:
            return rows
        if self._use_dict and isinstance(rows[0], dict):
            return [_convert_row_dict(r) for r in rows]
        return [_convert_row_tuple(r) for r in rows]

    def fetchmany(self, size=None):
        rows = self._cur.fetchmany(size) if size else self._cur.fetchmany()
        if not rows:
            return rows
        if self._use_dict and isinstance(rows[0], dict):
            return [_convert_row_dict(r) for r in rows]
        return [_convert_row_tuple(r) for r in rows]

    def __iter__(self):
        for row in self._cur:
            if self._use_dict and isinstance(row, dict):
                yield _convert_row_dict(row)
            else:
                yield _convert_row_tuple(row)

    def close(self):
        self._cur.close()

    @property
    def description(self):
        return self._cur.description


class Connection:
    def __init__(self, pg_conn):
        self._conn = pg_conn
        self._conn.autocommit = False
        self.row_factory = None

    def cursor(self):
        use_dict = (self.row_factory is not None)
        if use_dict:
            pg_cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            pg_cur = self._conn.cursor()
        return Cursor(pg_cur, use_dict=use_dict)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

    @property
    def total_changes(self):
        return 0


class _FakeRowClass:
    """Acts as sqlite3.Row class for row_factory assignment."""
    pass


Row_factory = _FakeRowClass()


def connect(_db_path=None):
    """Connect to PostgreSQL. The db_path argument is ignored (kept for compatibility)."""
    dsn = _get_dsn()
    if isinstance(dsn, str):
        pg_conn = psycopg2.connect(dsn)
    else:
        pg_conn = psycopg2.connect(**dsn)
    return Connection(pg_conn)
