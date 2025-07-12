# models/company_settings.py

from app.core.db import db
from app.models.base import BaseModel

class CompanySetting(BaseModel):
    __tablename__ = 'company_settings'
    setting_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    registration_no = db.Column(db.String(100))
    gst_no = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(100))
