# models/cases.py

from app.db import db
from app.models.base import BaseModel

class Case(BaseModel):
    __tablename__ = 'cases'

    case_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    leader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    case_no = db.Column(db.String(100))
    invoice_no = db.Column(db.String(100))
    eform_id = db.Column(db.String(100))
    property_address = db.Column(db.String(255))

    purchase_price = db.Column(db.Float)
    fee_pct = db.Column(db.Float)
    commission_pct = db.Column(db.Float)
    commission_total = db.Column(db.Float)
    override_leader_amt = db.Column(db.Float)
    override_hoa_amt = db.Column(db.Float)
    profit_proper = db.Column(db.Float)
    ed_paid = db.Column(db.Float)
    ed_pending = db.Column(db.String(100))
    tax = db.Column(db.Float)
    total_amount = db.Column(db.Float)

    reference_no = db.Column(db.String(100))
    registration_no = db.Column(db.String(100))
    mode_of_payment = db.Column(db.String(100))
    in_part_payment_of = db.Column(db.String(100))

    description = db.Column(db.Text)
    case_details = db.Column(db.Text)

    payment_status = db.Column(db.String(50))
    case_status = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    client = db.relationship("Client")
    agent = db.relationship("User", foreign_keys=[agent_id])
    leader = db.relationship("User", foreign_keys=[leader_id])
