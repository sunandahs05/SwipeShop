-- ============================================
-- SwipeShop - Procedures & Functions
-- ============================================

USE swipeshop;

-- ============================================
-- FUNCTION: get_cart_total
-- Purpose:
-- Returns total value of items in user's cart
-- Output:
-- DECIMAL (total amount)
-- ============================================

DROP FUNCTION IF EXISTS get_cart_total;

DELIMITER $$

CREATE FUNCTION get_cart_total(p_user_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
BEGIN
    DECLARE v_total DECIMAL(12,2);

    SELECT COALESCE(SUM(ci.quantity * p.price), 0.00)
    INTO v_total
    FROM cart c
    JOIN cart_items ci ON c.cart_id = ci.cart_id
    JOIN products p ON ci.product_id = p.product_id
    WHERE c.user_id = p_user_id;

    RETURN v_total;
END $$

DELIMITER ;

-- ============================================
-- PROCEDURE: checkout_cart
-- Purpose:
-- Converts cart → order (atomic transaction)
-- Prevents stock overselling
-- ============================================
DROP PROCEDURE IF EXISTS checkout_cart;

DELIMITER $$

CREATE PROCEDURE checkout_cart(
    IN p_user_id INT,
    IN p_address_id INT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_stock INT;
    DECLARE v_order_id INT;

    DECLARE cur CURSOR FOR
        SELECT ci.product_id, ci.quantity, p.price
        FROM cart c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        JOIN products p ON ci.product_id = p.product_id
        WHERE c.user_id = p_user_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    START TRANSACTION;

    INSERT INTO orders(user_id, address_id, status)
    VALUES(p_user_id, p_address_id, 'pending');

    SET v_order_id = LAST_INSERT_ID();

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_product_id, v_quantity, v_price;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Lock row to prevent race condition
        SELECT stock INTO v_stock
        FROM products
        WHERE product_id = v_product_id
        FOR UPDATE;

        IF v_stock < v_quantity THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Stock not sufficient';
        END IF;

        INSERT INTO order_items(order_id, product_id, quantity, price_at_purchase, line_total)
        VALUES(
            v_order_id,
            v_product_id,
            v_quantity,
            v_price,
            v_quantity * v_price
        );

        UPDATE products
        SET stock = stock - v_quantity
        WHERE product_id = v_product_id;

    END LOOP;

    CLOSE cur;

    -- Update order total
    UPDATE orders
    SET subtotal = (
        SELECT SUM(line_total)
        FROM order_items
        WHERE order_id = v_order_id
    )
    WHERE order_id = v_order_id;

    -- Clear cart
    DELETE ci FROM cart_items ci
    JOIN cart c ON ci.cart_id = c.cart_id
    WHERE c.user_id = p_user_id;

    COMMIT;

END $$

DELIMITER ;

-- ============================================
-- PROCEDURE: get_personalized_feed
-- Purpose:
-- Returns top-N products based on user preference scores
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
-- PROCEDURE: get_liked_products
-- Purpose:
-- Returns all products that a user has liked (swiped right on)
-- Includes product details and avg_rating
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
-- PROCEDURE: get_sales_report
-- Purpose:
-- Category-wise revenue report
-- ============================================
DROP PROCEDURE IF EXISTS get_sales_report;

DELIMITER $$

CREATE PROCEDURE get_sales_report(
    IN p_start DATE,
    IN p_end DATE
)
BEGIN
    SELECT 
        c.category_id,
        c.name AS category_name,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.line_total) AS revenue,
        AVG(oi.line_total) AS avg_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    WHERE o.status != 'cancelled'
      AND o.created_at BETWEEN p_start AND p_end
    GROUP BY c.category_id
    ORDER BY revenue DESC;
END $$

DELIMITER ;

-- ============================================
-- PROCEDURE: get_user_activity_report
-- Purpose:
-- Detailed user analytics
-- ============================================
DROP PROCEDURE IF EXISTS get_user_activity_report;

DELIMITER $$

CREATE PROCEDURE get_user_activity_report(
    IN p_user_id INT
)
BEGIN

    -- Swipe Stats
    SELECT 
        COUNT(*) AS total_swipes,
        SUM(CASE WHEN liked = TRUE THEN 1 ELSE 0 END) AS right_swipes,
        SUM(CASE WHEN liked = FALSE THEN 1 ELSE 0 END) AS left_swipes,
        ROUND(
            SUM(CASE WHEN liked = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        ) AS like_rate_percent
    FROM swipes
    WHERE user_id = p_user_id;

    -- Order Stats
    SELECT 
        COUNT(*) AS total_orders,
        SUM(subtotal) AS total_spent,
        AVG(subtotal) AS avg_order_value,
        MAX(created_at) AS last_order_date
    FROM orders
    WHERE user_id = p_user_id;

    -- Top Categories
    SELECT 
        c.name,
        ps.score
    FROM preference_scores ps
    JOIN categories c ON ps.category_id = c.category_id
    WHERE ps.user_id = p_user_id
    ORDER BY ps.score DESC
    LIMIT 5;

END $$

DELIMITER ;

-- ============================================
-- PROCEDURE: get_trending_products
-- Purpose:
-- Most liked products in last N days
-- ============================================
DROP PROCEDURE IF EXISTS get_trending_products;

DELIMITER $$

CREATE PROCEDURE get_trending_products(
    IN p_days INT,
    IN p_limit INT
)
BEGIN
    SELECT 
        p.product_id,
        p.name,
        COUNT(*) AS total_swipes,
        SUM(CASE WHEN s.liked = TRUE THEN 1 ELSE 0 END) AS total_likes,
        ROUND(
            SUM(CASE WHEN s.liked = TRUE THEN 1 ELSE 0 END) * 100.0 /
            NULLIF(COUNT(*), 0),
            2
        ) AS like_percentage
    FROM swipes s
    JOIN products p ON s.product_id = p.product_id
    WHERE s.swiped_at >= DATE_SUB(NOW(), INTERVAL p_days DAY)
    GROUP BY p.product_id
    ORDER BY total_likes DESC
    LIMIT p_limit;
END $$

DELIMITER ;