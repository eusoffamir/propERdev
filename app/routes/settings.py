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
            INSERT INTO company_settings (setting_key, setting_value) 
            VALUES ('company_name', %s), ('company_address', %s), ('company_phone', %s), ('company_email', %s)
            ON CONFLICT (setting_key) 
            DO UPDATE SET setting_value = EXCLUDED.setting_value
        """, (company_name, company_address, company_phone, company_email))
        
        conn.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings.index'))
    
    # Get current settings
    cur.execute("SELECT setting_key, setting_value FROM company_settings")
    settings = {row['setting_key']: row['setting_value'] for row in cur.fetchall()}
    
    cur.close()
    conn.close()
    
    return render_template('settings.html', settings=settings)
