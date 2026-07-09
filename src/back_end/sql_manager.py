import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

destructive_query_keywords = ['DELETE', 'DROP']

def get_connection():
    try:
        connection = psycopg2.connect(
            host="ep-ancient-meadow-atqyb536-pooler.c-9.us-east-1.aws.neon.tech",
            database="utdacademicdb",
            user="neondb_owner",
            password=os.getenv("POSTGRES_PASSWORD"),
            sslmode="require"
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_query_results(query):
    try:
        for keyword in destructive_query_keywords:
            if keyword in query.lower():
                print("Attempted to execute destructive query!")
                return 'Failed'
        connection = get_connection()
        if connection is None:
            return "Failed"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return "Failed"