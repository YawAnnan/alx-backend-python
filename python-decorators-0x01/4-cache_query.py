#!/usr/bin/env python3
import sqlite3
import functools

# simple in-memory cache
query_cache = {}


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


def cache_query(func):
    """Decorator that caches query results based on the SQL query string"""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print(f"Cache hit for query: {query}")
            return query_cache[query]
        else:
            print(f"Cache miss for query: {query}")
            result = func(conn, query, *args, **kwargs)
            query_cache[query] = result
            return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call → query runs, result cached
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)

    # Second call → result comes from cache, no DB call
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
