#!/usr/bin/env python3
"""
Database connection test script for propER system
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_database_connection():
    """Test database connection and basic operations"""
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:proper123@localhost:5432/propdb'
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("🔍 Testing database connection...")
        
        # Test direct PostgreSQL connection
        conn = psycopg2.connect(
            dbname="propdb",
            user="postgres",
            password="proper123",
            host="localhost",
            port="5432"
        )
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test basic query
        cur.execute("SELECT version();")
        version = cur.fetchone()
        if version is not None and 'version' in version:
            print(f"✅ PostgreSQL version: {version['version']}")
        else:
            print("⚠️ Could not fetch PostgreSQL version.")
        
        # Check if tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        if tables:
            print("📋 Existing tables:")
            for table in tables:
                print(f"  - {table['table_name']}")
        else:
            print("📋 No tables found in database")
        
        cur.close()
        conn.close()
        
        print("✅ Database connection test successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Install psycopg2: pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check database credentials")
        print("3. Verify database 'propdb' exists")
        print("4. Check network connectivity")
        return False

def test_flask_sqlalchemy():
    """Test Flask-SQLAlchemy setup"""
    
    try:
        print("\n🔍 Testing Flask-SQLAlchemy setup...")
        
        from app import create_app
        from app.db import db
        
        app = create_app('development')
        
        with app.app_context():
            # Test database connection
            db.session.execute(db.text("SELECT 1"))
            print("✅ Flask-SQLAlchemy connection successful!")
            
            # Test model imports
            from app.models import User, Role, Case
            print("✅ Model imports successful!")
            
            return True
            
    except Exception as e:
        print(f"❌ Flask-SQLAlchemy test failed: {e}")
        return False

if __name__ == '__main__':
    print("🧪 propER Database Connection Test")
    print("=" * 40)
    
    # Test direct PostgreSQL connection
    db_test = test_database_connection()
    
    # Test Flask-SQLAlchemy
    flask_test = test_flask_sqlalchemy()
    
    print("\n" + "=" * 40)
    if db_test and flask_test:
        print("🎉 All tests passed! Database setup is ready.")
        print("\n📋 Next steps:")
        print("1. Run: python setup_database.py")
        print("2. Run: python run.py")
    else:
        print("❌ Some tests failed. Please check the errors above.") 