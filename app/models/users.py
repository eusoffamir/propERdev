# models/users.py

from app.db import db
from app.models.base import BaseModel
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    role = db.relationship("Role", backref="users")
    team = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    ren_no = db.Column(db.String(50))
    nric = db.Column(db.String(20))
    tiering_pct = db.Column(db.Float)
    position = db.Column(db.String(100))
    notes = db.Column(db.String(255))
    expiry_year = db.Column(db.Integer)
    registration_fee_paid = db.Column(db.Boolean, default=False)
    
    # Kit info
    kit_bag = db.Column(db.Boolean, default=False)
    kit_black_file = db.Column(db.Boolean, default=False)
    kit_lanyard = db.Column(db.Boolean, default=False)
    kit_tg_id = db.Column(db.String(100))
    kit_biz_card = db.Column(db.Boolean, default=False)
    kit_tshirt = db.Column(db.Boolean, default=False)
    kit_remarks = db.Column(db.String(255))

    # Bank
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(100))

    status = db.Column(db.String(50), default='active')
    added_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # self-reference
    reset_token = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)

    # Relationship: self
    added_by_user = db.relationship("User", remote_side=[user_id])
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role and self.role.name.lower() in ['admin', 'administrator']
