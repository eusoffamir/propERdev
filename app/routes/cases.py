from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime
import psycopg2
import psycopg2.extras
from app.utils.db import get_db
from app.utils.auth import login_required, leader_required
import pdfkit

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

    return render_template('cases/cases.html', cases=cases, user_role=user_role, user_name=session.get('user_name'))

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

    # Auto-fill agent and leader name for GET
    agent_name = session.get('user_name', '')
    team = session.get('team', None)
    leader_name = ''
    if team:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT name FROM users WHERE team = %s AND role = 'Leader' LIMIT 1", (team,))
        row = cur.fetchone()
        if row:
            leader_name = row['name']
        cur.close()
        conn.close()

    return render_template('cases/add_case.html', agent_name=agent_name, leader_name=leader_name)

@cases_bp.route('/cases/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(case_id):
    """Edit a case"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST':
        # Fetch all fields from the form
        client_name = request.form.get('client_name')
        case_no = request.form.get('case_no')
        invoice_no = request.form.get('invoice_no')
        eform_id = request.form.get('eform_id')
        property_address = request.form.get('property_address')
        
        # Handle numeric fields properly
        def safe_float(value):
            if value == 'None' or value == '' or value is None:
                return None
            try:
                return float(value) if value else None
            except (ValueError, TypeError):
                return None
        
        purchase_price = safe_float(request.form.get('purchase_price'))
        fee_pct = safe_float(request.form.get('fee_pct'))
        commission_pct = safe_float(request.form.get('commission_pct'))
        commission_total = safe_float(request.form.get('commission_total'))
        override_leader_amt = safe_float(request.form.get('override_leader_amt'))
        override_hoa_amt = safe_float(request.form.get('override_hoa_amt'))
        profit_proper = safe_float(request.form.get('profit_proper'))
        ed_paid = safe_float(request.form.get('ed_paid'))
        ed_pending = request.form.get('ed_pending')
        tax = safe_float(request.form.get('tax'))
        total_amount = safe_float(request.form.get('total_amount'))
        
        reference_no = request.form.get('reference_no')
        registration_no = request.form.get('registration_no')
        mode_of_payment = request.form.get('mode_of_payment')
        in_part_payment_of = request.form.get('in_part_payment_of')
        description = request.form.get('description')
        case_details = request.form.get('case_details')
        payment_status = request.form.get('payment_status')
        case_status = request.form.get('case_status', 'Active')
        
        # Handle integer fields properly
        agent_id = request.form.get('agent_id')
        if agent_id == 'None' or agent_id == '':
            agent_id = None
        else:
            try:
                agent_id = int(agent_id) if agent_id else None
            except (ValueError, TypeError):
                agent_id = None
                
        leader_id = request.form.get('leader_id')
        if leader_id == 'None' or leader_id == '':
            leader_id = None
        else:
            try:
                leader_id = int(leader_id) if leader_id else None
            except (ValueError, TypeError):
                leader_id = None
                
        number = request.form.get('number')

        cur.execute("""
            UPDATE cases SET
                number = %s,
                client_name = %s,
                agent_id = %s,
                leader_id = %s,
                case_no = %s,
                invoice_no = %s,
                eform_id = %s,
                property_address = %s,
                purchase_price = %s,
                fee_pct = %s,
                commission_pct = %s,
                commission_total = %s,
                override_leader_amt = %s,
                override_hoa_amt = %s,
                profit_proper = %s,
                ed_paid = %s,
                ed_pending = %s,
                tax = %s,
                total_amount = %s,
                reference_no = %s,
                registration_no = %s,
                mode_of_payment = %s,
                in_part_payment_of = %s,
                description = %s,
                case_details = %s,
                payment_status = %s,
                case_status = %s
            WHERE case_id = %s
        """, (
            number, client_name, agent_id, leader_id, case_no, invoice_no, eform_id, property_address,
            purchase_price, fee_pct, commission_pct, commission_total, override_leader_amt, override_hoa_amt, profit_proper,
            ed_paid, ed_pending, tax, total_amount, reference_no, registration_no, mode_of_payment, in_part_payment_of,
            description, case_details, payment_status, case_status, case_id
        ))
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
    from num2words import num2words
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Fetch case only (no join)
    cur.execute('SELECT * FROM cases WHERE case_id = %s', (case_id,))
    case = cur.fetchone()
    if not case:
        cur.close()
        conn.close()
        flash('Case not found.', 'error')
        return redirect(url_for('cases.index'))

    # Fetch company settings (for bank, address, etc.)
    cur.execute('SELECT * FROM company_settings LIMIT 1')
    company = cur.fetchone()
    cur.close()
    conn.close()

    # Prepare all fields for the template
    net_price = float(case['purchase_price'] or 0)
    fee_pct = float(case['fee_pct'] or 0)
    amount = round(net_price * (fee_pct / 100), 2)
    tax = round(amount * 0.08, 2)  # SST 8%
    total = round(amount + tax, 2)
    total_words = num2words(total, to='currency', lang='en').replace('euro', 'Ringgit Malaysia').upper() + ' ONLY'

    # Invoice meta
    invoice_no = case['invoice_no'] or f"{case['case_id']}"
    date = case['date_created'][:10] if case['date_created'] else datetime.now().strftime('%Y-%m-%d')
    ref_no = case['reference_no'] or '-'
    reg_no = case['registration_no'] or (company['firm_reg_no'] if company and 'firm_reg_no' in company else '-')

    # Client and property
    client_name = case['client_name'] or '-'
    property_address = case['property_address'] or '-'

    # Company/bank
    bank_name = company['bank_name'] if company and 'bank_name' in company else '-'
    account_no = company['bank_account'] if company and 'bank_account' in company else '-'

    # Logo and signature paths (static)
    logo_left = url_for('static', filename='logo_left.png')
    logo_right = url_for('static', filename='logo_right.png')
    sign_path = url_for('static', filename='signature.png')
    stamp_path = url_for('static', filename='stamp_signature.png')

    return render_template(
        'billing/invoice.html',
        client_name=client_name,
        invoice_no=invoice_no,
        date=date,
        ref_no=ref_no,
        reg_no=reg_no,
        property_address=property_address,
        net_price=f"{net_price:,.2f}",
        fee_pct=f"{fee_pct:.2f}%",
        amount=f"{amount:,.2f}",
        tax=f"{tax:,.2f}",
        total=f"{total:,.2f}",
        total_words=total_words,
        bank_name=bank_name,
        account_no=account_no,
        logo_left=logo_left,
        logo_right=logo_right,
        sign_path=sign_path,
        stamp_path=stamp_path
    )

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

@cases_bp.route('/generate_invoice_pdf/<int:case_id>')
@login_required
def generate_invoice_pdf(case_id):
    from num2words import num2words
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM cases WHERE case_id = %s', (case_id,))
    case = cur.fetchone()
    if not case:
        cur.close()
        conn.close()
        flash('Case not found.', 'error')
        return redirect(url_for('cases.index'))
    cur.execute('SELECT * FROM company_settings LIMIT 1')
    company = cur.fetchone()
    cur.close()
    conn.close()
    # Use DB values directly, but swap amount and total due to DB issue
    net_price = float(case['purchase_price'] or 0)
    fee_pct = float(case['fee_pct'] or 0)
    amount = float(case['total_amount'] or 0)  # swapped
    tax = float(case['tax'] or 0)
    total = float(case['amount'] or 0)         # swapped
    total_words = num2words(total, to='currency', lang='en').replace('euro', 'Ringgit Malaysia').upper() + ' ONLY'
    invoice_no = case['invoice_no'] or f"{case['case_id']}"
    date = case['date_created'][:10] if case['date_created'] else datetime.now().strftime('%Y-%m-%d')
    ref_no = case['reference_no'] or '-'
    reg_no = case['registration_no'] or (company['firm_reg_no'] if company and 'firm_reg_no' in company else '-')
    client_name = case['client_name'] or '-'
    property_address = case['property_address'] or '-'
    bank_name = company['bank_name'] if company and 'bank_name' in company else '-'
    account_no = company['bank_account'] if company and 'bank_account' in company else '-'
    logo_left = url_for('static', filename='logo_left.png', _external=True)
    logo_right = url_for('static', filename='logo_right.png', _external=True)
    sign_path = url_for('static', filename='signature.png', _external=True)
    stamp_path = url_for('static', filename='stamp_signature.png', _external=True)
    context = dict(
        client_name=client_name,
        invoice_no=invoice_no,
        date=date,
        ref_no=ref_no,
        reg_no=reg_no,
        property_address=property_address,
        net_price=f"{net_price:,.2f}",
        fee_pct=f"{fee_pct:.2f}%",
        amount=f"{amount:,.2f}",
        tax=f"{tax:,.2f}",
        total=f"{total:,.2f}",
        total_words=total_words,
        bank_name=bank_name,
        account_no=account_no,
        logo_left=logo_left,
        logo_right=logo_right,
        sign_path=sign_path,
        stamp_path=stamp_path
    )
    rendered = render_template('billing/invoice.html', **context)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
    return response

@cases_bp.route('/generate_receipt_pdf/<int:case_id>')
@login_required
def generate_receipt_pdf(case_id):
    from num2words import num2words
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM cases WHERE case_id = %s', (case_id,))
    case = cur.fetchone()
    if not case:
        cur.close()
        conn.close()
        flash('Case not found.', 'error')
        return redirect(url_for('cases.index'))
    cur.execute('SELECT * FROM company_settings LIMIT 1')
    company = cur.fetchone()
    cur.close()
    conn.close()
    # For receipt as well
    net_price = float(case['purchase_price'] or 0)
    fee_pct = float(case['fee_pct'] or 0)
    amount = float(case['total_amount'] or 0)  # swapped
    tax = float(case['tax'] or 0)
    total = float(case['amount'] or 0)         # swapped
    total_words = num2words(total, to='currency', lang='en').replace('euro', 'Ringgit Malaysia').upper() + ' ONLY'
    receipt_no = case['invoice_no'] or f"{case['case_id']}"
    date = case['date_created'][:10] if case['date_created'] else datetime.now().strftime('%Y-%m-%d')
    ref_no = case['reference_no'] or '-'
    reg_no = case['registration_no'] or (company['firm_reg_no'] if company and 'firm_reg_no' in company else '-')
    client_name = case['client_name'] or '-'
    property_address = case['property_address'] or '-'
    bank_name = company['bank_name'] if company and 'bank_name' in company else '-'
    account_no = company['bank_account'] if company and 'bank_account' in company else '-'
    logo_left = url_for('static', filename='logo_left.png', _external=True)
    logo_right = url_for('static', filename='logo_right.png', _external=True)
    sign_path = url_for('static', filename='signature.png', _external=True)
    stamp_path = url_for('static', filename='stamp_signature.png', _external=True)
    context = dict(
        client_name=client_name,
        receipt_no=receipt_no,
        date=date,
        ref_no=ref_no,
        reg_no=reg_no,
        property_address=property_address,
        net_price=f"{net_price:,.2f}",
        fee_pct=f"{fee_pct:.2f}%",
        amount=f"{amount:,.2f}",
        tax=f"{tax:,.2f}",
        total=f"{total:,.2f}",
        total_words=total_words,
        bank_name=bank_name,
        account_no=account_no,
        logo_left=logo_left,
        logo_right=logo_right,
        sign_path=sign_path,
        stamp_path=stamp_path
    )
    rendered = render_template('billing/resit.html', **context)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=receipt.pdf'
    return response

@cases_bp.route('/cases/<int:case_id>/update_status', methods=['POST'])
@login_required
def update_status(case_id):
    new_status = request.json.get('case_status')
    if new_status not in ['SUBMIT', 'IN PROGRESS', 'SETTLE', 'KIV', 'CANCEL']:
        return {'success': False, 'error': 'Invalid status'}, 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE cases SET case_status = %s WHERE case_id = %s', (new_status, case_id))
    conn.commit()
    cur.close()
    conn.close()
    return {'success': True}
