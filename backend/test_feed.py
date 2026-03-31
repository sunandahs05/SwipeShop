from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

print("\n" + "="*60)
print("   SWIPESHOP FEED & LIKED PRODUCTS VERIFICATION")
print("="*60)

# Check products
print("\n1️⃣  PRODUCTS IN DATABASE:")
cursor.execute('SELECT COUNT(*) as cnt FROM products')
count = cursor.fetchone()['cnt']
print(f"   ✅ Total products: {count}")

cursor.execute('SELECT product_id, name, image_url FROM products LIMIT 3')
for row in cursor.fetchall():
    has_img = "✅" if row['image_url'] else "❌"
    print(f"   {has_img} {row['product_id']:2d}. {row['name']:30s} → {row['image_url'][:50] if row['image_url'] else 'NO IMAGE'}")

# Check stored procedures
print("\n2️⃣  STORED PROCEDURES:")
cursor.execute("""
    SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES 
    WHERE ROUTINE_SCHEMA = 'swipeshop'
""")
procedures = cursor.fetchall()
proc_names = [p['ROUTINE_NAME'] for p in procedures]

for proc in ['get_personalized_feed', 'get_liked_products']:
    if proc in proc_names:
        print(f"   ✅ {proc}")
    else:
        print(f"   ❌ {proc} - MISSING!")

# Check swipes
print("\n3️⃣  SWIPES RECORDED:")
cursor.execute('SELECT COUNT(*) as cnt FROM swipes')
count = cursor.fetchone()['cnt']
print(f"   Total swipes: {count}")

cursor.execute("""
    SELECT s.user_id, u.email, COUNT(*) as total_swipes,
           SUM(CASE WHEN s.liked = 1 THEN 1 ELSE 0 END) as liked_count
    FROM swipes s
    JOIN users u ON s.user_id = u.user_id
    GROUP BY s.user_id, u.email
    LIMIT 3
""")

for row in cursor.fetchall():
    liked = int(row['liked_count'] or 0)
    total = int(row['total_swipes'] or 0)
    discarded = total - liked
    print(f"   👤 {row['email']:25s} → {liked} liked, {discarded} discarded (Total: {total})")

# Test API endpoint
print("\n4️⃣  TESTING API:")
cursor.execute("SELECT user_id FROM users WHERE role = 'buyer' LIMIT 1")
user = cursor.fetchone()

if user:
    user_id = user['user_id']
    
    # Test get_personalized_feed
    try:
        cursor.callproc('get_personalized_feed', (user_id, 5))
        count = 0
        for result in cursor.stored_results():
            count = len(result.fetchall())
        print(f"   ✅ get_personalized_feed() → {count} products available")
    except Exception as e:
        print(f"   ❌ get_personalized_feed() error: {e}")
    
    # Test get_liked_products
    try:
        cursor.callproc('get_liked_products', (user_id,))
        count = 0
        for result in cursor.stored_results():
            products = result.fetchall()
            count = len(products)
            if products:
                print(f"   ✅ get_liked_products() → {count} liked products")
                for p in products:
                    print(f"      - {p['name']} (⭐ {p['avg_rating']})")
        if count == 0:
            print(f"   ℹ️  get_liked_products() → No likes yet (try swiping right!)")
    except Exception as e:
        print(f"   ❌ get_liked_products() error: {e}")

print("\n" + "="*60)
print("✅ READY TO TEST!")
print("="*60)
print("""
HOW TO TEST:
1. Go to http://localhost:5000/feed
2. Login with: test@gmail.com (or any buyer account)
3. Swipe RIGHT → Product goes to Liked Products ♥
4. Swipe LEFT → Product is discarded ✕
5. Check /liked to see your liked products
6. Return here and run this script again to verify!

COLORS:
✅ = Working correctly
❌ = Problem found
⭐ = Rating
""")
