import time
import sqlite3
import functools


query_cache = {}

# ---------------------------
# with_db_connection decorator
# (copied from previous task)
# ---------------------------
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper


# ---------------------------
# cache_query decorator
# ---------------------------
def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # extract query (always passed as keyword or positionally)
        query = kwargs.get("query") or args[1]

        # check if cached
        if query in query_cache:
            print("Using cached result for query:", query)
            return query_cache[query]

        # not cached → run function
        result = func(*args, **kwargs)

        # store in cache
        query_cache[query] = result
        print("Caching result for query:", query)

        return result
    return wrapper



@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ---------------------------
# Test the caching behavior
# ---------------------------

# First call → executes SQL and caches result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call → loads from cache
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)
