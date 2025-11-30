#!/usr/bin/env python3
"""
Safe admin/user management script for the project.

Usage examples:
  python create_admin.py --username admin --password secret
  python create_admin.py --username admin --update --password newpass
  python create_admin.py --username admin --delete
  python create_admin.py --show

This script does NOT import `app` to avoid starting the Flask server.
It locates the SQLite DB next to this script: `database.db`.
"""
import os
import sqlite3
import hashlib
import argparse
import getpass


def db_path():
    return os.path.join(os.path.dirname(__file__), "database.db")


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def show_users(conn):
    cur = conn.execute("SELECT id,username FROM users")
    rows = cur.fetchall()
    if not rows:
        print("No users found")
        return
    for r in rows:
        print(f"{r[0]}:\t{r[1]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--username", "-u", help="Username to create/update/delete")
    p.add_argument("--password", "-p", help="Password (if omitted you'll be prompted)")
    p.add_argument("--update", action="store_true", help="Update password if user exists")
    p.add_argument("--delete", action="store_true", help="Delete the specified user")
    p.add_argument("--show", action="store_true", help="Show existing users")
    args = p.parse_args()

    DB = db_path()
    if not os.path.exists(DB):
        print(f"Database not found at {DB}. Run the app once to initialize the DB or run init_db().")
        return

    conn = sqlite3.connect(DB)
    try:
        if args.show:
            show_users(conn)
            return

        if not args.username:
            print("Please provide --username or use --show")
            return

        username = args.username

        if args.delete:
            cur = conn.execute("SELECT id FROM users WHERE username=?", (username,))
            if not cur.fetchone():
                print("User not found")
                return
            conn.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            print(f"Deleted user '{username}'")
            return

        password = args.password
        if not password:
            password = getpass.getpass(prompt="Password: ")

        pw_hash = sha256(password)

        cur = conn.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row:
            if args.update:
                conn.execute("UPDATE users SET password=? WHERE username=?", (pw_hash, username))
                conn.commit()
                print(f"Updated password for '{username}'")
            else:
                print(f"User '{username}' already exists. Use --update to change the password or --delete to remove the user.")
        else:
            conn.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, pw_hash))
            conn.commit()
            print(f"Created user '{username}'")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
