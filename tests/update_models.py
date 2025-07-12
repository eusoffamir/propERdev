#!/usr/bin/env python3
"""
Script to update all remaining models to use Flask-SQLAlchemy
"""

import os
import re

def update_model_file(file_path):
    """Update a model file to use Flask-SQLAlchemy"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace imports
    content = re.sub(
        r'from sqlalchemy import.*?\n',
        'from app.db import db\n',
        content, flags=re.DOTALL
    )
    
    content = re.sub(
        r'from sqlalchemy\.orm import.*?\n',
        '',
        content
    )
    
    content = re.sub(
        r'from app\.models\.base import Base',
        'from app.models.base import BaseModel',
        content
    )
    
    # Replace class inheritance
    content = re.sub(
        r'class (\w+)\(Base\):',
        r'class \1(BaseModel):',
        content
    )
    
    # Replace Column with db.Column
    content = re.sub(
        r'Column\(',
        'db.Column(db.',
        content
    )
    
    # Replace relationship with db.relationship
    content = re.sub(
        r'relationship\(',
        'db.relationship(',
        content
    )
    
    # Replace ForeignKey with db.ForeignKey
    content = re.sub(
        r'ForeignKey\(',
        'db.ForeignKey(',
        content
    )
    
    # Remove datetime imports if not needed
    if 'datetime' in content and 'datetime.utcnow' not in content:
        content = re.sub(
            r'from datetime import datetime\n',
            '',
            content
        )
    
    # Remove created_at/updated_at columns since they're in BaseModel
    content = re.sub(
        r'    created_at = db\.Column\(db\.DateTime, default=.*?\n',
        '',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {file_path}")

def main():
    """Update all model files"""
    
    models_dir = "app/models"
    model_files = [
        "registration_requests.py",
        "properties.py", 
        "notifications.py",
        "ledger.py",
        "financial_reports.py",
        "ed_summary.py",
        "ed_closures.py",
        "commission_records.py",
        "activity_logs.py"
    ]
    
    for model_file in model_files:
        file_path = os.path.join(models_dir, model_file)
        if os.path.exists(file_path):
            update_model_file(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")

if __name__ == '__main__':
    main() 