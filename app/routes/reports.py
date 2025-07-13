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
    selected_month = request.args.get('month')
    chart_period = request.args.get('chart_period', 'monthly')  # Default to monthly

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Base query with JOIN to get agent names
    base_query = """
        SELECT c.*, u.name as agent_name 
        FROM cases c 
        LEFT JOIN users u ON c.agent_id = u.user_id 
        WHERE 1=1
    """
    params = []

    # Add month filter if selected
    if selected_month:
        base_query += " AND c.date_created LIKE %s"
        params.append(f"{selected_month}%")

    if user_role == 'Admin':
        # Admin sees all data
        pass
    elif user_role == 'Leader':
        # Leader sees team data
        cur.execute("SELECT user_id FROM users WHERE team = %s AND role = 'Agent'", (team,))
        team_agent_ids = [row['user_id'] for row in cur.fetchall()]
        
        if team_agent_ids:
            format_ids = ','.join(['%s'] * len(team_agent_ids))
            base_query += f" AND c.agent_id IN ({format_ids})"
            params.extend(team_agent_ids)
        else:
            # No team agents, return empty result
            cur.close()
            conn.close()
            return render_template('reports/reports.html', 
                                 reports=[],
                                 selected_month=selected_month,
                                 chart_labels=[],
                                 chart_amounts=[],
                                 user_role=user_role)
    else:
        # Agent sees only their data
        user_id = session.get('user_id')
        base_query += " AND c.agent_id = %s"
        params.append(user_id)

    base_query += " ORDER BY c.date_created DESC"
    
    cur.execute(base_query, params)
    reports = cur.fetchall()

    # Calculate summary statistics
    total_revenue = sum(r['total_amount'] or 0 for r in reports)
    total_cases = len(reports)
    avg_case_value = total_revenue / total_cases if total_cases > 0 else 0

    # Monthly breakdown for chart (last 6 months)
    now = datetime.now()
    monthly_data = []
    for i in range(6):
        month = (now - timedelta(days=30 * i)).strftime('%Y-%m')
        month_cases = [r for r in reports if r['date_created'] and r['date_created'].startswith(month)]
        month_revenue = sum(r['total_amount'] or 0 for r in month_cases)
        monthly_data.append({
            'month': month,
            'cases': len(month_cases),
            'revenue': month_revenue
        })
    monthly_data.reverse()

    # Chart data based on selected period
    chart_labels = []
    chart_amounts = []
    now = datetime.now()
    
    if chart_period == 'daily':
        # Last 30 days
        daily_revenue = {}
        for i in range(30):
            date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_revenue[date] = 0
        
        for r in reports:
            if r['date_created']:
                date = r['date_created'][:10]  # Get YYYY-MM-DD part
                if date in daily_revenue:
                    daily_revenue[date] += r['total_amount'] or 0
        
        sorted_dates = sorted(daily_revenue.items(), key=lambda x: x[0])[-30:]
        chart_labels = [date[0] for date in sorted_dates]
        chart_amounts = [date[1] for date in sorted_dates]
        
    elif chart_period == 'weekly':
        # Last 12 weeks
        weekly_revenue = {}
        for i in range(12):
            week_start = now - timedelta(weeks=i)
            week_key = week_start.strftime('%Y-W%U')
            weekly_revenue[week_key] = 0
        
        for r in reports:
            if r['date_created']:
                try:
                    date_obj = datetime.strptime(r['date_created'][:10], '%Y-%m-%d')
                    week_key = date_obj.strftime('%Y-W%U')
                    if week_key in weekly_revenue:
                        weekly_revenue[week_key] += r['total_amount'] or 0
                except:
                    pass
        
        sorted_weeks = sorted(weekly_revenue.items(), key=lambda x: x[0])[-12:]
        chart_labels = [week[0] for week in sorted_weeks]
        chart_amounts = [week[1] for week in sorted_weeks]
        
    elif chart_period == 'yearly':
        # Last 5 years
        yearly_revenue = {}
        for i in range(5):
            year = (now - timedelta(days=365*i)).strftime('%Y')
            yearly_revenue[year] = 0
        
        for r in reports:
            if r['date_created']:
                year = r['date_created'][:4]  # Get YYYY part
                if year in yearly_revenue:
                    yearly_revenue[year] += r['total_amount'] or 0
        
        sorted_years = sorted(yearly_revenue.items(), key=lambda x: x[0])[-5:]
        chart_labels = [year[0] for year in sorted_years]
        chart_amounts = [year[1] for year in sorted_years]
        
    else:  # monthly (default)
        # Last 6 months
        monthly_revenue = {}
        for i in range(6):
            month = (now - timedelta(days=30 * i)).strftime('%Y-%m')
            monthly_revenue[month] = 0
        
        for r in reports:
            if r['date_created']:
                month = r['date_created'][:7]  # Get YYYY-MM part
                if month in monthly_revenue:
                    monthly_revenue[month] += r['total_amount'] or 0
        
        sorted_months = sorted(monthly_revenue.items(), key=lambda x: x[0])[-6:]
        chart_labels = [month[0] for month in sorted_months]
        chart_amounts = [month[1] for month in sorted_months]

    cur.close()
    conn.close()

    return render_template('reports/reports.html', 
                         reports=reports,
                         selected_month=selected_month,
                         chart_period=chart_period,
                         total_revenue=total_revenue,
                         total_cases=total_cases,
                         avg_case_value=avg_case_value,
                         monthly_data=monthly_data,
                         chart_labels=chart_labels,
                         chart_amounts=chart_amounts,
                         user_role=user_role)

