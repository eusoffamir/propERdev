from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from app.utils.db import get_db, get_leader_names, nric_to_dob
from app.utils.auth import login_required, admin_required, leader_required
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@admin_required
def index():
    """List all users (Admin only)"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('users/users.html', users=users)

@users_bp.route('/user/<int:user_id>')
@login_required
def details(user_id):
    """View user details"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    return render_template('users/user_details.html', user=user)

@users_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    """Edit user details"""
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
            form['name'], form['email'], form['team'], form['phone'],
            form['ren_no'], form['nric'], form['tiering_pct'], form['position'],
            form['notes'], form['role'], form['status'], user_id
        ))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.details', user_id=user_id))

    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    return render_template('users/edit_user.html', user=user)

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

@users_bp.route('/register', methods=['GET', 'POST'])
@leader_required
def register():
    """Register a new user (Admin/Leader only)"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        team = request.form['team']
        role = request.form['role']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (name, email, phone, team, role, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, phone, team, role, password_hash))
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

    cur.execute("""
        INSERT INTO users (name, nric, email, phone, team, role, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (req['name'], req['nric'], req['email'], req['phone'], req['team'], req['role'], req['password_hash']))
    
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