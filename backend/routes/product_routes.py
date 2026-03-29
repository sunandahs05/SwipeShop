from flask import Blueprint, request, jsonify
from db import get_db_connection

product_bp = Blueprint("product", __name__)

@product_bp.route("/api/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    return jsonify(products)