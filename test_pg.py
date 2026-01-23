import psycopg2
try:
    conn = psycopg2.connect(
        dbname="hospyflow",
        user="postgres",
        password="admin",
        host="127.0.0.1",
        port="5432"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
