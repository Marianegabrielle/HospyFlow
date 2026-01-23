import psycopg2
import sys

def diag():
    print("--- Diagnostic Connection V16 ---")
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="admin",
            host="127.0.0.1",
            port="5432"
        )
        print("Success connect to postgres db on 5432!")
        conn.close()
    except Exception as e:
        print(f"Error 5432: {repr(e)}")

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="admin",
            host="127.0.0.1",
            port="5433"
        )
        print("Success connect to postgres db on 5433!")
        conn.close()
    except Exception as e:
        print(f"Error 5433: {repr(e)}")

diag()
