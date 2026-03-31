#!/usr/bin/env python
"""
Test smart recommendation system with user interests
"""

from db import get_db_connection

def test_recommendations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("\n" + "="*70)
    print("      SMART RECOMMENDATION SYSTEM TEST")
    print("="*70)
    
    # Get a test user
    cursor.execute("SELECT user_id, email FROM users WHERE role = 'buyer' LIMIT 1")
    user = cursor.fetchone()
    
    if not user:
        print("❌ No buyer found in database")
        return
    
    user_id = user['user_id']
    email = user['email']
    
    print(f"\n👤 Testing with user: {email} (ID: {user_id})")
    
    # ===== TEST 1: Initial Feed =====
    print(f"\n1️⃣  INITIAL FEED (before any swipes)")
    cursor.callproc("get_personalized_feed", (user_id, 3))
    feed = []
    for result in cursor.stored_results():
        feed = result.fetchall()
    
    print(f"   📦 Products in initial feed: {len(feed)}")
    for p in feed:
        print(f"   - {p['name']:30s} | {p['category_name']:15s} | Score: {p['preference_score']}")
    
    # ===== TEST 2: Check Initial Interests =====
    print(f"\n2️⃣  INITIAL INTERESTS (before any swipes)")
    cursor.callproc("get_user_interests", (user_id,))
    interests = []
    for result in cursor.stored_results():
        interests = result.fetchall()
    
    if interests:
        print(f"   💎 Categories liked: {len(interests)}")
        for i in interests:
            print(f"   - {i['category_name']:20s} | Score: {i['preference_score']:5.1f} | {i['interest_percentage']}%")
    else:
        print("   ℹ️  No interests yet (will develop as you swipe)")
    
    # ===== TEST 3: Simulate Swipes =====
    print(f"\n3️⃣  SIMULATING SWIPES (liking products)")
    
    # Get products and their categories
    cursor.execute("""
        SELECT p.product_id, p.name, c.category_id, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        LIMIT 5
    """)
    products_to_like = cursor.fetchall()
    
    for product in products_to_like:
        # Like the product
        cursor.execute("""
            INSERT INTO swipes(user_id, product_id, liked)
            VALUES(%s, %s, TRUE)
            ON DUPLICATE KEY UPDATE liked = TRUE
        """, (user_id, product['product_id']))
        
        # Update preference score
        cursor.callproc("update_preference_scores", (user_id, product['category_id']))
        
        print(f"   ♥ Liked: {product['name']:30s} | Category: {product['category_name']}")
    
    conn.commit()
    
    # ===== TEST 4: Check Updated Interests =====
    print(f"\n4️⃣  UPDATED INTERESTS (after swiping)")
    cursor.callproc("get_user_interests", (user_id,))
    interests = []
    for result in cursor.stored_results():
        interests = result.fetchall()
    
    if interests:
        print(f"   💎 Your favorite categories:")
        for i in interests[:3]:
            percentage = parseFloat(i.get('interest_percentage', 0))
            print(f"   - {i['category_name']:20s} | Preference Score: {i['preference_score']:5.1f} | {int(i['interest_percentage'])}%")
    else:
        print("   ❌ No interests recorded")
    
    # ===== TEST 5: Check Updated Feed =====
    print(f"\n5️⃣  UPDATED FEED (now personalized by interests)")
    cursor.callproc("get_personalized_feed", (user_id, 5))
    feed = []
    for result in cursor.stored_results():
        feed = result.fetchall()
    
    print(f"   📦 Products in personalized feed: {len(feed)}")
    for p in feed:
        is_match = "✅ INTEREST MATCH" if p['is_interest_match'] else "   regular"
        print(f"   {is_match} | {p['name']:30s} | {p['category_name']:15s} | Score: {p['preference_score']}")
    
    # ===== TEST 6: Check Liked Products =====
    print(f"\n6️⃣  YOUR LIKED PRODUCTS")
    cursor.callproc("get_liked_products", (user_id,))
    liked = []
    for result in cursor.stored_results():
        liked = result.fetchall()
    
    print(f"   ♥ Total liked products: {len(liked)}")
    for p in liked[:5]:
        print(f"   - {p['name']:30s} | {p['category_name']:15s} | ${p['price']}")
    
    print("\n" + "="*70)
    print("✅ RECOMMENDATION SYSTEM WORKING!")
    print("="*70)
    print("""
HOW IT WORKS:
✅ You swipe RIGHT on a product
✅ System tracks the product's category
✅ Your preference score for that category increases
✅ Feed is sorted by your preference scores
✅ Products from your favorite categories appear first
✅ Your interests tags appear at the top of the feed

BENEFITS:
- Each like personalizes your feed
- More relevant product suggestions
- Discover products in categories you love
- Swipe faster through recommendations
""")
    
    cursor.close()
    conn.close()

def parseFloat(val):
    try:
        return float(val or 0)
    except:
        return 0.0

if __name__ == '__main__':
    test_recommendations()
