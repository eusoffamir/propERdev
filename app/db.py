from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create SQLAlchemy instance
db = SQLAlchemy()

# Create Migrate instance
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import all models to ensure they are registered
    from app.models import (
        User, Role, Client, Case, Invoice, CompanySetting,
        RegistrationRequest, EDClosure, EDSummary, Ledger,
        CommissionRecord, ActivityLog, Notification, Property, FinancialReport
    )
    
    return db

def create_tables():
    """Create all database tables"""
    with db.app.app_context():
        db.create_all()
        print("✅ Database tables created successfully.")

def drop_tables():
    """Drop all database tables"""
    with db.app.app_context():
        db.drop_all()
        print("🗑️ Database tables dropped successfully.")
