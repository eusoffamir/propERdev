from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from app.utils.db import get_db
from app.utils.auth import login_required, leader_required
import io
import pdfkit

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    """Main reports page with role-based access"""
    user_role = session.get('role')
    team = session.get('team')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if user_role == 'Admin':
        # Admin sees all data
        cur.execute("SELECT * FROM cases ORDER BY date_created DESC")
        cases = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE role = 'Agent'")
        agents = cur.fetchall()
    elif user_role == 'Leader':
        # Leader sees team data
        cur.execute("SELECT user_id FROM users WHERE team = %s AND role = 'Agent'", (team,))
        team_agent_ids = [row['user_id'] for row in cur.fetchall()]
        
        if team_agent_ids:
            format_ids = ','.join(['%s'] * len(team_agent_ids))
            cur.execute(f"SELECT * FROM cases WHERE agent_id IN ({format_ids}) ORDER BY date_created DESC", team_agent_ids)
            cases = cur.fetchall()
            cur.execute(f"SELECT * FROM users WHERE user_id IN ({format_ids})", team_agent_ids)
            agents = cur.fetchall()
        else:
            cases = []
            agents = []
    else:
        # Agent sees only their data
        user_id = session.get('user_id')
        cur.execute("SELECT * FROM cases WHERE agent_id = %s ORDER BY date_created DESC", (user_id,))
        cases = cur.fetchall()
        agents = []

    # Calculate summary statistics
    total_revenue = sum(c['total_amount'] or 0 for c in cases)
    total_cases = len(cases)
    avg_case_value = total_revenue / total_cases if total_cases > 0 else 0

    # Monthly breakdown
    now = datetime.now()
    monthly_data = []
    for i in range(6):
        month = (now - timedelta(days=30 * i)).strftime('%Y-%m')
        month_cases = [c for c in cases if c['date_created'].startswith(month)]
        month_revenue = sum(c['total_amount'] or 0 for c in month_cases)
        monthly_data.append({
            'month': month,
            'cases': len(month_cases),
            'revenue': month_revenue
        })
    monthly_data.reverse()

    cur.close()
    conn.close()

    return render_template('reports/reports.html', 
                         cases=cases, 
                         agents=agents, 
                         total_revenue=total_revenue,
                         total_cases=total_cases,
                         avg_case_value=avg_case_value,
                         monthly_data=monthly_data,
                         user_role=user_role)

@reports_bp.route('/reports/download')
@login_required
def download_report_pdf():
    """Download financial report as PDF"""
    user_role = session.get('role')
    team = session.get('team')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if user_role == 'Admin':
        cur.execute("SELECT * FROM cases ORDER BY date_created DESC")
        cases = cur.fetchall()
        report_title = "Company Financial Report"
    elif user_role == 'Leader':
        cur.execute("SELECT user_id FROM users WHERE team = %s AND role = 'Agent'", (team,))
        team_agent_ids = [row['user_id'] for row in cur.fetchall()]
        
        if team_agent_ids:
            format_ids = ','.join(['%s'] * len(team_agent_ids))
            cur.execute(f"SELECT * FROM cases WHERE agent_id IN ({format_ids}) ORDER BY date_created DESC", team_agent_ids)
            cases = cur.fetchall()
        else:
            cases = []
        report_title = f"Team {team} Financial Report"
    else:
        user_id = session.get('user_id')
        cur.execute("SELECT * FROM cases WHERE agent_id = %s ORDER BY date_created DESC", (user_id,))
        cases = cur.fetchall()
        report_title = "Personal Financial Report"

    # Calculate report data
    total_revenue = sum(c['total_amount'] or 0 for c in cases)
    total_cases = len(cases)
    avg_case_value = total_revenue / total_cases if total_cases > 0 else 0

    # Generate PDF
    html_content = render_template('reports/report_pdf.html',
                                 cases=cases,
                                 total_revenue=total_revenue,
                                 total_cases=total_cases,
                                 avg_case_value=avg_case_value,
                                 report_title=report_title,
                                 generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    try:
        # Generate PDF using pdfkit
        pdf_content = pdfkit.from_string(html_content, False, options={'encoding': 'UTF-8'})
        if not isinstance(pdf_content, (bytes, bytearray)):
            raise ValueError('PDF generation failed: pdfkit did not return bytes.')
        # Create file-like object
        pdf_buffer = io.BytesIO(pdf_content)
        pdf_buffer.seek(0)
        cur.close()
        conn.close()
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        cur.close()
        conn.close()
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('reports.index'))
