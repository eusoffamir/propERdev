from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from app.utils.db import get_db, get_leader_names, nric_to_dob
from app.utils.auth import login_required, admin_required, leader_required
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

def parse_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

@users_bp.route('/users')
@login_required
def index():
    """List users (Admin: all, Leader: only their agents)"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    user_role = session.get('role')
    user_id = session.get('user_id')
    if user_role == 'Admin':
        cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    elif user_role == 'Leader':
        cur.execute("SELECT * FROM users WHERE added_by = %s AND role = 'Agent' ORDER BY created_at DESC", (user_id,))
    else:
        cur.close()
        conn.close()
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.index'))
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('users/users.html', users=users)

@users_bp.route('/user/<int:user_id>')
@login_required
def details(user_id):
    """Return user details as an HTML fragment for the popup"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return "<div style='padding:2rem;text-align:center;color:#d7263d;'>User not found.</div>", 404
    return render_template('users/user_details_popup.html', user=user)

@users_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    """Return user edit form as an HTML fragment for the popup, or handle update"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        form = request.form
        cur.execute("""
            UPDATE users SET
                name = %s, email = %s, team = %s, phone = %s,
                ren_no = %s, nric = %s, tiering_pct = %s, position = %s,
                notes = %s, role = %s, status = %s
            WHERE user_id = %s
        """, (
            form.get('name', ''),
            form.get('email', ''),
            form.get('team', ''),
            form.get('phone', ''),
            form.get('ren_no', ''),
            form.get('nric', ''),
            parse_float(form.get('tiering_pct', None)),
            form.get('position', ''),
            form.get('notes', ''),
            form.get('role', ''),
            form.get('status', ''),
            user_id
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.pending_requests'))
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return "<div style='padding:2rem;text-align:center;color:#d7263d;'>User not found.</div>", 404
    from flask import session
    user_role = session.get('role')
    return render_template('users/edit_user_popup.html', user=user, user_role=user_role)

@users_bp.route('/user/<int:user_id>/remove', methods=['POST'])
@admin_required
def remove(user_id):
    """Remove a user (Admin only)"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('User removed successfully!', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/admin_register', methods=['GET', 'POST'])
@leader_required
def admin_register():
    """Register a new user (Admin/Leader only)"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        nric = request.form['nric']
        team = request.form['team']
        role = request.form['role']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (name, email, phone, nric, team, role, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, phone, nric, team, role, password_hash))
            conn.commit()
            flash('User registered successfully!', 'success')
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('This email is already registered.', 'error')
        cur.close()
        conn.close()
        
        return redirect(url_for('users.index'))

    leader_names = get_leader_names()
    return render_template('users/register.html', leader_names=leader_names)

@users_bp.route('/register_request', methods=['POST'])
def register_request():
    """Handle registration requests from new agents"""
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

@users_bp.route('/pending_requests')
@leader_required
def pending_requests():
    """View pending registration requests"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM registration_requests WHERE status = 'pending'")
    reqs = cur.fetchall()

    user_role = session.get('role')
    user_id = session.get('user_id')
    if user_role == 'Leader':
        cur.execute("SELECT * FROM users WHERE added_by = %s AND role = 'Agent'", (user_id,))
        users = cur.fetchall()
    else:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()

    # Sort: Admin first, then Leader, then Agent
    role_priority = {'Admin': 0, 'Leader': 1, 'Agent': 2}
    users.sort(key=lambda x: role_priority.get(x['role'], 3))

    cur.close()
    conn.close()

    return render_template(
        'auth/pending_requests.html',
        reqs=reqs,
        users=users,
        user_role=session.get('role'),
        user_name=session.get('user_name')
    )

@users_bp.route('/approve_request/<int:request_id>', methods=['POST'])
@leader_required
def approve_request(request_id):
    """Approve a registration request"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM registration_requests WHERE request_id = %s", (request_id,))
    req = cur.fetchone()
    
    if not req:
        cur.close()
        conn.close()
        flash('Request not found.', 'error')
        return redirect(url_for('users.pending_requests'))

    cur.execute("SELECT * FROM users WHERE email = %s", (req['email'],))
    existing = cur.fetchone()
    if existing:
        cur.execute("UPDATE registration_requests SET status = 'rejected' WHERE request_id = %s", (request_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('User already exists. Request rejected.', 'error')
        return redirect(url_for('users.pending_requests'))

    # Use posted team if admin, else use team from request
    from flask import session, request as flask_request
    team = req['team']
    if session.get('role') == 'Admin':
        posted_team = flask_request.form.get('team')
        if posted_team:
            team = posted_team

    cur.execute("""
        INSERT INTO users (name, nric, email, phone, team, role, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (req['name'], req['nric'], req['email'], req['phone'], team, req['role'], req['password_hash']))
    
    cur.execute("UPDATE registration_requests SET status = 'approved' WHERE request_id = %s", (request_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Registration request approved!', 'success')
    return redirect(url_for('users.pending_requests'))

@users_bp.route('/reject_request/<int:request_id>', methods=['POST'])
@leader_required
def reject_request(request_id):
    """Reject a registration request"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE registration_requests SET status = 'rejected' WHERE request_id = %s", (request_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Registration request rejected.', 'success')
    return redirect(url_for('users.pending_requests')) 

@users_bp.route('/change_team/<int:user_id>', methods=['POST'])
@admin_required
def change_team(user_id):
    """Change a user's team (Admin only, fast inline change)"""
    from flask import request
    team = request.form.get('team')
    if not team:
        flash('No team selected.', 'error')
        return redirect(url_for('users.pending_requests'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET team = %s WHERE user_id = %s", (team, user_id))
    if team == 'HQ':
        cur.execute("UPDATE users SET role = 'Admin' WHERE user_id = %s", (user_id,))
    else:
        # Only demote to Agent if not already Leader
        cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        if row and row[0] != 'Leader':
            cur.execute("UPDATE users SET role = 'Agent' WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Team updated successfully!', 'success')
    # Update session if the current user is changing their own team
    from flask import session as flask_session
    if flask_session.get('user_id') == user_id:
        flask_session['team'] = team
        if team == 'HQ':
            flask_session['role'] = 'Admin'
        else:
            # Only demote to Agent if not already Leader
            if row and row[0] != 'Leader':
                flask_session['role'] = 'Agent'
    return redirect(url_for('users.pending_requests')) 