"""
Migration script: SQLite (ProjectStatus.db) -> PostgreSQL (Replit built-in)
"""

import os
import re
import sqlite3
import psycopg2
import psycopg2.extras

SQLITE_DB = 'ProjectStatus.db'


def get_pg_conn():
    url = os.getenv('DATABASE_URL')
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.getenv('PGHOST'),
        port=int(os.getenv('PGPORT', 5432)),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        dbname=os.getenv('PGDATABASE'),
    )


def strip_line_comments(sql):
    """Remove -- comments, respecting string literals."""
    out = []
    i = 0
    n = len(sql)
    while i < n:
        c = sql[i]
        if c in ("'", '"'):
            q = c
            out.append(c)
            i += 1
            while i < n:
                c2 = sql[i]
                out.append(c2)
                i += 1
                if c2 == q:
                    break
        elif c == '-' and i + 1 < n and sql[i + 1] == '-':
            while i < n and sql[i] != '\n':
                i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def split_top_level(body):
    """Split by commas at depth 0, respecting parens and quotes."""
    parts = []
    cur = []
    depth = 0
    in_str = False
    sq = None
    i = 0
    while i < len(body):
        c = body[i]
        if in_str:
            cur.append(c)
            if c == sq:
                in_str = False
        elif c in ("'", '"'):
            in_str = True
            sq = c
            cur.append(c)
        elif c == '(':
            depth += 1
            cur.append(c)
        elif c == ')':
            depth -= 1
            cur.append(c)
        elif c == ',' and depth == 0:
            parts.append(''.join(cur).strip())
            cur = []
            i += 1
            continue
        else:
            cur.append(c)
        i += 1
    rest = ''.join(cur).strip()
    if rest:
        parts.append(rest)
    return parts


def read_token(s, start):
    """
    Read one SQL 'token' starting at index start (after any leading whitespace).
    Returns (token_string, end_index_exclusive).
    Handles:  'quoted strings'  (expr)   bare_words
    """
    i = start
    while i < len(s) and s[i] in ' \t\n\r':
        i += 1
    if i >= len(s):
        return '', i
    c = s[i]
    if c in ("'", '"'):
        q = c
        j = i + 1
        while j < len(s):
            if s[j] == q:
                j += 1
                break
            j += 1
        return s[i:j], j
    if c == '(':
        depth = 0
        j = i
        while j < len(s):
            if s[j] == '(':
                depth += 1
            elif s[j] == ')':
                depth -= 1
                if depth == 0:
                    return s[i:j + 1], j + 1
            j += 1
        return s[i:], len(s)
    j = i
    while j < len(s) and s[j] not in (' ', '\t', '\n', '\r', ',', ')', ';'):
        j += 1
    return s[i:j], j


def extract_balanced_kw(s, keyword):
    """Extract 'keyword(balanced expression)' from s."""
    m = re.search(r'\b' + re.escape(keyword) + r'\s*\(', s, re.IGNORECASE)
    if not m:
        return None, None, None
    paren_start = m.end() - 1
    depth = 0
    in_str = False
    sq = None
    for i in range(paren_start, len(s)):
        c = s[i]
        if in_str:
            if c == sq:
                in_str = False
        elif c in ("'", '"'):
            in_str = True
            sq = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return s[m.start():i + 1], m.start(), i + 1
    return None, None, None


def convert_type(t):
    t = t.upper().strip()
    if re.match(r'^(INTEGER|INT|TINYINT|SMALLINT|MEDIUMINT|BIGINT|INT2|INT8)(\(\d+\))?$', t):
        return 'INTEGER'
    if re.match(r'^(REAL|FLOAT|DOUBLE|NUMERIC|DECIMAL|NUMBER)(\(.+\))?$', t):
        return 'DOUBLE PRECISION'
    if t in ('BLOB', 'BINARY', 'VARBINARY', 'NONE'):
        return 'BYTEA'
    if t in ('DATETIME',):
        return 'TIMESTAMP'
    if t == 'DATE':
        return 'DATE'
    if t == 'BOOLEAN':
        return 'BOOLEAN'
    return t or 'TEXT'


def pg_default(raw):
    """Convert a SQLite DEFAULT value to PostgreSQL equivalent."""
    d = raw.strip()
    if d.startswith('(') and d.endswith(')'):
        d = d[1:-1].strip()
    d_low = d.lower()
    if d_low in ("datetime('now')", "date('now')", "now()",
                 "strftime('%Y-%m-%d %H:%M:%S', 'now')"):
        return 'CURRENT_TIMESTAMP'
    if d_low in ('current_timestamp', 'current timestamp'):
        return 'CURRENT_TIMESTAMP'
    if d_low == 'current_date':
        return 'CURRENT_DATE'
    if d.startswith('"') and d.endswith('"'):
        inner = d[1:-1].replace("'", "''")
        return f"'{inner}'"
    return d


