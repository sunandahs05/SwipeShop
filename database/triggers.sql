DROP TRIGGER IF EXISTS trg_update_preference;

DELIMITER $$

CREATE TRIGGER trg_update_preference
AFTER INSERT ON swipes
FOR EACH ROW
BEGIN
    DECLARE v_category_id INT;

    -- Get category of product
    SELECT category_id INTO v_category_id
    FROM products
    WHERE product_id = NEW.product_id;

    INSERT INTO preference_scores(user_id, category_id, score)
    VALUES(
        NEW.user_id,
        v_category_id,
        CASE WHEN NEW.liked THEN 1.0 ELSE 0 END
    )
    ON DUPLICATE KEY UPDATE
        score = GREATEST(
            0,
            score + CASE WHEN NEW.liked THEN 1.0 ELSE -0.5 END
        );
END $$

DELIMITER ;

DROP TRIGGER IF EXISTS trg_update_avg_rating;

DELIMITER $$

CREATE TRIGGER trg_update_avg_rating
AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    UPDATE products
    SET avg_rating = (
        SELECT ROUND(AVG(rating), 2)
        FROM reviews
        WHERE product_id = NEW.product_id
    )
    WHERE product_id = NEW.product_id;
END $$

DELIMITER ;

DROP TRIGGER IF EXISTS trg_deduct_stock;

DELIMITER $$

CREATE TRIGGER trg_deduct_stock
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    -- Deduct stock
    UPDATE products
    SET stock = stock - NEW.quantity
    WHERE product_id = NEW.product_id;

    -- Update user total_spent
    UPDATE users u
    JOIN orders o ON u.user_id = o.user_id
    SET u.total_spent = u.total_spent + NEW.line_total
    WHERE o.order_id = NEW.order_id;
END $$

DELIMITER ;

