#!/usr/bin/env python3
import time
import sqlite3
import functools


def with_db_connection(func):
    """Decorator that opens a sqlite3 connection, passes it to the function, and closes afterward"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper


def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory for retrying database operations.
    - retries: number of attempts before failing
    - delay: seconds to wait between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < retries:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print("All retries failed.")
                        raise
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # attempt to fetch users with automatic retry on failure
    users = fetch_users_with_retry()
    print(users)
    print("Users fetched successfully.")