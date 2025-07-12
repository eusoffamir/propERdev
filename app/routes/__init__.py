from .auth import auth_bp
from .root import root_bp
from .dashboard import dashboard_bp
from .cases import cases_bp
from .users import users_bp
from .reports import reports_bp
from .settings import settings_bp
from .admin import admin_bp

def register_routes(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(root_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
