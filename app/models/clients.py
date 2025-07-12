# models/clients.py

from app.db import db
from app.models.base import BaseModel

class Client(BaseModel):
    __tablename__ = 'clients'

    client_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nric = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    creator = db.relationship("User")
