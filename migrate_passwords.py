#!/usr/bin/env python3
"""
Password Migration Script
Converts all plaintext passwords in the database to encrypted hashes.
Run this ONCE before deploying to PythonAnywhere.
"""

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def migrate_passwords():
    """Migrate all plaintext passwords to hashed format."""
    conn = sqlite3.connect('ProjectStatus.db')
    c = conn.cursor()
    
    print("=" * 60)
    print("PASSWORD MIGRATION SCRIPT")
    print("=" * 60)
    print()
    
    # Migrate users table
    print("Migrating 'users' table...")
    c.execute("SELECT id, username, password FROM users")
    users = c.fetchall()
    
    users_migrated = 0
    users_already_hashed = 0
    
    for user_id, username, password in users:
        # Check if password is already hashed (starts with algorithm identifier)
        if password and (password.startswith('scrypt:') or password.startswith('pbkdf2:') or password.startswith('bcrypt:')):
            print(f"  ✓ {username}: Already encrypted (skipping)")
            users_already_hashed += 1
        else:
            # Encrypt the plaintext password
            hashed_password = generate_password_hash(password)
            c.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))
            print(f"  ✓ {username}: Password encrypted (was: {password[:3]}***)")
            users_migrated += 1
    
    print()
    print(f"Users table: {users_migrated} migrated, {users_already_hashed} already encrypted")
    print()
    
    # Migrate engineers table
    print("Migrating 'engineers' table...")
    c.execute("SELECT id, username, password FROM engineers")
    engineers = c.fetchall()
    
    engineers_migrated = 0
    engineers_already_hashed = 0
    
    for engineer_id, username, password in engineers:
        # Check if password is already hashed
        if password and (password.startswith('scrypt:') or password.startswith('pbkdf2:') or password.startswith('bcrypt:')):
            print(f"  ✓ {username}: Already encrypted (skipping)")
            engineers_already_hashed += 1
        else:
            # Encrypt the plaintext password
            hashed_password = generate_password_hash(password)
            c.execute("UPDATE engineers SET password=? WHERE id=?", (hashed_password, engineer_id))
            print(f"  ✓ {username}: Password encrypted (was: {password[:3]}***)")
            engineers_migrated += 1
    
    print()
    print(f"Engineers table: {engineers_migrated} migrated, {engineers_already_hashed} already encrypted")
    print()
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)
    print(f"Total passwords encrypted: {users_migrated + engineers_migrated}")
    print(f"Total already encrypted: {users_already_hashed + engineers_already_hashed}")
    print()
    print("✅ Your database is now ready for deployment!")
    print("✅ Users can now log in with their original passwords.")
    print()

if __name__ == '__main__':
    try:
        migrate_passwords()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
