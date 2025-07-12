# models/ed_summary.py

from app.db import db
from app.models.base import BaseModel

class EDSummary(BaseModel):
    __tablename__ = 'ed_summary'

    summary_id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    team = db.Column(db.String(100))
    ren_no = db.Column(db.String(50))

    total_closer = db.Column(db.Float)
    total_ed_claimed = db.Column(db.Float)
    quarter = db.Column(db.String(20))  # e.g. Q1 2025

    is_top_closer = db.Column(db.Boolean, default=False)
    is_top_active_player = db.Column(db.Boolean, default=False)
