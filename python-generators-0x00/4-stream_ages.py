"""
Module to compute memory-efficient average age using generators.
"""
seed = __import__('seed')

def stream_user_ages():
    """
    Generator that yields user ages one by one from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")
    
    # Loop 1: Iterating through the cursor to yield ages one by one
    for row in cursor:
        yield row['age']
    
    cursor.close()
    connection.close()

def calculate_average_age():
    """
    Calculates the average age using the stream_user_ages generator.
    """
    total_age = 0
    count = 0
    
    # Loop 2: Consuming the generator
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count == 0:
        return 0
    
    average_age = total_age / count
    print(f"Average age of users: {average_age}")

if __name__ == "__main__":
    calculate_average_age()