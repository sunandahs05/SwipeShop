from flask import Blueprint, request, jsonify, session
from db import get_db_connection

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # get cart_id safely
        cursor.execute("SELECT cart_id FROM cart WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Cart not found for user"}), 404
        cart_id = result[0]

        cursor.execute("""
            INSERT INTO cart_items(cart_id, product_id, quantity)
            VALUES(%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (cart_id, data.get("product_id"), data.get("qty"), data.get("qty")))

        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Added to cart"})