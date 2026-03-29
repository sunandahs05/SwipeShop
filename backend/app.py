from flask import Flask
from flask_session import Session
from flask_cors import CORS
from config import SECRET_KEY

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
@app.route("/")
def home():
    return "SwipeShop Backend Running!"
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
