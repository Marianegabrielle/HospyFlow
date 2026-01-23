import os
import sys

print(f"Python version: {sys.version}")
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"File system encoding: {sys.getfilesystemencoding()}")
print(f"PATH: {os.environ.get('PATH')}")

import psycopg2
try:
    # Try with a very minimal connection string
    dsn = "dbname=hospyflow user=postgres password=admin host=127.0.0.1"
    print(f"Trying DSN: {dsn}")
    conn = psycopg2.connect(dsn)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Caught error: {e}")
    if isinstance(e, UnicodeDecodeError):
        print(f"Encoding: {e.encoding}")
        print(f"Reason: {e.reason}")
        print(f"Object: {e.object}")
        print(f"Start: {e.start}, End: {e.end}")
