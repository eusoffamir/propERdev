#!/usr/bin/env python3
"""
Database initialization script for propER system
This script sets up the database, creates tables, and seeds initial data
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.db import db
from app.models import *
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize the database with tables and seed data"""
    app = create_app('development')
    
    with app.app_context():
        print("🗄️ Initializing database...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully.")
        
        # Seed initial data
        seed_initial_data()
        print("✅ Initial data seeded successfully.")
        
        print("🎉 Database initialization completed!")

def seed_initial_data():
    """Seed the database with initial data"""
    
    # Create roles
    roles = [
        {'name': 'Admin', 'description': 'System Administrator'},
        {'name': 'Leader', 'description': 'Team Leader'},
        {'name': 'Agent', 'description': 'Property Agent'}
    ]
    
    for role_data in roles:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
    
    db.session.commit()
    print("✅ Roles created/updated")
    
    # Create default admin user
    admin_role = Role.query.filter_by(name='Admin').first()
    admin_user = User.query.filter_by(email='eusoff@proper.com').first()
    
    if not admin_user:
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
        db.session.commit()
        print("✅ Default admin user created")
    
    # Create default leader user
    leader_role = Role.query.filter_by(name='Leader').first()
    leader_user = User.query.filter_by(email='azimi@proper.com').first()
    
    if not leader_user:
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
        db.session.commit()
        print("✅ Default leader user created")
    
    # Create default agent user
    agent_role = Role.query.filter_by(name='Agent').first()
    agent_user = User.query.filter_by(email='mizan@proper.com').first()
    
    if not agent_user:
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
        db.session.commit()
        print("✅ Default agent user created")
    
    # Create company settings
    company_settings = CompanySetting.query.first()
    if not company_settings:
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

if __name__ == '__main__':
    init_database() 