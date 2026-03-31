#!/usr/bin/env python
"""
Create stored procedures for SwipeShop with smart recommendations
"""

import mysql.connector
from config import DB_CONFIG

def create_procedures():
    """Create required stored procedures"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("\n📋 Creating smart recommendation procedures...\n")
    
    # 0. Update preference scores when user likes a product
    print("0. Creating update_preference_scores procedure...")
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS update_preference_scores")
        conn.commit()
    except:
        pass
    
    sql0 = """
    CREATE PROCEDURE update_preference_scores(
        IN p_user_id INT,
        IN p_category_id INT
    )
    BEGIN
        INSERT INTO preference_scores(user_id, category_id, score)
        VALUES(p_user_id, p_category_id, 1.0)
        ON DUPLICATE KEY UPDATE score = score + 1.0;
    END
    """
    
    try:
        cursor.execute(sql0)
        conn.commit()
        print("   ✅ update_preference_scores created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
    
    # 1. Enhanced get_personalized_feed with interest-based recommendations
    print("1. Creating get_personalized_feed (interest-based)...")
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS get_personalized_feed")
        conn.commit()
    except:
        pass
    
    sql1 = """
    CREATE PROCEDURE get_personalized_feed(
        IN p_user_id INT,
        IN p_limit INT
    )
    BEGIN
        SELECT 
            p.product_id,
            p.name,
            p.price,
            p.description,
            p.image_url,
            p.avg_rating,
            c.name AS category_name,
            COALESCE(ps.score, 0) AS preference_score,
            CASE 
                WHEN COALESCE(ps.score, 0) > 0 THEN 1 
                ELSE 0 
            END AS is_interest_match
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN preference_scores ps 
            ON p.category_id = ps.category_id
            AND ps.user_id = p_user_id
        WHERE p.product_id NOT IN (
            SELECT product_id FROM swipes WHERE user_id = p_user_id
        )
        AND p.is_active = TRUE
        ORDER BY 
            is_interest_match DESC,
            preference_score DESC, 
            p.avg_rating DESC,
            p.created_at DESC
        LIMIT p_limit;
    END
    """
    
    try:
        cursor.execute(sql1)
        conn.commit()
        print("   ✅ get_personalized_feed created (interest-based)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
    
    # 2. Get user interest summary (categories they like)
    print("2. Creating get_user_interests procedure...")
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS get_user_interests")
        conn.commit()
    except:
        pass
    
    sql2 = """
    CREATE PROCEDURE get_user_interests(
        IN p_user_id INT
    )
    BEGIN
        SELECT 
            c.category_id,
            c.name AS category_name,
            COUNT(s.swipe_id) AS like_count,
            ps.score AS preference_score,
            ROUND(100 * ps.score / (SELECT SUM(score) FROM preference_scores WHERE user_id = p_user_id), 1) AS interest_percentage
        FROM preference_scores ps
        JOIN categories c ON ps.category_id = c.category_id
        LEFT JOIN swipes s ON s.user_id = ps.user_id AND s.liked = TRUE
        WHERE ps.user_id = p_user_id AND ps.score > 0
        GROUP BY ps.user_id, c.category_id
        ORDER BY ps.score DESC;
    END
    """
    
    try:
        cursor.execute(sql2)
        conn.commit()
        print("   ✅ get_user_interests created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
    
    # 3. get_liked_products
    print("3. Creating get_liked_products...")
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS get_liked_products")
        conn.commit()
    except:
        pass
    
    sql3 = """
    CREATE PROCEDURE get_liked_products(
        IN p_user_id INT
    )
    BEGIN
        SELECT DISTINCT
            p.product_id,
            p.name,
            p.description,
            p.price,
            p.image_url,
            p.avg_rating,
            p.category_id,
            c.name AS category_name,
            s.swiped_at,
            p.seller_id
        FROM products p
        JOIN swipes s ON p.product_id = s.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE s.user_id = p_user_id 
          AND s.liked = TRUE
          AND p.is_active = TRUE
        ORDER BY s.swiped_at DESC;
    END
    """
    
    try:
        cursor.execute(sql3)
        conn.commit()
        print("   ✅ get_liked_products created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
    
    # Test the procedures
    print("\n3. Testing procedures...")
    
    # Get a user ID
    cursor.execute("SELECT user_id FROM users WHERE role = 'buyer' LIMIT 1")
    user_row = cursor.fetchone()
    
    if user_row:
        user_id = user_row[0]
        
        try:
            cursor.callproc('get_personalized_feed', (user_id, 5))
            results = []
            for result in cursor.stored_results():
                results = result.fetchall()
            print(f"   ✅ get_personalized_feed works ({len(results)} products)")
        except Exception as e:
            print(f"   ❌ get_personalized_feed failed: {e}")
        
        try:
            cursor.callproc('get_liked_products', (user_id,))
            results = []
            for result in cursor.stored_results():
                results = result.fetchall()
            print(f"   ✅ get_liked_products works ({len(results)} liked products)")
        except Exception as e:
            print(f"   ❌ get_liked_products failed: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ Procedures setup complete!")
    print("="*50)
    print("\n🚀 The feed should now work!")
    print("   - Try accessing /feed")
    print("   - Or check browser console for any JS errors\n")

if __name__ == "__main__":
    create_procedures()
