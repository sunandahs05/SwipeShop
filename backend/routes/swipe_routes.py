from flask import Blueprint, request, jsonify, session
from db import get_db_connection

swipe_bp = Blueprint("swipe", __name__)

# GET FEED
@swipe_bp.route("/api/feed", methods=["GET"])
def get_feed():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.callproc("get_personalized_feed", (user_id, 10))

    results = []
    for result in cursor.stored_results():
        results = result.fetchall()

    return jsonify(results)


# SWIPE ACTION
@swipe_bp.route("/api/swipe", methods=["POST"])
def swipe():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO swipes(user_id, product_id, liked)
            VALUES(%s, %s, %s)
        """, (user_id, data.get("product_id"), data.get("liked")))

        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Swipe recorded"})