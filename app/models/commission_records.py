# models/commission_records.py

from app.db import db
from app.models.base import BaseModel

class CommissionRecord(BaseModel):
    __tablename__ = 'commission_records'

    record_id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.case_id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    team = db.Column(db.String(100))
    account_no = db.Column(db.String(100))
    commission_total = db.Column(db.Float)
    fifty_pct = db.Column(db.Float)
    coa_deduction = db.Column(db.Float)
    commission_agent_rm = db.Column(db.Float)
    agent_pct = db.Column(db.Float)
    team_leader_pct = db.Column(db.Float)
    team_leader_rm = db.Column(db.Float)
    hoa_pct = db.Column(db.Float)
    hoa_rm = db.Column(db.Float)
    proper_pct = db.Column(db.String(50))
    proper_rm = db.Column(db.Float)
    claim_date = db.Column(db.Date)
    payment_status = db.Column(db.String(50), default='Pending')
    payment_date = db.Column(db.Date)

    # Relationships
    case = db.relationship("Case")
    agent = db.relationship("User")
