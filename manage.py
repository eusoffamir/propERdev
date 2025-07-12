#!/usr/bin/env python3
"""
Flask CLI management script for propER system
Provides commands for database operations and application tasks
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Set up environment variables"""
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('SECRET_KEY', 'your-secret-key-change-this-in-production')
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:proper123@localhost:5432/propdb')

def init_db():
    """Initialize the database with tables and seed data"""
    setup_environment()
    
    try:
        from app import create_app
        from app.db import db
        from werkzeug.security import generate_password_hash
        
        app = create_app('development')
        
        with app.app_context():
            print("🗄️ Initializing database...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully.")
            
            # Import models after db is initialized
            from app.models import User, Role, CompanySetting
            
            # Create roles
            roles_data = [
                {'name': 'Admin', 'description': 'System Administrator'},
                {'name': 'Leader', 'description': 'Team Leader'},
                {'name': 'Agent', 'description': 'Property Agent'}
            ]
            
            for role_data in roles_data:
                role = Role.query.filter_by(name=role_data['name']).first()
                if not role:
                    role = Role(**role_data)
                    db.session.add(role)
            
            db.session.commit()
            print("✅ Roles created/updated")
            
            # Create default users
            admin_role = Role.query.filter_by(name='Admin').first()
            leader_role = Role.query.filter_by(name='Leader').first()
            agent_role = Role.query.filter_by(name='Agent').first()
            
            # Admin user
            if not User.query.filter_by(email='eusoff@proper.com').first():
                admin_user = User(
                    name='Eusoff',
                    email='eusoff@proper.com',
                    password_hash=generate_password_hash('eusoff'),
                    role_id=admin_role.role_id,
                    team='Admin',
                    phone='+60123456789',
                    status='active'
                )
                db.session.add(admin_user)
                print("✅ Default admin user created")
            
            # Leader user
            if not User.query.filter_by(email='azimi@proper.com').first():
                leader_user = User(
                    name='Azimi',
                    email='azimi@proper.com',
                    password_hash=generate_password_hash('azimi'),
                    role_id=leader_role.role_id,
                    team='Team A',
                    phone='+60123456788',
                    status='active'
                )
                db.session.add(leader_user)
                print("✅ Default leader user created")
            
            # Agent user
            if not User.query.filter_by(email='mizan@proper.com').first():
                agent_user = User(
                    name='Mizan',
                    email='mizan@proper.com',
                    password_hash=generate_password_hash('mizan'),
                    role_id=agent_role.role_id,
                    team='Team A',
                    phone='+60123456787',
                    status='active'
                )
                db.session.add(agent_user)
                print("✅ Default agent user created")
            
            db.session.commit()
            
            # Create company settings
            if not CompanySetting.query.first():
                company_settings = CompanySetting(
                    company_name='MOHD ANUAR & CO.',
                    address='123 Business Street, Kuala Lumpur, Malaysia',
                    phone='+603-1234-5678',
                    email='info@mohdanuar.com',
                    website='www.mohdanuar.com',
                    registration_no='REG123456',
                    gst_no='GST123456789'
                )
                db.session.add(company_settings)
                db.session.commit()
                print("✅ Company settings created")
            
            print("🎉 Database initialization completed!")
            print("\n📋 Default login credentials:")
            print("Admin:  eusoff@proper.com / eusoff")
            print("Leader: azimi@proper.com  / azimi")
            print("Agent:  mizan@proper.com  / mizan")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

def seed_data():
    """Seed the database with initial data"""
    init_db()

def drop_db():
    """Drop all database tables"""
    setup_environment()
    
    try:
        from app import create_app
        from app.db import db
        
        app = create_app('development')
        
        with app.app_context():
            db.drop_all()
            print("🗑️ Database tables dropped successfully.")
            
    except Exception as e:
        print(f"❌ Error dropping database: {e}")

def create_user():
    """Create a new user interactively"""
    setup_environment()
    
    try:
        from app import create_app
        from app.db import db
        from app.models import User, Role
        from werkzeug.security import generate_password_hash
        
        app = create_app('development')
        
        with app.app_context():
            name = input("Enter user name: ")
            email = input("Enter email: ")
            password = input("Enter password: ")
            role_name = input("Enter role (Admin/Leader/Agent): ")
            team = input("Enter team: ")
            
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                print(f"❌ Role '{role_name}' not found!")
                return
            
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                role_id=role.role_id,
                team=team,
                status='active'
            )
            
            db.session.add(user)
            db.session.commit()
            print(f"✅ User '{name}' created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands:")
        print("  init-db     - Initialize database with tables and seed data")
        print("  seed-data   - Seed data only")
        print("  drop-db     - Drop all database tables")
        print("  create-user - Create a new user interactively")
        return
    
    command = sys.argv[1]
    
    if command == "init-db":
        init_db()
    elif command == "seed-data":
        seed_data()
    elif command == "drop-db":
        drop_db()
    elif command == "create-user":
        create_user()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main() 