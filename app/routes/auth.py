from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from datetime import datetime
from app.utils.db import get_db, get_leader_names, nric_to_dob

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            leader_names = get_leader_names()
            return render_template('auth/login.html', error="Invalid email or password.", leader_names=leader_names)

        password_hash = user['password_hash']

        if not isinstance(password_hash, str) or not password_hash.startswith(('pbkdf2', 'scrypt', '$pbkdf2')):
            leader_names = get_leader_names()
            return render_template('auth/login.html', error="Password hash is invalid or corrupted.", leader_names=leader_names)

        if check_password_hash(password_hash, password):
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            session['team'] = user['team']

            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE users SET last_login=NOW() WHERE user_id=%s", (user['user_id'],))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('dashboard.index'))

        leader_names = get_leader_names()
        return render_template('auth/login.html', error="Invalid email or password.", leader_names=leader_names)
    
    # GET request - show login page
    leader_names = get_leader_names()
    return render_template('auth/login.html', leader_names=leader_names)

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('role', None)
    session.pop('team', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        nric = request.form['nric']
        dob = nric_to_dob(nric)  # auto-extract DOB
        email = request.form['email']
        phone = request.form['phone']
        team = request.form['team']
        password_hash = generate_password_hash(request.form['password'])
        role = "Agent"  # Only allow agent registration

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO registration_requests (name, nric, dob, email, phone, team, role, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, nric, dob, email, phone, team, role, password_hash))
            conn.commit()
            msg = "Registration submitted. Please contact Admin/Leader for approval."
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            msg = "This email has already been requested or registered."
        cur.close()
        conn.close()
        
        leader_names = get_leader_names()
        return render_template('auth/login.html', error=msg, leader_names=leader_names)
    
    leader_names = get_leader_names()
    return render_template('auth/login.html', leader_names=leader_names)

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    reset_link = None
    error = None
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user:
            error = "Email not found. Please enter a registered email."
        else:
            token = secrets.token_urlsafe(32)
            cur.execute("UPDATE users SET reset_token = %s WHERE email = %s", (token, email))
            conn.commit()
            reset_link = url_for('auth.reset_password', token=token, _external=True)
        cur.close()
        conn.close()
    return render_template('auth/forgot_password.html', reset_link=reset_link, error=error)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    error = None
    success = None
    if request.method == 'POST':
        pw = request.form['password']
        pw2 = request.form['confirm_password']
        if pw != pw2:
            error = "Passwords do not match."
        else:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM users WHERE reset_token = %s", (token,))
            user = cur.fetchone()
            if not user:
                error = "Invalid or expired link."
            else:
                cur.execute("UPDATE users SET password_hash = %s, reset_token = NULL WHERE reset_token = %s", 
                            (generate_password_hash(pw), token))
                conn.commit()
                success = "Password has been reset. You can now login."
            cur.close()
            conn.close()
    return render_template("auth/reset_password.html", error=error, success=success)
