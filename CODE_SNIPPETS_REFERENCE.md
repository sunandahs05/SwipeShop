# SwipeShop "Liked Products" - Copy-Paste Code Reference

This document contains all the copy-paste ready code for the "Liked Products" feature, organized by component.

---

## 🗄️ DATABASE LAYER

### SQL: Get Liked Products Query

**Simple SELECT**:
```sql
SELECT 
    p.product_id,
    p.name,
    p.description,
    p.price,
    p.image_url,
    p.avg_rating,
    c.name AS category_name
FROM products p
JOIN swipes s ON p.product_id = s.product_id
JOIN categories c ON p.category_id = c.category_id
WHERE s.user_id = 4 
  AND s.liked = TRUE
  AND p.is_active = TRUE
ORDER BY s.swiped_at DESC;
```

**Count Liked Products**:
```sql
SELECT COUNT(*) as total_liked
FROM swipes
WHERE user_id = 4 AND liked = TRUE;
```

**Get Liked with Review Count**:
```sql
SELECT 
    p.product_id,
    p.name,
    p.price,
    p.image_url,
    p.avg_rating,
    COUNT(r.review_id) as review_count,
    COUNT(s.swipe_id) as times_liked
FROM products p
JOIN swipes s ON p.product_id = s.product_id
LEFT JOIN reviews r ON p.product_id = r.product_id
WHERE s.user_id = 4 AND s.liked = TRUE
GROUP BY p.product_id
ORDER BY s.swiped_at DESC;
```

**Stored Procedure**:
```sql
DROP PROCEDURE IF EXISTS get_liked_products;

DELIMITER $$

CREATE PROCEDURE get_liked_products(IN p_user_id INT)
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
END $$

DELIMITER ;
```

---

## 🔧 BACKEND LAYER

### Python/Flask: Liked Products Routes

**Complete File: `backend/routes/swipe_routes.py`**:
```python
from flask import Blueprint, request, jsonify, session
from db import get_db_connection

swipe_bp = Blueprint("swipe", __name__)

# GET FEED
@swipe_bp.route("/api/feed", methods=["GET"])
def get_feed():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.callproc("get_personalized_feed", (user_id, 10))

    results = []
    for result in cursor.stored_results():
        results = result.fetchall()

    return jsonify(results)


# GET LIKED PRODUCTS
@swipe_bp.route("/api/liked", methods=["GET"])
def get_liked_products():
    """
    Returns all products that the user has liked (swiped right on).
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.callproc("get_liked_products", (user_id,))

        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# SWIPE ACTION
@swipe_bp.route("/api/swipe", methods=["POST"])
def swipe():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO swipes(user_id, product_id, liked)
            VALUES(%s, %s, %s)
        """, (user_id, data.get("product_id"), data.get("liked")))

        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Swipe recorded"})


# UNLIKE PRODUCT (Remove from liked)
@swipe_bp.route("/api/unlike", methods=["POST"])
def unlike():
    """
    Removes a product from the user's liked list by deleting the swipe.
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    product_id = data.get("product_id") if data else None

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM swipes
            WHERE user_id = %s AND product_id = %s AND liked = TRUE
        """, (user_id, product_id))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Product was not in likes"}), 200

        return jsonify({"message": "Product removed from likes"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
```

### Python/Flask: Flask App Route

**Add to `backend/app.py`:**
```python
@app.route("/liked")
def liked_page():
    return render_template("liked.html")
```

---

## 🎨 FRONTEND LAYER

### HTML/CSS/JavaScript - Key Code Snippets

**Fetch Liked Products**:
```javascript
async function loadLikedProducts() {
    try {
        const response = await fetch('/api/liked');
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Failed to load liked products');
        }

        const likedProducts = await response.json();
        renderLikedProducts(likedProducts);
    } catch (error) {
        showAlert('Error loading liked products: ' + error.message, 'error');
    }
}
```

