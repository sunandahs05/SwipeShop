from db import get_db_connection

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Add image_url column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN image_url VARCHAR(255);")
        print("Added image_url column to products table.")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("image_url column already exists.")
        else:
            print("Error altering table:", e)

    # 2. Get or create a seller
    cursor.execute("SELECT user_id FROM users WHERE role = 'seller' LIMIT 1;")
    seller = cursor.fetchone()
    if not seller:
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Sample Seller', 'seller@swipeshop.com', 'hashed_pw', 'seller');")
        seller_id = cursor.lastrowid
        print(f"Created sample seller with ID: {seller_id}")
    else:
        seller_id = seller['user_id']
        print(f"Using existing seller ID: {seller_id}")

    # 3. Get or create a category
    try:
        cursor.execute("SELECT category_id FROM categories LIMIT 1;")
        category = cursor.fetchone()
        if not category:
            cursor.execute("INSERT INTO categories (name) VALUES ('Electronics'), ('Apparel');")
            category_id = cursor.lastrowid
            print(f"Created sample categories. Using ID: {category_id}")
        else:
            category_id = category['category_id']
            print(f"Using existing category ID: {category_id}")
    except Exception as e:
        print("Error with categories table (maybe it doesn't exist):", e)
        # It's possible categories table has a different structure or doesn't exist? The schema said category_id is int.
        # If it failed, let's create a table
        if "categories' doesn't exist" in str(e):
            cursor.execute("CREATE TABLE categories (category_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100));")
            cursor.execute("INSERT INTO categories (name) VALUES ('Tech'), ('Fashion');")
            category_id = cursor.lastrowid
        else:
            category_id = 1

    # 4. Insert Products
    sample_products = [
        (seller_id, category_id, 'Wireless Noise Cancelling Headphones', 'Premium over-ear headphones with 30-hour battery life.', 199.99, 50, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=60'),
        (seller_id, category_id, 'Smart Fitness Watch', 'Track your steps, heart rate, and sleep with this sleek smartwatch.', 149.50, 120, 'https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?w=600&auto=format&fit=crop&q=60'),
        (seller_id, category_id, 'Mechanical Gaming Keyboard', 'RGB backlighting, tactile switches, and aluminum frame.', 89.99, 30, 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&auto=format&fit=crop&q=60'),
        (seller_id, category_id, 'Minimalist Leather Backpack', 'Durable, stylish, and perfect for everyday carry or travel.', 125.00, 15, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=60'),
        (seller_id, category_id, 'Portable Bluetooth Speaker', 'Waterproof design with 360-degree sound and deep bass.', 59.90, 85, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format&fit=crop&q=60')
    ]

    insert_query = """
        INSERT INTO products (seller_id, category_id, name, description, price, stock, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for p in sample_products:
        cursor.execute(insert_query, p)
    
    conn.commit()
    print("Inserted 5 sample products with images!")

if __name__ == "__main__":
    seed_database()
