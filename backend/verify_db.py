#!/usr/bin/env python
"""
Quick setup verification and fix script for SwipeShop database
"""

import mysql.connector
from config import DB_CONFIG
import os
import sys

def run_sql_file(filepath, conn):
    """Run SQL file and return results"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        sql_content = f.read()
    
    cursor = conn.cursor()
    
    # Split by delimiter and execute each statement
    statements = sql_content.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement:
            if 'DELIMITER' in statement:
                continue
            try:
                cursor.execute(statement)
                conn.commit()
            except Exception as e:
                print(f"⚠️  Warning: {e}")
                conn.rollback()
    
    cursor.close()
    return True

def verify_database():
    """Verify database setup"""
    print("🔍 Verifying SwipeShop Database Setup...\n")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Check products table
        print("1️⃣  Checking products table...")
        cursor.execute("DESCRIBE products")
        columns = cursor.fetchall()
        col_names = [col['Field'] for col in columns]
        
        if 'image_url' in col_names:
            print("   ✅ image_url column exists")
        else:
            print("   ❌ image_url column missing - adding...")
            cursor.execute("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)")
            conn.commit()
            print("   ✅ image_url column added")
        
        # Check products data
        print("\n2️⃣  Checking product data...")
        cursor.execute("SELECT COUNT(*) as cnt FROM products")
        result = cursor.fetchone()
        product_count = result['cnt']
        print(f"   Products in database: {product_count}")
        
        if product_count == 0:
            print("   ❌ No products found - loading sample data...")
            run_sql_file("../database/sample_data.sql", conn)
            cursor.execute("SELECT COUNT(*) as cnt FROM products")
            result = cursor.fetchone()
            print(f"   ✅ Loaded {result['cnt']} products")
        else:
            print(f"   ✅ Found {product_count} products")
        
        # Check stored procedures
        print("\n3️⃣  Checking stored procedures...")
        cursor.execute("""
            SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES 
            WHERE ROUTINE_SCHEMA = 'swipeshop' AND ROUTINE_NAME = 'get_liked_products'
        """)
        if cursor.fetchone():
            print("   ✅ get_liked_products procedure exists")
        else:
            print("   ❌ get_liked_products procedure missing")
        
        # Check if user has likes
        print("\n4️⃣  Checking sample user data...")
        cursor.execute("""
            SELECT u.user_id, u.email, COUNT(s.swipe_id) as likes
            FROM users u
            LEFT JOIN swipes s ON u.user_id = s.user_id AND s.liked = 1
            WHERE u.role = 'buyer'
            GROUP BY u.user_id
            LIMIT 3
        """)
        users = cursor.fetchall()
        
        if users:
            print(f"   ✅ Found {len(users)} buyer accounts:")
            for u in users:
                print(f"      - {u['email']}: {u['likes']} likes")
        else:
            print("   ❌ No buyer accounts found")
        
        # Test API query
        print("\n5️⃣  Testing get_personalized_feed procedure...")
        if users and users[0]['user_id']:
            try:
                cursor.callproc('get_personalized_feed', (users[0]['user_id'], 5))
                results = []
                for result in cursor.stored_results():
                    results = result.fetchall()
                print(f"   ✅ Procedure returned {len(results)} products")
            except Exception as e:
                print(f"   ❌ Procedure error: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ Database setup verification complete!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_database()
