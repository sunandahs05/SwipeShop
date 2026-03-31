-- ============================================
-- SwipeShop - Quick Setup for "Liked Products" Feature
-- Run this script to add the liked products feature to existing SwipeShop database
-- ============================================

USE swipeshop;

-- ============================================
-- 1. ADD IMAGE_URL COLUMN TO PRODUCTS (if not exists)
-- ============================================

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);

-- ============================================
-- 2. CREATE GET_PERSONALIZED_FEED PROCEDURE (with image_url)
-- ============================================

DROP PROCEDURE IF EXISTS get_personalized_feed;

DELIMITER $$

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
        COALESCE(ps.score, 0) AS preference_score
    FROM products p
    LEFT JOIN preference_scores ps
        ON p.category_id = ps.category_id
        AND ps.user_id = p_user_id
    WHERE p.product_id NOT IN (
        SELECT product_id FROM swipes WHERE user_id = p_user_id
    )
    AND p.is_active = TRUE
    ORDER BY preference_score DESC, p.created_at DESC
    LIMIT p_limit;
END $$

DELIMITER ;

-- ============================================
-- 3. CREATE GET_LIKED_PRODUCTS PROCEDURE
-- ============================================

DROP PROCEDURE IF EXISTS get_liked_products;

DELIMITER $$

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
END $$

DELIMITER ;

-- ============================================
-- 4. VERIFY INSTALLATION
-- ============================================

-- Check if image_url column exists
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'products' AND COLUMN_NAME = 'image_url';

-- Test get_liked_products procedure with a sample user
-- Replace 1 with actual user_id
-- CALL get_liked_products(1);

-- ============================================
-- 5. UPDATE SAMPLE PRODUCTS WITH IMAGE URLS (Optional)
-- ============================================

-- Adding sample image URLs to existing products or new products
-- This example assumes you have existing products

-- If you have no products, insert sample ones:
/*
INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active)
SELECT 
    u.user_id as seller_id,
    1 as category_id,
    'Wireless Headphones' as name,
    'Premium quality wireless headphones with noise cancellation' as description,
    79.99 as price,
    25 as stock,
    4.5 as avg_rating,
    'https://i.dummyjson.com/data/products/3/1.jpg' as image_url,
    TRUE as is_active
FROM users u
WHERE u.role = 'seller'
LIMIT 1;
*/

-- Or update existing products with image URLs:
-- UPDATE products SET image_url = 'https://i.dummyjson.com/data/products/1/1.jpg' WHERE product_id = 1;

-- ============================================
-- SUMMARY
-- ============================================
-- 
-- Features Added:
-- ✓ image_url column in products table
-- ✓ get_personalized_feed procedure (updated)
-- ✓ get_liked_products procedure (new)
--
-- API Endpoints Added (in backend/routes/swipe_routes.py):
-- ✓ GET /api/liked - Fetch liked products
-- ✓ POST /api/unlike - Remove from likes
--
-- Frontend Added:
-- ✓ /liked page route
-- ✓ liked.html template with vanilla JS
-- ✓ Navigation link in base.html
--
-- Database Status: READY TO USE
--
