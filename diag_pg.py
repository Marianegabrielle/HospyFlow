import psycopg2
import os

print("--- Diagnostic PostgreSQL Connection ---")
try:
    # Attempting connection with explicit parameters
    conn = psycopg2.connect(
        dbname="hospyflow",
        user="postgres",
        password="admin",
        host="localhost", # Changed from 127.0.0.1 to see if it makes a difference
        port="5432"
    )
    print("SUCCESS: Connection established to 'hospyflow' database.")
    conn.close()
except psycopg2.OperationalError as e:
    print(f"OperationalError: {e}")
    print("\nAttempting connection to default 'postgres' database...")
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        print("SUCCESS: Connection established to default 'postgres' database.")
        conn.close()
    except Exception as e2:
        print(f"FAILED again: {e2}")
except Exception as e:
    print(f"Unexpected error: {type(e).__name__}: {e}")
