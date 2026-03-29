from flask import Blueprint, request, jsonify, session
from db import get_db_connection

order_bp = Blueprint("order", __name__)

@order_bp.route("/api/checkout", methods=["POST"])
def checkout():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    address_id = data.get("address_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.callproc("checkout_cart", (user_id, address_id))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Order placed successfully"})