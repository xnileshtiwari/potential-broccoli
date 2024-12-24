from datetime import datetime
from Database.connection import getconnection

# Function to increment a column for today's date
def increment_column_for_today(column_name):
    connection = getconnection()
    if connection is None:
        print("Failed to connect to the database.")
        return

    try:
        # First, check if the column exists
        cursor = connection.cursor()
        check_column_query = """
        SELECT COUNT(*) as count
        FROM information_schema.columns 
        WHERE table_schema = 'defaultdb'
        AND table_name = 'cat_is_trending'
        AND column_name = %s
        """
        cursor.execute(check_column_query, (column_name,))
        result = cursor.fetchone()
        
        # If column doesn't exist, create it
        if result['count'] == 0:
            print(f"Column {column_name} doesn't exist. Creating it...")
            alter_query = f"""
            ALTER TABLE cat_is_trending 
            ADD COLUMN {column_name} INT NOT NULL DEFAULT 0
            """
            cursor.execute(alter_query)
            connection.commit()

        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # Check if today's row exists
        check_query = "SELECT * FROM cat_is_trending WHERE date = %s"
        cursor.execute(check_query, (today_date,))
        result = cursor.fetchone()

        if result:
            # If row exists, increment the column value
            update_query = f"UPDATE cat_is_trending SET {column_name} = {column_name} + 1 WHERE date = %s"
            cursor.execute(update_query, (today_date,))
        else:
            # Get all column names except 'date'
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'defaultdb' 
                AND TABLE_NAME = 'cat_is_trending' 
                AND COLUMN_NAME != 'date'
                ORDER BY ORDINAL_POSITION
            """)
            columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
            
            # Create placeholders for values (0 for all columns except the target column)
            values = [1 if col == column_name else 0 for col in columns]
            
            # Build the INSERT query dynamically
            insert_query = f"""
            INSERT INTO cat_is_trending (date, {', '.join(columns)})
            VALUES (%s, {', '.join(['%s'] * len(columns))})
            """
            cursor.execute(insert_query, (today_date, *values))

        connection.commit()
        print(f"Successfully updated column '{column_name}' for date {today_date}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        connection.rollback()
    finally:
        connection.close()


