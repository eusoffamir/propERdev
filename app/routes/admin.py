from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for, flash
from sqlalchemy import text, inspect
from app.models import *
from app.core.db import db
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('role') not in ['Admin', 'admin']:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    """Admin dashboard with database viewer"""
    # Get all table names
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return render_template('admin/database_viewer.html', tables=tables, user_role=session.get('role'), user_name=session.get('user_name'))

@admin_bp.route('/table/<table_name>')
@admin_required
def view_table(table_name):
    """View data from a specific table"""
    try:
        # Get table data with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Use raw SQL to get data from any table
        query = text(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {(page-1)*per_page}")
        result = db.session.execute(query)
        
        # Get column names
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Get total count
        count_query = text(f"SELECT COUNT(*) FROM {table_name}")
        total_count = db.session.execute(count_query).scalar()
        
        # Get table info
        inspector = inspect(db.engine)
        table_info = inspector.get_columns(table_name)
        
        return render_template('admin/table_view.html', 
                             table_name=table_name,
                             columns=columns,
                             rows=rows,
                             page=page,
                             per_page=per_page,
                             total_count=total_count,
                             table_info=table_info,
                             user_role=session.get('role'),
                             user_name=session.get('user_name'),
                             min=min)
    
    except Exception as e:
        return f"Error viewing table: {str(e)}", 500

@admin_bp.route('/api/table/<table_name>')
@admin_required
def api_table_data(table_name):
    """API endpoint for table data (for AJAX requests)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = text(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {(page-1)*per_page}")
        result = db.session.execute(query)
        
        columns = result.keys()
        rows = [dict(zip(columns, [str(val) if val is not None else '' for val in row])) for row in result.fetchall()]
        
        count_query = text(f"SELECT COUNT(*) FROM {table_name}")
        total_count = db.session.execute(count_query).scalar()
        
        return jsonify({
            "data": rows,
            "columns": list(columns),
            "total": total_count,
            "page": page,
            "per_page": per_page
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/export/<table_name>')
@admin_required
def export_table(table_name):
    """Export table data to CSV"""
    try:
        query = text(f"SELECT * FROM {table_name}")
        result = db.session.execute(query)
        
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Convert to DataFrame and export
        df = pd.DataFrame(rows)
        
        from flask import send_file
        import io
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table_name}_export.csv'
        )
    
    except Exception as e:
        return f"Error exporting table: {str(e)}", 500 