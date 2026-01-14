#!/usr/bin/python3
"""
Lazy pagination module to fetch database users in pages.
"""
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a specific page of users from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily loads pages of users.
    Uses exactly one loop to manage the offset and yielding of data.
    """
    offset = 0
    
    # The single permitted loop
    while True:
        page = paginate_users(page_size, offset)
        
        # If the page is empty, we have reached the end of the database
        if not page:
            break
            
        yield page
        
        # Increment offset to fetch the next page in the next iteration
        offset += page_size