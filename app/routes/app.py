from flask import Flask
from app.core.config import get_config_by_name
from app.core.db import db
from app.routes import register_routes

def create_app(config_name='development') -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config_by_name(config_name))

    # DB
    db.init_app(app)

    # ROUTES
    register_routes(app)

    return app
