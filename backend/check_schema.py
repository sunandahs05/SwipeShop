from db import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DESCRIBE products;")
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print("Error:", e)
