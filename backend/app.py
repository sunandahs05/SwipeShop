from flask import Flask
from flask_session import Session
from flask_cors import CORS
from config import SECRET_KEY

from flask import render_template

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app, supports_credentials=True)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# --- Frontend Routes ---
@app.route("/")
def home():
    return render_template("swipe_feed.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/feed")
def feed_page():
    return render_template("swipe_feed.html")

@app.route("/liked")
def liked_page():
    return render_template("liked.html")

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

@app.route("/orders")
def orders_page():
    return render_template("orders.html")

@app.route("/product")
def product_page():
    return render_template("product_detail.html")

@app.route("/seller/dashboard")
def seller_dashboard():
    return render_template("seller_dashboard.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/review/write")
def write_review():
    return render_template("write_review.html")
# Register routes
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.swipe_routes import swipe_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(swipe_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    print("Flask app starting...")
    app.run(debug=True, use_reloader=False)
