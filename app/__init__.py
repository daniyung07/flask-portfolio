# app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

# Define the base directory for file paths
basedir = os.path.abspath(os.path.dirname(__file__))

# Create the database instance globally
db = SQLAlchemy()


# Define the User Model (placed here for simple imports in our app size)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    # It's best practice to hash this password!
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email_address}')"


# app/__init__.py (inside Portfolio class)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)  # Increased length for description
    link = db.Column(db.String(100), nullable=False)
    # NEW COLUMN for filtering
    category = db.Column(db.String(50), nullable=False, default='General')

    def __repr__(self):
        return f"Portfolio('{self.title}', '{self.category}')"

def create_app():
    # Create the Flask application instance
    app = Flask(__name__)

    # Application Configuration
    app.config['SECRET_KEY'] = 'PASTE_YOUR_LONG_RANDOM_KEY_HERE'  # RETAIN YOUR LONG KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize extensions with the app
    db.init_app(app)

    # === Blueprint Registration ===
    # Import the blueprint from the routes module
    from .routes import main
    app.register_blueprint(main)
    # ==============================



    # Important: Return the created app object
    return app

