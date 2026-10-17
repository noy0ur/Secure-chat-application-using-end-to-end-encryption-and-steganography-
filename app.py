from flask import Flask
from config import Config
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from database.models import create_tables
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Ensure folders exist
os.makedirs("instance", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

# Register routes
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

# Create tables
create_tables()

if __name__ == "__main__":
    app.run(debug=False)
