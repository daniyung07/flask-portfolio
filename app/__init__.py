import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, \
    check_password_hash  # Though used in routes, good to have available

# Define the base directory (Important for paths)
basedir = os.path.abspath(os.path.dirname(__file__))

# Create the database instance globally
db = SQLAlchemy()


# --- MODEL DEFINITIONS ---
# Models must be defined or imported where db is created.

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    # Increased length to safely store the password hash
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email_address}')"


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')

    def __repr__(self):
        return f"Portfolio('{self.title}', '{self.category}')"


# --- APPLICATION FACTORY ---

def create_app():
    # Create the Flask application instance
    app = Flask(__name__)

    # Application Configuration
    # NOTE: SECRET_KEY should be set via environment variable on Render!
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Simple path for SQLite deployment
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # User Loader function: tells Flask-Login how to find a user by their ID
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # === CRITICAL FIX: AUTOMATED DB CREATION ===
    # This ensures the tables exist when the app starts up on the server
    with app.app_context():
        db.create_all()
        # ============================================

    # Blueprint Registration
    from .routes import main
    app.register_blueprint(main)

    return app