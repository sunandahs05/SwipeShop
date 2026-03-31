-- ============================================
-- SwipeShop - Sample Data for Testing and Demo
-- ============================================

USE swipeshop;

-- ============================================
-- CATEGORIES
-- ============================================
INSERT INTO categories (name, parent_id, is_active) VALUES
('Electronics', NULL, TRUE),
('Clothing', NULL, TRUE),
('Home & Garden', NULL, TRUE),
('Sports & Outdoors', NULL, TRUE),
('Books', NULL, TRUE);

-- ============================================
-- USERS (Buyers & Sellers)
-- ============================================

-- Sellers
INSERT INTO users (name, email, password_hash, role, is_active) VALUES
('TechMart Seller', 'seller1@swipeshop.com', '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890', 'seller', TRUE),
('Fashion Hub', 'seller2@swipeshop.com', '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890', 'seller', TRUE),
('HomeGoods Plus', 'seller3@swipeshop.com', '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890', 'seller', TRUE);

-- Buyers
INSERT INTO users (name, email, password_hash, role, total_spent, is_active) VALUES
('John Customer', 'john@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890', 'buyer', 0.00, TRUE),
('Jane Shopper', 'jane@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890', 'buyer', 0.00, TRUE),
('Mike Buyer', 'mike@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890', 'buyer', 0.00, TRUE);

-- ============================================
-- PRODUCTS (with image URLs from dummyjson API)
-- ============================================
INSERT INTO products (seller_id, category_id, name, description, price, stock, avg_rating, image_url, is_active) VALUES
-- Electronics
(1, 1, 'Wireless Headphones', 'Premium quality wireless headphones with noise cancellation', 79.99, 25, 4.5, 'https://i.dummyjson.com/data/products/3/1.jpg', TRUE),
(1, 1, 'Smart Watch', 'Advanced fitness tracking and notifications', 199.99, 15, 4.3, 'https://i.dummyjson.com/data/products/32/1.jpg', TRUE),
(1, 1, 'USB-C Cable', 'Durable USB-C fast charging cable', 12.99, 100, 4.2, 'https://i.dummyjson.com/data/products/23/1.jpg', TRUE),
(1, 1, '4K Webcam', 'Professional 4K webcam for streaming and video calls', 149.99, 10, 4.6, 'https://i.dummyjson.com/data/products/24/1.jpg', TRUE),
(1, 1, 'Portable Charger', '20000mAh portable power bank with fast charging', 29.99, 50, 4.4, 'https://i.dummyjson.com/data/products/25/1.jpg', TRUE),

-- Clothing
(2, 2, 'Cotton T-Shirt', 'Comfortable 100% cotton t-shirt in multiple colors', 19.99, 80, 4.1, 'https://i.dummyjson.com/data/products/1/1.jpg', TRUE),
(2, 2, 'Denim Jeans', 'Classic style premium denim jeans', 59.99, 40, 4.3, 'https://i.dummyjson.com/data/products/4/1.jpg', TRUE),
(2, 2, 'Sports Jacket', 'Lightweight and breathable sports jacket', 89.99, 30, 4.5, 'https://i.dummyjson.com/data/products/5/1.jpg', TRUE),
(2, 2, 'Running Shoes', 'Professional running shoes with cushioning', 99.99, 35, 4.7, 'https://i.dummyjson.com/data/products/6/1.jpg', TRUE),
(2, 2, 'Wool Sweater', 'Warm and cozy wool sweater for winter', 49.99, 25, 4.2, 'https://i.dummyjson.com/data/products/7/1.jpg', TRUE),

-- Home & Garden
(3, 3, 'LED Desk Lamp', 'Adjustable LED desk lamp with touch control', 39.99, 45, 4.4, 'https://i.dummyjson.com/data/products/8/1.jpg', TRUE),
(3, 3, 'Throw Pillow', 'Decorative throw pillow with premium fabric', 24.99, 60, 4.0, 'https://i.dummyjson.com/data/products/9/1.jpg', TRUE),
(3, 3, 'Wall Clock', 'Modern analog wall clock with silent mechanism', 44.99, 35, 4.3, 'https://i.dummyjson.com/data/products/10/1.jpg', TRUE),
(3, 3, 'Plant Pot', 'Ceramic plant pot with drainage hole', 14.99, 75, 4.1, 'https://i.dummyjson.com/data/products/11/1.jpg', TRUE),

