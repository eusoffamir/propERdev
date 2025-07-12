# models/activity_logs.py

from app.core.db import db
from datetime import datetime
from app.models.base import BaseModel

class ActivityLog(BaseModel):
    __tablename__ = 'activity_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    action = db.Column(db.String(100))
    target_table = db.Column(db.String(100))
    target_id = db.Column(db.Integer)
    details = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
