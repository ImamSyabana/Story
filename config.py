import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SQLALCHEMY_DATABASE_URI= os.getenv('DB_URL', 'postgresql://neondb_owner:npg_Sr84UkmbJvWH@ep-misty-shape-aduutejd-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False