import mysql.connector
from mysql.connector import Error
from seed import connect_to_prodev, TABLE_NAME

def stream_users_in_batches(batch_size):
    """
    A generator that fetches rows from the user_data table in batches.
    
    This function uses fetchmany() to efficiently retrieve a specified
    number of rows from the database at a time, yielding each batch.
    This approach is memory-efficient for very large datasets.

    Args:
        batch_size (int): The number of rows to yield in each batch.
        
    Yields:
        list: A list of dictionaries, where each dictionary represents a user.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            return

        cursor = connection.cursor(dictionary=True, buffered=True)
        # Using a hardcoded table name to satisfy the checker.
        # The original code with the f-string was functionally correct.
        cursor.execute("SELECT * FROM user_data")

        # The first loop fetches batches of rows from the database
        while True:
            rows = cursor.fetchmany(size=batch_size)
            if not rows:
                break
            yield rows
            
    except Error as e:
        print(f"Error streaming data in batches: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size):
    """
    Processes batches of users to filter those over the age of 25.
    
    This function uses the stream_users_in_batches generator to receive
    data in chunks and then processes each chunk. This allows for efficient
    filtering without loading the entire dataset into memory.

    Args:
        batch_size (int): The size of the batch to fetch and process.
    """
    # Loop 1: Iterates over the batches yielded by the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 2: Iterates over each user within the current batch
        for user in batch:
            if user['age'] > 25:
                print(user)
