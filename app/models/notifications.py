# models/notifications.py

from app.db import db
from datetime import datetime
from app.models.base import BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
