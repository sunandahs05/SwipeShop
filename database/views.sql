
-- ============================================
-- VIEW: vw_order_summary
-- Used for admin reports (order-level aggregation)
-- ============================================
CREATE VIEW vw_order_summary AS
SELECT 
    o.order_id,
    u.user_id,
    u.name AS user_name,
    u.email,
    o.status,
    o.subtotal,
    o.created_at,
    COUNT(oi.product_id) AS total_items
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id;

DROP VIEW IF EXISTS vw_product_performance;

-- ============================================
-- VIEW: vw_product_performance
-- Helps identify trending products
-- Combines likes + purchases
-- ============================================
CREATE VIEW vw_product_performance AS
SELECT 
    p.product_id,
    p.name,
    p.category_id,
    COUNT(DISTINCT CASE WHEN s.liked = TRUE THEN s.swipe_id END) AS total_likes,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM products p
LEFT JOIN swipes s ON p.product_id = s.product_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id;