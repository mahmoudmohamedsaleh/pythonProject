import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# 1. Replace main sqlite3 import with db_postgres adapter
content = content.replace(
    'import sqlite3\n',
    'import db_postgres as sqlite3\n',
    1
)

# 2. Replace local sqlite3 imports inside functions
content = content.replace(
    "import sqlite3 as _msql, requests as _mreq, re as _re",
    "import db_postgres as _msql; import requests as _mreq; import re as _re"
)
content = content.replace(
    "import sqlite3 as _sql, requests as _mreq",
    "import db_postgres as _sql; import requests as _mreq"
)
content = re.sub(
    r'^(\s*)import sqlite3\s*$',
    r'\1import db_postgres as sqlite3',
    content,
    flags=re.MULTILINE
)
content = re.sub(
    r'^(\s*)import sqlite3, json\s*$',
    r'\1import db_postgres as sqlite3\n\1import json',
    content,
    flags=re.MULTILINE
)

# 3. Replace all sqlite3.connect('ProjectStatus.db') with sqlite3.connect()
target = "sqlite3.connect('ProjectStatus.db')"
replacement = "sqlite3.connect()"
count = content.count(target)
content = content.replace(target, replacement)

print(f"Original size: {original_len}, New size: {len(content)}")
print(f"Replaced {count} sqlite3.connect() calls")
remaining = content.count(target)
print(f"Remaining connect calls: {remaining}")
pg_imports = content.count('import db_postgres')
print(f"db_postgres imports: {pg_imports}")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.py updated successfully")
