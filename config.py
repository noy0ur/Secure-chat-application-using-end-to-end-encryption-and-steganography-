import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    DATABASE = os.path.join(BASE_DIR, "instance", "database.db")