def parse_clause(clause):
    """
    Parse one column definition or table constraint.
    Returns (pg_sql_fragment, is_pk_from_constraint, autoincrement_col_name).
    """
    clause = clause.strip()
    if not clause:
        return None, False, None

    upper = re.sub(r'\s+', ' ', clause).upper().lstrip()

    if upper.startswith('PRIMARY KEY'):
        expr, _, _ = extract_balanced_kw(clause, 'PRIMARY KEY')
        if expr:
            inner = expr[len('PRIMARY KEY'):].strip().strip('()')
            cols = re.split(r'\s*,\s*', inner.strip())
            clean = []
            has_autoincrement = False
            for col in cols:
                c = col.strip().strip('"').split()[0]
                if 'AUTOINCREMENT' in col.upper():
                    has_autoincrement = True
                clean.append(c)
            if len(clean) == 1 and has_autoincrement:
                return None, True, clean[0]
            elif len(clean) == 1:
                return None, True, clean[0]
            else:
                col_list = ', '.join(f'"{c}"' for c in clean)
                return f'PRIMARY KEY ({col_list})', False, None
        return None, False, None

    if upper.startswith('FOREIGN KEY'):
        return None, False, None

    if upper.startswith('UNIQUE'):
        expr, _, _ = extract_balanced_kw(clause, 'UNIQUE')
        if expr:
            inner = expr[len('UNIQUE'):].strip().strip('()')
            return f'UNIQUE ({inner})', False, None
        return None, False, None

    if upper.startswith('CHECK'):
        expr, _, _ = extract_balanced_kw(clause, 'CHECK')
        if expr:
            return expr, False, None
        return None, False, None

    name_m = re.match(r'^["`\[]?(\w+)["`\]]?\s*(.*)', clause, re.DOTALL)
    if not name_m:
        return clause, False, None

    col_name = name_m.group(1)
    rest = name_m.group(2).strip()

    type_m = re.match(r'^(\w+(?:\s*\([^)]*\))?)\s*(.*)', rest, re.DOTALL)
    if not type_m:
        pg_type = 'TEXT'
        constraints_rest = rest
    else:
        pg_type = convert_type(type_m.group(1))
        constraints_rest = type_m.group(2).strip()

    autoincrement = bool(re.search(r'\bAUTOINCREMENT\b', constraints_rest, re.IGNORECASE))
    constraints_rest = re.sub(r'\bAUTOINCREMENT\b', '', constraints_rest, flags=re.IGNORECASE).strip()

    is_pk = bool(re.search(r'\bPRIMARY\s+KEY\b', constraints_rest, re.IGNORECASE))
    if is_pk:
        pg_type = 'SERIAL'
        constraints_rest = re.sub(r'\bPRIMARY\s+KEY\b', '', constraints_rest, flags=re.IGNORECASE).strip()

    not_null = ' NOT NULL' if re.search(r'\bNOT\s+NULL\b', constraints_rest, re.IGNORECASE) else ''
    unique = ' UNIQUE' if re.search(r'\bUNIQUE\b(?!\s*\()', constraints_rest, re.IGNORECASE) else ''

    default_clause = ''
    def_m = re.search(r'\bDEFAULT\b\s*', constraints_rest, re.IGNORECASE)
    if def_m:
        after_default = constraints_rest[def_m.end():]
        token, tok_end = read_token(after_default, 0)
        if token:
            default_clause = f' DEFAULT {pg_default(token)}'
            constraints_rest = constraints_rest[:def_m.start()] + after_default[tok_end:]

    check_expr, ck_start, ck_end = extract_balanced_kw(constraints_rest, 'CHECK')
    check_clause = f' {check_expr}' if check_expr else ''

    if is_pk:
        col_def = f'"{col_name}" {pg_type} PRIMARY KEY{not_null}{unique}{default_clause}{check_clause}'
    else:
        col_def = f'"{col_name}" {pg_type}{not_null}{unique}{default_clause}{check_clause}'

    return col_def, is_pk, col_name


def convert_create_table(table_name, sqlite_sql):
    sql = strip_line_comments(sqlite_sql).strip()
    outer_m = re.search(r'\((.+)\)\s*$', sql, re.DOTALL)
    if not outer_m:
        return None

    body = outer_m.group(1).strip()
    clauses = split_top_level(body)

    pg_parts = []
    pk_constraint_col = None

    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        pg_part, is_pk, col_name = parse_clause(clause)
        upper = re.sub(r'\s+', ' ', clause).upper().lstrip()
        if upper.startswith('PRIMARY KEY') and col_name:
            pk_constraint_col = col_name
            if pg_part:
                pg_parts.append(pg_part)
            continue
        if pg_part:
            pg_parts.append(pg_part)

    if pk_constraint_col:
        for i, part in enumerate(pg_parts):
            if re.match(rf'"{re.escape(pk_constraint_col)}"\s+INTEGER\b', part, re.IGNORECASE):
                pg_parts[i] = re.sub(r'\bINTEGER\b', 'SERIAL PRIMARY KEY', part, count=1, flags=re.IGNORECASE)
                break

    cols_str = ',\n    '.join(pg_parts)
    return f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    {cols_str}\n)'