**Remove from Likes**:
```javascript
async function handleRemoveLike(productId, button) {
    try {
        button.disabled = true;
        button.textContent = 'Removing...';

        const response = await fetch('/api/unlike', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ product_id: productId })
        });

        if (!response.ok) {
            throw new Error('Failed to remove from likes');
        }

        // Remove card from DOM
        const cardElement = document.querySelector(`[data-product-id="${productId}"]`);
        if (cardElement) {
            cardElement.style.opacity = '0';
            cardElement.style.transform = 'scale(0.95)';
            setTimeout(() => cardElement.remove(), 300);
        }

        showAlert('Product removed from likes', 'success');
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
        button.disabled = false;
        button.textContent = '✕ Remove';
    }
}
```

**Add to Cart**:
```javascript
async function handleAddToCart(productId) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                qty: 1
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to add to cart');
        }

        showAlert('Product added to cart!', 'success');
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}
```

**Product Card HTML**:
```javascript
function createProductCard(product) {
    const html = `
        <div class="product-card" data-product-id="${product.product_id}">
            <div class="product-image-container">
                <img src="${escapeHTML(product.image_url || 'https://via.placeholder.com/250x200')}" 
                     alt="${escapeHTML(product.name)}"
                     class="product-image"
                     onerror="this.src='https://via.placeholder.com/250x200?text=Image+Error'">
            </div>
            <div class="product-content">
                <div class="product-category">${escapeHTML(product.category_name || 'Unknown')}</div>
                <h3 class="product-name">${escapeHTML(product.name)}</h3>
                <p class="product-description">${escapeHTML(product.description || 'No description')}</p>
                <div class="product-footer">
                    <div class="product-price">$${parseFloat(product.price).toFixed(2)}</div>
                    <div class="product-rating">
                        <span class="rating-value">${parseFloat(product.avg_rating).toFixed(1)}</span>
                        <span class="star">★★★★☆</span>
                    </div>
                </div>
                <div class="product-actions">
                    <button class="btn-small btn-remove" onclick="handleRemoveLike(${product.product_id}, this)">✕ Remove</button>
                    <button class="btn-small btn-cart" onclick="handleAddToCart(${product.product_id})">🛒 Cart</button>
                </div>
            </div>
        </div>
    `;
    return html;
}
```

**CSS: Responsive Grid**:
```css
.liked-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

@media (max-width: 768px) {
    .liked-grid {
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .liked-grid {
        grid-template-columns: 1fr;
    }
}
```

**CSS: Product Card**:
```css
.product-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
}

.product-card:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-4px);
}

.product-image-container {
    width: 100%;
    height: 200px;
    background: #f9f9f9;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.product-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: cover;
    width: 100%;
    height: 100%;
}
```

**HTML: Navigation Link**:
```html
<!-- In base.html -->
<a href="/liked" class="nav-auth" style="display:none;">♥ Liked</a>
```

**XSS Protection Helper**:
```javascript
function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

## 📦 Sample Product Data (SQL INSERT)

```sql
-- Electronics
INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active) VALUES
(1, 1, 'Wireless Headphones', 'Premium quality wireless headphones with noise cancellation', 79.99, 25, 4.5, 'https://i.dummyjson.com/data/products/3/1.jpg', TRUE),
(1, 1, 'Smart Watch', 'Advanced fitness tracking and notifications', 199.99, 15, 4.3, 'https://i.dummyjson.com/data/products/32/1.jpg', TRUE),
(1, 1, 'USB-C Cable', 'Durable USB-C fast charging cable', 12.99, 100, 4.2, 'https://i.dummyjson.com/data/products/23/1.jpg', TRUE),
(1, 1, '4K Webcam', 'Professional 4K webcam for streaming', 149.99, 10, 4.6, 'https://i.dummyjson.com/data/products/24/1.jpg', TRUE),
(1, 1, 'Portable Charger', '20000mAh portable power bank with fast charging', 29.99, 50, 4.4, 'https://i.dummyjson.com/data/products/25/1.jpg', TRUE);

