from flask import Flask
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv, find_dotenv
from markupsafe import Markup
from flask_migrate import Migrate
from config import Config
import logging

# Find and load environment variables from .env file
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# Create the Flask app instance
app = Flask(__name__)
# Configure the app
app.config.from_object(Config)


db = SQLAlchemy(app)

migrate = Migrate(app, db)

from app import routes, models


# Initialize extensions
ckeditor = CKEditor(app)
Bootstrap(app)
db.init_app(app)


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Create gravatar instance
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Import routes and models at the end to avoid circular imports
from app import routes, models

# Create all database tables
with app.app_context():
    db.create_all()

# Setup console logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Flask App startup')