def migrate_schema(sqlite_conn, pg_conn):
    sc = sqlite_conn.cursor()
    pc = pg_conn.cursor()

    sc.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY rowid")
    tables = sc.fetchall()

    print(f"Creating {len(tables)} tables...")
    ok = 0
    fail = 0

    for name, sql in tables:
        if not sql:
            continue
        pg_sql = convert_create_table(name, sql)
        if not pg_sql:
            print(f"  ! {name}: parse failed")
            fail += 1
            continue
        try:
            pc.execute(f'DROP TABLE IF EXISTS "{name}" CASCADE')
            pc.execute(pg_sql)
            ok += 1
            print(f"  + {name}")
        except Exception as e:
            pg_conn.rollback()
            print(f"  ERROR {name}: {e}")
            print(f"  SQL:\n{pg_sql[:400]}\n")
            fail += 1
            pc = pg_conn.cursor()

    pg_conn.commit()
    print(f"\nSchema: {ok} created, {fail} failed\n")


def migrate_data(sqlite_conn, pg_conn):
    sc = sqlite_conn.cursor()
    pc = pg_conn.cursor()

    sc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY rowid")
    tables = [r[0] for r in sc.fetchall()]

    print(f"Migrating data for {len(tables)} tables...")
    total = 0

    for table in tables:
        sc.execute(f'PRAGMA table_info("{table}")')
        col_info = sc.fetchall()
        col_names = [c[1] for c in col_info]
        col_types_map = {c[1]: c[2].upper() for c in col_info}

        sc.execute(f'SELECT * FROM "{table}"')
        rows = sc.fetchall()

        if not rows:
            print(f"  - {table}: 0 rows")
            continue

        cols_q = ', '.join(f'"{c}"' for c in col_names)
        phs = ', '.join(['%s'] * len(col_names))
        ins = f'INSERT INTO "{table}" ({cols_q}) VALUES ({phs}) ON CONFLICT DO NOTHING'

        converted = []
        for row in rows:
            cr = []
            for i, val in enumerate(row):
                cname = col_names[i]
                ctype = col_types_map.get(cname, '')
                if val is not None and ('BLOB' in ctype or 'BINARY' in ctype):
                    b = val if isinstance(val, (bytes, bytearray)) else bytes(val)
                    cr.append(psycopg2.Binary(b))
                else:
                    cr.append(val)
            converted.append(cr)

        try:
            psycopg2.extras.execute_batch(pc, ins, converted, page_size=500)
            pg_conn.commit()
            total += len(rows)
            print(f"  + {table}: {len(rows)} rows")
        except Exception as e:
            pg_conn.rollback()
            print(f"  ERROR {table}: {e}")
            pc = pg_conn.cursor()

    print(f"\nTotal rows migrated: {total}\n")


def fix_sequences(pg_conn):
    pc = pg_conn.cursor()
    pc.execute("""
        SELECT table_name, column_name FROM information_schema.columns
        WHERE column_default LIKE 'nextval%' AND table_schema = 'public'
        ORDER BY table_name
    """)
    seqs = pc.fetchall()
    print(f"Resetting {len(seqs)} sequences...")
    for table, col in seqs:
        try:
            pc.execute(f'SELECT MAX("{col}") FROM "{table}"')
            max_val = pc.fetchone()[0]
            if max_val and max_val > 0:
                pc.execute(f"SELECT setval(pg_get_serial_sequence('\"{table}\"', '{col}'), {max_val})")
                print(f"  + {table}.{col} -> {max_val}")
        except Exception as e:
            pg_conn.rollback()
            print(f"  ERROR {table}.{col}: {e}")
            pc = pg_conn.cursor()
    pg_conn.commit()
    print("Sequences done.\n")


def main():
    print("=== SQLite -> PostgreSQL Migration ===\n")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    pg_conn = get_pg_conn()
    pg_conn.autocommit = False

    migrate_schema(sqlite_conn, pg_conn)
    migrate_data(sqlite_conn, pg_conn)
    fix_sequences(pg_conn)

    sqlite_conn.close()
    pg_conn.close()
    print("=== Done! ===")


if __name__ == '__main__':
    main()
