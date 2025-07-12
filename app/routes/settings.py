from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from app.utils.db import get_db
from app.utils.auth import login_required, admin_required
from werkzeug.utils import secure_filename
import os
from werkzeug.security import check_password_hash, generate_password_hash

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def index():
    """Settings page - Admin settings for admins, user profile for others"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    user_role = session.get('role', '')
    user_id = session.get('user_id')
    avatar_folder = os.path.join('app', 'static', 'avatars')
    avatar_filename = f"{user_id}.jpg"
    avatar_path = os.path.join(avatar_folder, avatar_filename)
    avatar_url = url_for('static', filename=f'avatars/{avatar_filename}') if os.path.exists(avatar_path) else url_for('static', filename='default-avatar.jpg')

    if user_role == 'Admin':
        # Admin settings - company settings
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
            flash('Company settings updated successfully!', 'success')
            return redirect(url_for('settings.index'))
        
        # Get current company settings
        cur.execute("SELECT * FROM company_settings LIMIT 1")
        row = cur.fetchone()
        settings = dict(row) if row else {}
        
        cur.close()
        conn.close()
        
        return render_template('settings.html', settings=settings, user_role=user_role, is_admin=True)
    
    else:
        # User profile settings for agents and leaders
        if request.method == 'POST':
            # Update user profile
            user_name = request.form.get('user_name', '')
            user_email = request.form.get('user_email', '')
            user_phone = request.form.get('user_phone', '')
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            # Handle avatar upload
            if 'avatar' in request.files:
                avatar = request.files['avatar']
                if avatar and avatar.filename:
                    filename = secure_filename(f"{user_id}.jpg")
                    save_path = os.path.join(avatar_folder, filename)
                    avatar.save(save_path)
            # Update name/email/phone
            cur.execute("""
                UPDATE users
                SET name = %s, email = %s, phone = %s
                WHERE user_id = %s
            """, (user_name, user_email, user_phone, user_id))
            # Password change logic
            if new_password:
                if not old_password:
                    flash('Old password is required to change password.', 'danger')
                    return redirect(url_for('settings.index'))
                if new_password != confirm_password:
                    flash('New passwords do not match.', 'danger')
                    return redirect(url_for('settings.index'))
                # Fetch current password hash
                cur.execute("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
                pw_row = cur.fetchone()
                if not pw_row or not check_password_hash(pw_row['password_hash'], old_password):
                    flash('Old password is incorrect.', 'danger')
                    return redirect(url_for('settings.index'))
                # Update password
                new_hash = generate_password_hash(new_password)
                cur.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_hash, user_id))
            conn.commit()
            # Update session
            session['user_name'] = user_name
            session['user_email'] = user_email
            session['user_phone'] = user_phone
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('settings.index'))
        
        # Get current user info
        cur.execute("SELECT name, email, phone FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        user_info = dict(row) if row else {}
        
        return render_template('settings.html', user_info=user_info, user_role=user_role, is_admin=False, avatar_url=avatar_url)
