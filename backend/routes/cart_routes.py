from flask import Blueprint, request, jsonify, session
from db import get_db_connection

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/api/cart", methods=["GET"])
def get_cart():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if cart exists for user
        cursor.execute("SELECT cart_id FROM cart WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        # Auto-create cart if it doesn't exist
        if not result:
            cursor.execute("INSERT INTO cart(user_id) VALUES(%s)", (user_id,))
            conn.commit()
            cart_id = cursor.lastrowid
        else:
            cart_id = result['cart_id']
        
        # Get cart items for user
        cursor.execute("""
            SELECT 
                ci.product_id,
                ci.quantity,
                p.name,
                p.price,
                p.image_url
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.cart_id = %s
            ORDER BY ci.product_id
        """, (cart_id,))
        
        items = cursor.fetchall()
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@cart_bp.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if cart exists for user, create if not
        cursor.execute("SELECT cart_id FROM cart WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            # Create new cart
            cursor.execute("INSERT INTO cart(user_id) VALUES(%s)", (user_id,))
            conn.commit()
            # Fetch the newly created cart
            cursor.execute("SELECT cart_id FROM cart WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Failed to create cart for user"}), 500
        
        cart_id = result['cart_id']

        # Add item to cart
        cursor.execute("""
            INSERT INTO cart_items(cart_id, product_id, quantity)
            VALUES(%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (cart_id, data.get("product_id"), data.get("qty"), data.get("qty")))

        conn.commit()
        return jsonify({"message": "Added to cart"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()