import os

class Config:
    SECRET_KEY = os.getenv("FLASK_KEY", os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL', 'postgres://neondb_owner:npg_0nqtbHFOEG7P@ep-morning-queen-adhe20kk-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False