#!/usr/bin/env bash
# ============================================================
# EJTech CRM — Export Replit PostgreSQL for Cloud SQL import
#
# Run this script INSIDE the Replit shell while your app is
# still connected to the Replit database.
#
# Usage:
#   bash db_export.sh
#
# Output:
#   ejtech_crm.dump   — custom-format PostgreSQL dump
#   ejtech_crm.sql    — plain-SQL dump (easier to inspect/edit)
# ============================================================

set -e

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set."
    echo "Make sure you run this script inside the Replit shell."
    exit 1
fi

echo "==> Exporting Replit PostgreSQL database..."
echo "    Source: $DATABASE_URL"
echo ""

# Custom-format dump (recommended — smaller, supports parallel restore)
echo "[1/2] Creating custom-format dump (ejtech_crm.dump)..."
pg_dump \
    --no-owner \
    --no-acl \
    --no-privileges \
    --exclude-table-data='django_*' \
    -Fc \
    "$DATABASE_URL" \
    -f ejtech_crm.dump

echo "      Done. Size: $(du -sh ejtech_crm.dump | cut -f1)"

# Plain-SQL dump (easier to inspect or selectively restore)
echo "[2/2] Creating plain-SQL dump (ejtech_crm.sql)..."
pg_dump \
    --no-owner \
    --no-acl \
    --no-privileges \
    -Fp \
    "$DATABASE_URL" \
    -f ejtech_crm.sql

echo "      Done. Size: $(du -sh ejtech_crm.sql | cut -f1)"

echo ""
echo "==> Export complete!"
echo ""
echo "Next steps:"
echo "  1. Download ejtech_crm.dump from Replit (use the Files panel or 'cat | base64')"
echo "  2. On your local machine, restore to Cloud SQL:"
echo ""
echo "     pg_restore --no-owner --no-acl -h <CLOUD_SQL_PUBLIC_IP> \\"
echo "                -U ejtech -d ejtech ejtech_crm.dump"
echo ""
echo "  3. Then run the custom functions:"
echo ""
echo "     psql -h <CLOUD_SQL_PUBLIC_IP> -U ejtech -d ejtech -f cloud_sql_functions.sql"
echo ""
