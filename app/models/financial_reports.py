# models/financial_reports.py

from app.db import db
from app.models.base import BaseModel

class FinancialReport(BaseModel):
    __tablename__ = 'financial_reports'

    report_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))            # e.g. 'P&L', 'Balance Sheet', 'Cash Flow'
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    data_json = db.Column(db.Text)             # Store structured JSON as text
