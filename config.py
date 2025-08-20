import os

class Config:
    SECRET_KEY = os.getenv("FLASK_KEY", os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False