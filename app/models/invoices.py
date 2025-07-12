# models/invoices.py

from app.db import db
from app.models.base import BaseModel

class Invoice(BaseModel):
    __tablename__ = 'invoices'

    invoice_id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.case_id'))
    invoice_no = db.Column(db.String(100), unique=True)
    invoice_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    tax_amount = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(50), default='pending')
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)

    case = db.relationship("Case")
