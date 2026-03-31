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


# GET LIKED PRODUCTS
@swipe_bp.route("/api/liked", methods=["GET"])
def get_liked_products():
    """
    Returns all products that the user has liked (swiped right on).
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.callproc("get_liked_products", (user_id,))

        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


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
    cursor = conn.cursor(dictionary=True)

    try:
        product_id = data.get("product_id")
        liked = data.get("liked")

        # Insert swipe
        cursor.execute("""
            INSERT INTO swipes(user_id, product_id, liked)
            VALUES(%s, %s, %s)
        """, (user_id, product_id, liked))

        # If liked, update user preferences
        if liked:
            # Get product's category
            cursor.execute("""
                SELECT category_id FROM products WHERE product_id = %s
            """, (product_id,))
            
            result = cursor.fetchone()
            if result:
                category_id = result['category_id']
                # Update preference score
                cursor.callproc("update_preference_scores", (user_id, category_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Swipe recorded", "liked": bool(liked)})


# UNLIKE PRODUCT (Remove from liked)
@swipe_bp.route("/api/unlike", methods=["POST"])
def unlike():
    """
    Removes a product from the user's liked list by deleting the swipe.
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or request.form
    product_id = data.get("product_id") if data else None

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM swipes
            WHERE user_id = %s AND product_id = %s AND liked = TRUE
        """, (user_id, product_id))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Product was not in likes"}), 200

        return jsonify({"message": "Product removed from likes"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# GET USER INTERESTS
@swipe_bp.route("/api/user-interests", methods=["GET"])
def get_user_interests():
    """
    Returns the user's category interests based on their liked swipes.
    Shows which categories they prefer most.
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.callproc("get_user_interests", (user_id,))

        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()