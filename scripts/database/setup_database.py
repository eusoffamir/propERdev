#!/usr/bin/env python3
"""
Simple database setup script for propER system
This script sets up the database and creates initial data
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_database():
    """Set up the database with initial configuration"""
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:proper123@localhost:5432/propdb'
    
    try:
        from app import create_app
        from app.db import db
        from app.models import User, Role, CompanySetting
        from werkzeug.security import generate_password_hash
        
        app = create_app('development')
        
        with app.app_context():
            print("🗄️ Initializing database...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully.")
            
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
            
            print("🎉 Database setup completed successfully!")
            print("\n📋 Default login credentials:")
            print("Admin:  eusoff@proper.com / eusoff")
            print("Leader: azimi@proper.com  / azimi")
            print("Agent:  mizan@proper.com  / mizan")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == '__main__':
    setup_database() 