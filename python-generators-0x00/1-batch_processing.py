import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator that fetches users from the database in chunks.
    Uses 1 loop to iterate through the fetched results.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='alx_low_level_programming'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        # Loop 1: Fetching batches from the cursor
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            yield rows
            
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    return

def batch_processing(batch_size):
    """
    Processes each batch and filters users older than 25.
    Uses 2 loops (one for the generator, one for the batch list).
    """
    # Loop 2: Iterating over the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Iterating over the list of users in the current batch
        filtered_users = [user for user in batch if user['age'] > 25]
        
        for user in filtered_users:
            print(user)