-- Clothing
INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active) VALUES
(2, 2, 'Cotton T-Shirt', 'Comfortable 100% cotton t-shirt in multiple colors', 19.99, 80, 4.1, 'https://i.dummyjson.com/data/products/1/1.jpg', TRUE),
(2, 2, 'Denim Jeans', 'Classic style premium denim jeans', 59.99, 40, 4.3, 'https://i.dummyjson.com/data/products/4/1.jpg', TRUE),
(2, 2, 'Sports Jacket', 'Lightweight and breathable sports jacket', 89.99, 30, 4.5, 'https://i.dummyjson.com/data/products/5/1.jpg', TRUE),
(2, 2, 'Running Shoes', 'Professional running shoes with cushioning', 99.99, 35, 4.7, 'https://i.dummyjson.com/data/products/6/1.jpg', TRUE),
(2, 2, 'Wool Sweater', 'Warm and cozy wool sweater for winter', 49.99, 25, 4.2, 'https://i.dummyjson.com/data/products/7/1.jpg', TRUE);

-- Home & Garden
INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active) VALUES
(3, 3, 'LED Desk Lamp', 'Adjustable LED desk lamp with touch control', 39.99, 45, 4.4, 'https://i.dummyjson.com/data/products/8/1.jpg', TRUE),
(3, 3, 'Throw Pillow', 'Decorative throw pillow with premium fabric', 24.99, 60, 4.0, 'https://i.dummyjson.com/data/products/9/1.jpg', TRUE),
(3, 3, 'Wall Clock', 'Modern analog wall clock with silent mechanism', 44.99, 35, 4.3, 'https://i.dummyjson.com/data/products/10/1.jpg', TRUE),
(3, 3, 'Plant Pot', 'Ceramic plant pot with drainage hole', 14.99, 75, 4.1, 'https://i.dummyjson.com/data/products/11/1.jpg', TRUE);

-- Books
INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active) VALUES
(2, 5, 'JavaScript Guide', 'Comprehensive guide to modern JavaScript programming', 34.99, 20, 4.6, 'https://i.dummyjson.com/data/products/2/1.jpg', TRUE),
(2, 5, 'Web Development Handbook', 'Complete handbook for web developers', 44.99, 15, 4.5, 'https://i.dummyjson.com/data/products/12/1.jpg', TRUE);
```

---

## 🧪 Testing API Endpoints

### Test with cURL

**Get Liked Products**:
```bash
curl -X GET http://localhost:5000/api/liked \
  -H "Cookie: session=YOUR_SESSION_ID"
```

**Unlike a Product**:
```bash
curl -X POST http://localhost:5000/api/unlike \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_ID" \
  -d '{"product_id": 5}'
```

### Test with JavaScript (in browser console)

**Fetch and Display**:
```javascript
fetch('/api/liked')
  .then(r => r.json())
  .then(data => console.table(data));
```

**Remove from Likes**:
```javascript
fetch('/api/unlike', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ product_id: 5 })
}).then(r => r.json()).then(d => console.log(d));
```

---

## 🔍 Debugging Queries

**Check if user has liked any products**:
```sql
SELECT * FROM swipes WHERE user_id = 4 AND liked = TRUE;
```

**Check swipes table structure**:
```sql
DESCRIBE swipes;
```

**Check products with images**:
```sql
SELECT product_id, name, image_url, price FROM products WHERE image_url IS NOT NULL;
```

**Test stored procedure**:
```sql
CALL get_liked_products(4);
```

**Check for duplicate likes**:
```sql
SELECT product_id, COUNT(*) as cnt 
FROM swipes 
WHERE user_id = 4 AND liked = TRUE 
GROUP BY product_id 
HAVING cnt > 1;
```

---

## ✅ Validation Checklist

- [ ] Column `image_url` added to products table
- [ ] `get_liked_products` procedure created
- [ ] `/api/liked` endpoint returns JSON array
- [ ] `/api/unlike` endpoint deletes swipe record
- [ ] `/liked` page loads without errors
- [ ] Product images display correctly
- [ ] "Remove" button removes product
- [ ] "Add to Cart" button adds product
- [ ] Navigation link appears after login
- [ ] Empty state shows when no products liked
- [ ] Responsive design works on mobile
- [ ] XSS protection active (check HTML escaping)
- [ ] Session auth required for endpoints

---

**Ready to copy and use! 🚀**