@reports_bp.route('/reports/download')
@login_required
def download_report_pdf():
    """Download financial report as PDF"""
    user_role = session.get('role')
    team = session.get('team')
    month = request.args.get('month')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Base query with JOIN to get agent names
    base_query = """
        SELECT c.*, u.name as agent_name 
        FROM cases c 
        LEFT JOIN users u ON c.agent_id = u.user_id 
        WHERE 1=1
    """
    params = []

    # Add month filter if selected
    if month:
        base_query += " AND c.date_created LIKE %s"
        params.append(f"{month}%")

    if user_role == 'Admin':
        report_title = "Company Financial Report"
    elif user_role == 'Leader':
        cur.execute("SELECT user_id FROM users WHERE team = %s AND role = 'Agent'", (team,))
        team_agent_ids = [row['user_id'] for row in cur.fetchall()]
        
        if team_agent_ids:
            format_ids = ','.join(['%s'] * len(team_agent_ids))
            base_query += f" AND c.agent_id IN ({format_ids})"
            params.extend(team_agent_ids)
        else:
            # No team agents, return empty result
            cur.close()
            conn.close()
            flash('No team agents found.', 'error')
            return redirect(url_for('reports.index'))
        report_title = f"Team {team} Financial Report"
    else:
        user_id = session.get('user_id')
        base_query += " AND c.agent_id = %s"
        params.append(user_id)
        report_title = "Personal Financial Report"

    base_query += " ORDER BY c.date_created DESC"
    
    cur.execute(base_query, params)
    reports = cur.fetchall()

    # Calculate report data
    total_revenue = sum(r['total_amount'] or 0 for r in reports)
    total_cases = len(reports)
    avg_case_value = total_revenue / total_cases if total_cases > 0 else 0

    # Generate PDF
    html_content = render_template('reports/report_pdf.html',
                                 reports=reports,
                                 total_revenue=total_revenue,
                                 total_cases=total_cases,
                                 avg_case_value=avg_case_value,
                                 report_title=report_title,
                                 month=month,
                                 now=datetime.now(),
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
            as_attachment=False,  # Changed from True to False for inline preview
            download_name=f"financial_report_{month or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        cur.close()
        conn.close()
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('reports.index'))
