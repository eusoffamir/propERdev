# models/registration_requests.py

from app.db import db
from datetime import datetime
from app.models.base import BaseModel

class RegistrationRequest(BaseModel):
    __tablename__ = 'registration_requests'

    request_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    team = db.Column(db.String(100))
    role = db.Column(db.String(50))
    password_hash = db.Column(db.String(255))
    nric = db.Column(db.String(20))
    dob = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
