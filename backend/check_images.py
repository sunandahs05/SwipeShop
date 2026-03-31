from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT product_id, name, image_url FROM products LIMIT 5')

print("\n📸 Product Images in Database:\n")
for row in cursor.fetchall():
    img = row['image_url'] if row['image_url'] else "NO IMAGE"
    print(f"  {row['product_id']:2d}. {row['name']:25s} → {img}")

print("\n")
