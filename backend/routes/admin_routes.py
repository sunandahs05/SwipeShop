from flask import Blueprint, jsonify, session
from db import get_db_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/sales-report", methods=["GET"])
def sales_report():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if session["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.callproc("get_sales_report", ("2024-01-01", "2025-01-01"))

    results = []
    for result in cursor.stored_results():
        results = result.fetchall()

    return jsonify(results)