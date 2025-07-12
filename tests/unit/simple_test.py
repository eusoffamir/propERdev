#!/usr/bin/env python3
"""
Simple test script to verify database setup
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_setup():
    """Test basic database setup"""
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:proper123@localhost:5432/propdb'
    
    try:
        print("🔍 Testing basic imports...")
        
        # Test Flask import
        from flask import Flask
        print("✅ Flask import successful")
        
        # Test SQLAlchemy import
        from flask_sqlalchemy import SQLAlchemy
        print("✅ Flask-SQLAlchemy import successful")
        
        # Test Flask-Migrate import
        from flask_migrate import Migrate
        print("✅ Flask-Migrate import successful")
        
        # Test app creation
        from app import create_app
        print("✅ App creation successful")
        
        # Test database initialization
        from app.db import db
        print("✅ Database instance created")
        
        # Create app
        app = create_app('development')
        print("✅ Flask app created successfully")
        
        with app.app_context():
            # Test database connection using session
            with db.session.begin():
                result = db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            
            # Test model imports
            from app.models import User, Role, CompanySetting
            print("✅ Model imports successful")
            
            # Test table creation
            db.create_all()
            print("✅ Tables created successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 Simple Database Test")
    print("=" * 30)
    
    success = test_basic_setup()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 All tests passed! Database setup is working.")
    else:
        print("❌ Tests failed. Please check the errors above.") 