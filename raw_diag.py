import psycopg2
import sys

def try_connect(dsn):
    print(f"Testing: {dsn}")
    try:
        conn = psycopg2.connect(dsn)
        print("Success!")
        conn.close()
    except Exception as e:
        # Capture the raw error from the exception if possible, 
        # or at least prevent the crash during print
        print(f"Error caught (type: {type(e).__name__})")
        try:
            # Using repr to avoid decoding issues during print
            print(f"Error details: {repr(e)}")
        except:
            print("Could not even print the error repr.")

print("--- Raw Error Diagnostic ---")
# Try 127.0.0.1
try_connect("dbname=hospyflow user=postgres password=admin host=127.0.0.1 port=5432")
# Try localhost
try_connect("dbname=hospyflow user=postgres password=admin host=localhost port=5432")
# Try default db
try_connect("dbname=postgres user=postgres password=admin host=127.0.0.1 port=5432")
