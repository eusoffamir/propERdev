# app/models/roles.py

from app.db import db
from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = 'roles'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
