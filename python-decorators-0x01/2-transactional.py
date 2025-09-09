#!/usr/bin/env python3
import sqlite3
import functools


def with_db_connection(func):
    """Decorator that opens a sqlite3 connection, passes it to the function, and closes afterward"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper


def transactional(func):
    """Decorator to manage transactions (commit on success, rollback on error)"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction failed, rolled back. Error: {e}")
            raise
    return wrapper


def ensure_email_column(conn):
    """Add email column if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "email" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    ensure_email_column(conn)  # ensure column exists before updating
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")
    print("Email updated successfully.")
