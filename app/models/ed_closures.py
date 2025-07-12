# models/ed_closures.py

from app.db import db
from app.models.base import BaseModel

class EDClosure(BaseModel):
    __tablename__ = 'ed_closures'

    closure_id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    team = db.Column(db.String(100))
    ren_no = db.Column(db.String(50))
    case_no = db.Column(db.String(100))

    purchase_price = db.Column(db.Float)
    total_ed = db.Column(db.Float)        # 3.24% of purchase price
    ed_converted = db.Column(db.Float)    # Converted to commission
    commission_agent = db.Column(db.Float)
    remarks = db.Column(db.String(255))

    agent = db.relationship("User")
