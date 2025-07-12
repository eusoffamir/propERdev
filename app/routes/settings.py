from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from app.utils.db import get_db
from app.utils.auth import login_required, admin_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def index():
    """Application settings page (Admin only)"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST':
        # Update company settings
        company_name = request.form.get('company_name', '')
        company_address = request.form.get('company_address', '')
        company_phone = request.form.get('company_phone', '')
        company_email = request.form.get('company_email', '')
        
        cur.execute("""
            UPDATE company_settings
            SET company_name = %s, address = %s, phone = %s, email = %s
            WHERE setting_id = 1
        """, (company_name, company_address, company_phone, company_email))
        
        conn.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings.index'))
    
    # Get current settings
    cur.execute("SELECT * FROM company_settings LIMIT 1")
    row = cur.fetchone()
    settings = dict(row) if row else {}
    
    cur.close()
    conn.close()
    
    # Get user info from session or settings
    user_name = session.get('user_name') or settings.get('company_name', '')
    user_email = session.get('user_email') or settings.get('email', '')
    user_phone = session.get('user_phone') or settings.get('phone', '')
    user_role = session.get('role') or ''
    notifications = False  # Set to True if you have notification logic
    editable_role = user_role == 'Admin'
    
    return render_template('settings.html', settings=settings, user_name=user_name, user_email=user_email, user_phone=user_phone, user_role=user_role, notifications=notifications, editable_role=editable_role)
