#!/usr/bin/env python
"""
SwipeShop Database Setup Fixer
Properly sets up the database with all required components
"""

import mysql.connector
from config import DB_CONFIG

def execute_sql(sql_text, conn):
    """Execute SQL statements"""
    cursor = conn.cursor()
    statements = sql_text.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
                conn.commit()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
                conn.rollback()
    
    cursor.close()

def setup_database():
    """Complete database setup"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    print("\n🔧 Setting up SwipeShop database...\n")
    
    # 1. Add image_url column if missing
    print("1️⃣  Adding image_url column...")
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)")
        conn.commit()
        print("   ✅ Column added")
    except:
        print("   ℹ️  Column already exists")
    
    # 2. Get or create sellers
    print("\n2️⃣  Setting up sellers...")
    cursor.execute("""
        SELECT user_id FROM users 
        WHERE role = 'seller' 
        LIMIT 1
    """)
    seller = cursor.fetchone()
    
    if not seller:
        print("   Creating sellers...")
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, is_active) 
            VALUES 
            ('Tech Seller', 'seller1@swipeshop.local', 'hash1', 'seller', TRUE),
            ('Fashion Seller', 'seller2@swipeshop.local', 'hash2', 'seller', TRUE),
            ('Home Seller', 'seller3@swipeshop.local', 'hash3', 'seller', TRUE)
        """)
        conn.commit()
        print("   ✅ Sellers created")
    else:
        print(f"   ✅ Sellers exist (ID: {seller['user_id']})")
    
    # Get seller IDs
    cursor.execute("SELECT user_id FROM users WHERE role = 'seller' LIMIT 3")
    sellers = cursor.fetchall()
    seller_ids = [s['user_id'] for s in sellers]
    
    # Get category IDs
    cursor.execute("SELECT category_id FROM categories LIMIT 5")
    categories = cursor.fetchall()
    if len(categories) < 5:
        print("\n   Creating categories...")
        cursor.execute("""
            INSERT INTO categories (name, parent_id, is_active) VALUES 
            ('Electronics', NULL, TRUE),
            ('Clothing', NULL, TRUE),
            ('Home', NULL, TRUE),
            ('Books', NULL, TRUE),
            ('Sports', NULL, TRUE)
        """)
        conn.commit()
        cursor.execute("SELECT category_id FROM categories LIMIT 5")
        categories = cursor.fetchall()
    
    category_ids = [c['category_id'] for c in categories]
    
    # 3. Clear existing products
    print("\n3️⃣  Loading sample products...")
    cursor.execute("DELETE FROM products")
    conn.commit()
    
    # 4. Insert products with proper seller_id and image_url
    products_sql = f"""
    INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active) VALUES
    ({seller_ids[0]}, {category_ids[0]}, 'Wireless Headphones', 'Premium quality wireless', 79.99, 25, 4.5, 'https://i.dummyjson.com/data/products/3/1.jpg', TRUE),
    ({seller_ids[0]}, {category_ids[0]}, 'Smart Watch', 'Advanced fitness tracking', 199.99, 15, 4.3, 'https://i.dummyjson.com/data/products/32/1.jpg', TRUE),
    ({seller_ids[0]}, {category_ids[0]}, 'USB-C Cable', 'Fast charging cable', 12.99, 100, 4.2, 'https://i.dummyjson.com/data/products/23/1.jpg', TRUE),
    ({seller_ids[1]}, {category_ids[1]}, 'Cotton T-Shirt', 'Comfortable cotton tee', 19.99, 80, 4.1, 'https://i.dummyjson.com/data/products/1/1.jpg', TRUE),
    ({seller_ids[1]}, {category_ids[1]}, 'Denim Jeans', 'Classic style denim', 59.99, 40, 4.3, 'https://i.dummyjson.com/data/products/4/1.jpg', TRUE),
    ({seller_ids[1]}, {category_ids[1]}, 'Running Shoes', 'Professional running', 99.99, 35, 4.7, 'https://i.dummyjson.com/data/products/6/1.jpg', TRUE),
    ({seller_ids[2]}, {category_ids[2]}, 'LED Desk Lamp', 'Adjustable LED lamp', 39.99, 45, 4.4, 'https://i.dummyjson.com/data/products/8/1.jpg', TRUE),
    ({seller_ids[2]}, {category_ids[2]}, 'Plant Pot', 'Ceramic plant pot', 14.99, 75, 4.1, 'https://i.dummyjson.com/data/products/11/1.jpg', TRUE),
    ({seller_ids[0]}, {category_ids[3]}, 'JavaScript Guide', 'Modern JS programming', 34.99, 20, 4.6, 'https://i.dummyjson.com/data/products/2/1.jpg', TRUE),
    ({seller_ids[2]}, {category_ids[4]}, 'Yoga Mat', 'Professional yoga mat', 24.99, 50, 4.2, 'https://i.dummyjson.com/data/products/5/1.jpg', TRUE);
    """
    
    execute_sql(products_sql, conn)
    cursor.execute("SELECT COUNT(*) as cnt FROM products")
    product_count = cursor.fetchone()['cnt']
    print(f"   ✅ Loaded {product_count} products")
    
    # 5. Create/Recreate stored procedures
    print("\n4️⃣  Setting up stored procedures...")
    
    procedures_sql = """
    DROP PROCEDURE IF EXISTS get_personalized_feed;
    DROP PROCEDURE IF EXISTS get_liked_products;
    """
    execute_sql(procedures_sql, conn)
    
    # Recreate procedures
    sql_file = "../database/procedures.sql"
    try:
        with open(sql_file, 'r') as f:
            proc_content = f.read()
        
        # Execute procedures
        cursor = conn.cursor()
        # Handle DELIMITER statements
        statements = proc_content.split('DELIMITER $$')
        
        for i, stmt in enumerate(statements):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                # Clean up the statement
                stmt = stmt.replace('DELIMITER ;', '').strip()
                if 'CREATE PROCEDURE' in stmt or 'CREATE FUNCTION' in stmt:
                    try:
                        cursor.execute(stmt)
                        conn.commit()
                    except mysql.connector.Error as e:
                        if 'already exists' not in str(e):
                            print(f"   ℹ️  Note: {e}")
        
        print("   ✅ Procedures created")
    except Exception as e:
        print(f"   ⚠️  Procedures may need manual setup: {e}")
    
    # 6. Add sample likes for test user
    print("\n5️⃣  Adding sample likes...")
    
    # Get a buyer user
    cursor.execute("SELECT user_id FROM users WHERE role = 'buyer' LIMIT 1")
    buyer = cursor.fetchone()
    
    if buyer:
        buyer_id = buyer['user_id']
        
        # Clear existing likes
        cursor.execute("DELETE FROM swipes WHERE user_id = %s", (buyer_id,))
        conn.commit()
        
        # Get first 3 products
        cursor.execute("SELECT product_id FROM products LIMIT 3")
        products = cursor.fetchall()
        
        # Add likes
        for product in products:
            cursor.execute("""
                INSERT INTO swipes (user_id, product_id, liked) 
                VALUES (%s, %s, 1)
            """, (buyer_id, product['product_id']))
        conn.commit()
        
        print(f"   ✅ Added {len(products)} sample likes for test user")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ Database setup complete!")
    print("="*50)
    print("\n🔑 Test Credentials:")
    print("   Email: test@gmail.com (or any existing buyer)")
    print("   Password: (from your sample user setup)")
    print("\n🚀 Try this:")
    print("   1. Refresh the page or restart Flask")
    print("   2. Login")
    print("   3. Go to /feed")
    print("\n")

if __name__ == "__main__":
    setup_database()
