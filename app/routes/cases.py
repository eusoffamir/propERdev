from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import psycopg2
import psycopg2.extras
from app.utils.db import get_db
from app.utils.auth import login_required, leader_required

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/cases')
@login_required
def index():
    """List all cases with role-based filtering"""
    user_id = session.get('user_id')
    user_role = session.get('role')
    team = session.get('team')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if user_role == 'Admin':
        # Admin sees all cases
        cur.execute("SELECT * FROM cases ORDER BY date_created DESC")
        cases = cur.fetchall()
    elif user_role == 'Leader':
        # Leader sees team cases
        cur.execute("SELECT user_id FROM users WHERE team = %s AND role = 'Agent'", (team,))
        team_agent_ids = [row['user_id'] for row in cur.fetchall()]
        
        if team_agent_ids:
            format_ids = ','.join(['%s'] * len(team_agent_ids))
            cur.execute(f"SELECT * FROM cases WHERE agent_id IN ({format_ids}) ORDER BY date_created DESC", team_agent_ids)
            cases = cur.fetchall()
        else:
            cases = []
    else:
        # Agent sees only their cases
        cur.execute("SELECT * FROM cases WHERE agent_id = %s ORDER BY date_created DESC", (user_id,))
        cases = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('cases/cases.html', cases=cases, user_role=user_role)

@cases_bp.route('/add_case', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new case"""
    if request.method == 'POST':
        client_name = request.form['client_name']
        case_details = request.form['case_details']
        total_amount = request.form.get('total_amount', 0)
        agent_id = session['user_id']

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO cases (client_name, case_details, agent_id, total_amount, date_created) VALUES (%s, %s, %s, %s, %s)',
            (client_name, case_details, agent_id, total_amount, datetime.now().strftime('%Y-%m-%d'))
        )
        conn.commit()
        cur.close()
        conn.close()

        flash('Case added successfully!', 'success')
        return redirect(url_for('cases.index'))

    return render_template('cases/add_case.html')

@cases_bp.route('/cases/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(case_id):
    """Edit a case"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST':
        client_name = request.form['client_name']
        case_details = request.form['case_details']
        total_amount = request.form.get('total_amount', 0)
        status = request.form.get('status', 'Active')

        cur.execute("""
            UPDATE cases SET
                client_name = %s, case_details = %s, total_amount = %s, status = %s
            WHERE case_id = %s
        """, (client_name, case_details, total_amount, status, case_id))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Case updated successfully!', 'success')
        return redirect(url_for('cases.index'))

    cur.execute("SELECT * FROM cases WHERE case_id = %s", (case_id,))
    case = cur.fetchone()
    cur.close()
    conn.close()
    
    if not case:
        flash('Case not found.', 'error')
        return redirect(url_for('cases.index'))
    
    return render_template('cases/edit_case.html', case=case)

@cases_bp.route('/cases/<int:case_id>/delete', methods=['POST'])
@login_required
def delete(case_id):
    """Delete a case"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM cases WHERE case_id = %s", (case_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Case deleted successfully!', 'success')
    return redirect(url_for('cases.index'))

@cases_bp.route('/generate_invoice/<int:case_id>')
@login_required
def generate_invoice(case_id):
    """Generate invoice for a case"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM cases WHERE case_id = %s', (case_id,))
    case = cur.fetchone()
    cur.close()
    conn.close()

    if not case:
        flash('Case not found.', 'error')
        return redirect(url_for('cases.index'))

    def safe_float(val):
        try:
            return float(val) if val else 0
        except (ValueError, TypeError):
            return 0

    # Calculate invoice details
    total_amount = safe_float(case['total_amount'])
    commission_rate = 0.10  # 10% commission
    commission_amount = total_amount * commission_rate
    net_amount = total_amount - commission_amount

    invoice_data = {
        'case': case,
        'total_amount': total_amount,
        'commission_amount': commission_amount,
        'net_amount': net_amount,
        'invoice_date': datetime.now().strftime('%Y-%m-%d'),
        'invoice_number': f"INV-{case_id:06d}"
    }

    return render_template('billing/invoice.html', **invoice_data)

@cases_bp.route('/generate_receipt/<int:case_id>')
@login_required
def generate_receipt(case_id):
    """Generate receipt for a case"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM cases WHERE case_id = %s', (case_id,))
    case = cur.fetchone()
    cur.close()
    conn.close()

    if not case:
        flash('Case not found.', 'error')
        return redirect(url_for('cases.index'))

    def safe_float(val):
        try:
            return float(val) if val else 0
        except (ValueError, TypeError):
            return 0

    # Calculate receipt details
    total_amount = safe_float(case['total_amount'])
    commission_rate = 0.10  # 10% commission
    commission_amount = total_amount * commission_rate
    net_amount = total_amount - commission_amount

    receipt_data = {
        'case': case,
        'total_amount': total_amount,
        'commission_amount': commission_amount,
        'net_amount': net_amount,
        'receipt_date': datetime.now().strftime('%Y-%m-%d'),
        'receipt_number': f"REC-{case_id:06d}"
    }

    return render_template('billing/resit.html', **receipt_data)
