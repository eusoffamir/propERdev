# models/base.py

from app.db import db

class BaseModel(db.Model):
    """Base model class that includes common fields"""
    __abstract__ = True
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
