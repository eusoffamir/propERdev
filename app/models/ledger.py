# models/ledger.py

from app.db import db
from app.models.base import BaseModel

class Ledger(BaseModel):
    __tablename__ = 'ledger'

    ledger_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id'))
    amount_paid = db.Column(db.Float)
    date_paid = db.Column(db.String(50))  # You can change to DateTime if needed
    payment_method = db.Column(db.String(50))
    payment_note = db.Column(db.String(255))
    file_reference_no = db.Column(db.String(100))
    in_part_payment_of = db.Column(db.String(100))
