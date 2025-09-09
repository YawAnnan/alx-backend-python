import mysql.connector
from mysql.connector import Error
from seed import connect_to_prodev, TABLE_NAME

def paginate_users(page_size, offset):
    """
    Fetches a single page of users from the database.
    
    Args:
        page_size (int): The number of users to fetch per page.
        offset (int): The starting position for the query.
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a user.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        return rows
        
    except Error as e:
        print(f"Error fetching page: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def lazy_paginate(page_size):
    """
    A generator that fetches and yields pages of users lazily.
    
    This function uses a single loop to manage the offset and calls
    paginate_users to get the next page only when the generator is iterated over.

    Args:
        page_size (int): The number of users to fetch per page.
        
    Yields:
        list: A list of dictionaries, representing a page of users.
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            # Stop iteration when an empty page is returned
            break
        yield page
        offset += page_size

def stream_user_ages():
    """
    A generator that yields user ages one by one from the database.
    
    This function is memory-efficient as it does not load all ages
    into memory at once.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            return
        
        cursor = connection.cursor(buffered=True)
        cursor.execute(f"SELECT age FROM {TABLE_NAME}")
        
        for row in cursor:
            yield row[0]
            
    except Error as e:
        print(f"Error streaming ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def calculate_average_age():
    """
    Calculates the average age of users without loading all data into memory.
    
    This function uses the stream_user_ages generator to get ages one by one.
    """
    total_age = 0
    user_count = 0
    
    # Loop 1: Iterates through the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1
        
    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age}")
    else:
        print("No users found to calculate the average age.")

if __name__ == "__main__":
    # Example usage from 3-main.py
    try:
        for page in lazy_paginate(100):
            for user in page:
                pass # print(user)
        
        # New call to demonstrate the average age calculation
        calculate_average_age()
        
    except BrokenPipeError:
        pass
