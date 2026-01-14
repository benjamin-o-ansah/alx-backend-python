import mysql.connector


def stream_users():
    """
    Generator that fetches rows one by one from the user_data table.
    """
    connection = None
    try:
        # Establish connection to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password",
            database="alx_backend_python"
        )
        
        # Use a dictionary cursor to get rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        # The single allowed loop to yield rows
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        # Ensure resources are closed after the generator is exhausted or closed
        if connection and connection.is_connected():
            cursor.close()
            connection.close()