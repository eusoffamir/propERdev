from flask import Flask
from app.config import get_config_by_name
from app.db import init_db
from app.routes import register_routes
from flask_login import LoginManager
from app.models.users import User

def create_app(config_name='development') -> Flask:
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config_by_name(config_name))
    
    # Initialize database
    init_db(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # type: ignore[attr-defined]
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register routes
    register_routes(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        from app.db import db
        db.create_all()
    
    return app

