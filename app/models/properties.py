# models/properties.py

from app.db import db
from app.models.base import BaseModel

class Property(BaseModel):
    __tablename__ = 'properties'

    property_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))       # e.g. 'Condo', 'Landed', 'Commercial'
    location = db.Column(db.String(255))
    value = db.Column(db.Float)
    notes = db.Column(db.String(255))
