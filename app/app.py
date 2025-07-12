from flask import Flask
from app.core.config import get_config_by_name
from app.core.db import init_db
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
        from app.core.db import db
        db.create_all()
    
    # CONTEXT PROCESSOR: Inject user_name, user_role, and avatar_url into all templates
    @app.context_processor
    def inject_user_info():
        from flask import session, url_for
        import os
        user_id = session.get('user_id')
        avatar_url = url_for('static', filename='default-avatar.jpg')
        if user_id:
            avatar_path = os.path.join(app.root_path, 'static', 'avatars', f'{user_id}.jpg')
            if os.path.exists(avatar_path):
                avatar_url = url_for('static', filename=f'avatars/{user_id}.jpg')
        return dict(user_name=session.get('user_name', ''), user_role=session.get('role', ''), avatar_url=avatar_url)
    
    return app

