from flask import Blueprint, request, session, jsonify
from db import get_db_connection
from utils.auth_utils import hash_password,check_password

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = hash_password(data.get("password", "")).decode('utf-8')
        cursor.execute("""
            INSERT INTO users(name, email, password_hash, role)
            VALUES(%s, %s, %s, %s)
            """, (data.get("name"), data.get("email"), hashed_pw, "buyer"))
        conn.commit()
        return jsonify({"message": "User registered"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users WHERE email=%s
    """, (data.get("email"),))

    user = cursor.fetchone()

    password = data.get("password", "")
    if user and check_password(password, user["password_hash"]):
        session["user_id"] = user["user_id"]
        session["role"] = user["role"]
        return jsonify({"message": "Login success", "user_id": user["user_id"]})

    return jsonify({"error": "Invalid credentials"}), 401
