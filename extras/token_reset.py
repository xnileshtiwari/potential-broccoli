import pymysql
from datetime import datetime
from Database.connection import getconnection

connection = getconnection()

def delete_row_by_date_and_tokens(date, input_token, output_token):
    connection = getconnection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    
    try:
        with connection.cursor() as cursor:
            # Query to delete the row
            query = """
            DELETE FROM token_usage
            WHERE Date = %s AND Input_token = %s AND Output_token = %s
            """
            cursor.execute(query, (date, input_token, output_token))
            connection.commit()
            print(f"Row with Date={date}, Input_token={input_token}, and Output_token={output_token} has been deleted.")
    except Exception as e:
        print(f"An error occurred while deleting the row: {str(e)}")
    finally:
        connection.close()

