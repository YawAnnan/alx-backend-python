#!/usr/bin/env python3
import sqlite3
import functools
from datetime import datetime   # required for timestamp logging

# setup database automatically
def setup_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Alice')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (2, 'Bob')")
    conn.commit()
    conn.close()

setup_db()  # run this before anything else


# decorator to log SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(query, *args, **kwargs):
        # log query with timestamp
        print(f"[{datetime.now()}] Executing query: {query}")
        return func(query, *args, **kwargs)
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# fetch users while logging the query
if __name__ == "__main__":
    users = fetch_all_users("SELECT * FROM users")
    print(users)