-- Books
(2, 5, 'JavaScript Guide', 'Comprehensive guide to modern JavaScript programming', 34.99, 20, 4.6, 'https://i.dummyjson.com/data/products/2/1.jpg', TRUE),
(2, 5, 'Web Development Handbook', 'Complete handbook for web developers', 44.99, 15, 4.5, 'https://i.dummyjson.com/data/products/12/1.jpg', TRUE);

-- ============================================
-- ADDRESSES
-- ============================================
INSERT INTO addresses (user_id, line1, line2, city, state, pincode, is_default) VALUES
(4, '123 Main St', 'Apt 101', 'New York', 'NY', '10001', TRUE),
(4, '456 Oak Ave', NULL, 'Los Angeles', 'CA', '90001', FALSE),
(5, '789 Pine Rd', 'Suite 200', 'Chicago', 'IL', '60601', TRUE),
(6, '321 Elm St', NULL, 'Houston', 'TX', '77001', TRUE);

-- ============================================
-- SAMPLE SWIPES (User interactions)
-- ============================================

-- John (user_id=4) likes some products
INSERT INTO swipes (user_id, product_id, liked, swiped_at) VALUES
(4, 1, TRUE, NOW()),              -- Liked: Wireless Headphones
(4, 2, TRUE, NOW() - INTERVAL 1 DAY),  -- Liked: Smart Watch
(4, 6, FALSE, NOW() - INTERVAL 2 DAY), -- Disliked: Cotton T-Shirt
(4, 7, TRUE, NOW() - INTERVAL 3 DAY),  -- Liked: Denim Jeans
(4, 9, TRUE, NOW() - INTERVAL 4 DAY);  -- Liked: Sports Jacket

-- Jane (user_id=5) likes different products
INSERT INTO swipes (user_id, product_id, liked, swiped_at) VALUES
(5, 3, TRUE, NOW()),              -- Liked: USB-C Cable
(5, 8, TRUE, NOW() - INTERVAL 1 DAY),  -- Liked: 4K Webcam
(5, 12, FALSE, NOW() - INTERVAL 2 DAY),-- Disliked: Running Shoes
(5, 13, TRUE, NOW() - INTERVAL 3 DAY), -- Liked: Wool Sweater
(5, 15, TRUE, NOW() - INTERVAL 4 DAY); -- Liked: LED Desk Lamp

-- Mike (user_id=6) likes tech and home products
INSERT INTO swipes (user_id, product_id, liked, swiped_at) VALUES
(6, 2, TRUE, NOW()),              -- Liked: Smart Watch
(6, 4, TRUE, NOW() - INTERVAL 1 DAY),  -- Liked: Portable Charger
(6, 15, TRUE, NOW() - INTERVAL 2 DAY), -- Liked: LED Desk Lamp
(6, 16, TRUE, NOW() - INTERVAL 3 DAY), -- Liked: Throw Pillow
(6, 18, TRUE, NOW() - INTERVAL 4 DAY); -- Liked: Wall Clock

-- ============================================
-- CARTS
-- ============================================
INSERT INTO cart (user_id) VALUES (4), (5), (6);

-- ============================================
-- PREFERENCE SCORES (User category preferences)
-- ============================================
INSERT INTO preference_scores (user_id, category_id, score) VALUES
-- John: Likes Electronics and Sports
(4, 1, 75.00),  -- Electronics
(4, 2, 50.00),  -- Clothing
(4, 4, 65.00),  -- Sports & Outdoors

-- Jane: Likes Tech and Home
(5, 1, 70.00),  -- Electronics
(5, 3, 60.00),  -- Home & Garden
(5, 5, 55.00),  -- Books

-- Mike: Tech enthusiast
(6, 1, 85.00),  -- Electronics
(6, 3, 60.00);  -- Home & Garden
