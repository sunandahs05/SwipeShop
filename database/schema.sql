-- ============================================
-- SwipeShop - Complete DDL (MySQL 8.0)
-- ============================================

DROP DATABASE IF EXISTS swipeshop;
CREATE DATABASE swipeshop;
USE swipeshop;

-- ============================================
-- TABLE: users
-- Stores all users (buyer/seller/admin)
-- total_spent is maintained via triggers
-- Soft delete via is_active
-- ============================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('buyer','seller','admin') NOT NULL DEFAULT 'buyer',
    total_spent DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: addresses
-- Each user can have multiple addresses
-- Deleted automatically if user is deleted
-- ============================================
CREATE TABLE addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    line1 VARCHAR(255) NOT NULL,
    line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_addresses_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================
-- TABLE: categories
-- Self-referencing hierarchy (parent-child)
-- ON DELETE SET NULL ensures safe hierarchy removal
-- ============================================
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ============================================
-- TABLE: products
-- Listed by sellers; belongs to one category
-- avg_rating updated via triggers
-- Soft delete via is_active
-- ============================================
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock INT NOT NULL CHECK (stock >= 0),
    avg_rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_products_seller (seller_id),
    INDEX idx_products_category (category_id),

    CONSTRAINT fk_products_seller
        FOREIGN KEY (seller_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================
-- TABLE: swipes
-- Logs user swipe behavior (like/skip)
-- Used for recommendation system
-- ============================================
CREATE TABLE swipes (
    swipe_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    liked BOOLEAN NOT NULL,
    swiped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_swipes_user_product (user_id, product_id),

    CONSTRAINT fk_swipes_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_swipes_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

-- ============================================
-- TABLE: preference_scores
-- M:N resolution between users and categories
-- Maintains user preference score per category
-- ============================================
CREATE TABLE preference_scores (
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    score DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    PRIMARY KEY (user_id, category_id),

    CONSTRAINT fk_pref_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_pref_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE CASCADE
);

-- ============================================
-- TABLE: cart
-- Each user has exactly one cart
-- ============================================
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cart_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- ============================================
-- TABLE: cart_items
-- Stores items inside cart
-- ============================================
CREATE TABLE cart_items (
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),

    PRIMARY KEY (cart_id, product_id),

    FOREIGN KEY (cart_id)
        REFERENCES cart(cart_id)
        ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

-- ============================================
-- TABLE: orders
-- Stores finalized orders
-- subtotal derived from order_items
-- status used as soft-state tracking
-- ============================================
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    address_id INT NOT NULL,
    status ENUM('pending','paid','shipped','delivered','cancelled') 
        NOT NULL DEFAULT 'pending',
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_orders_user (user_id),

    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_orders_address
        FOREIGN KEY (address_id)
        REFERENCES addresses(address_id)
        ON DELETE RESTRICT
);

-- ============================================
-- TABLE: order_items (Weak Entity)
-- Composite PK ensures no duplicate product per order
-- price_at_purchase freezes price
-- ============================================
CREATE TABLE order_items (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_purchase DECIMAL(10,2) NOT NULL CHECK (price_at_purchase > 0),
    line_total DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    PRIMARY KEY (order_id, product_id),

    INDEX idx_order_items_product (product_id),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE RESTRICT
);

-- ============================================
-- TABLE: reviews
-- Only verified purchases allowed
-- Enforced via (user_id, product_id, order_id)
-- Prevents duplicate reviews
-- ============================================
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_review (user_id, product_id, order_id),

    INDEX idx_reviews_product (product_id),

    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE
);

