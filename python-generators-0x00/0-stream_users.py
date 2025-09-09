import mysql.connector
from mysql.connector import Error
from seed import connect_to_prodev, TABLE_NAME

def stream_users():
    """
    A generator that streams rows from the user_data table one by one.
    
    This function connects to the 'ALX_prodev' database, fetches all
    users, and yields each row as a dictionary. It ensures the database
    connection is properly closed after the operation.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            # If connection fails, stop the generator.
            return

        # Use buffered=True to ensure all results are fetched at once, which
        # is necessary for multiple queries in a session.
        # Use dictionary=True to return rows as dictionaries.
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")

        # The single loop iterates over the cursor and yields each row.
        for row in cursor:
            yield row
            
    except Error as e:
        print(f"Error streaming data: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    # This block is for demonstrating the generator locally
    user_generator = stream_users()
    for user in user_generator:
        print(user)
