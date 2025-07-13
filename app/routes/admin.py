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
    # Move 'users' and 'cases' to the front if they exist
    priority = ['users', 'cases']
    tables_sorted = [t for t in priority if t in tables] + [t for t in tables if t not in priority]
    return render_template('admin/database_viewer.html', tables=tables_sorted, user_role=session.get('role'), user_name=session.get('user_name'))

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
        columns = list(result.keys())
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

@admin_bp.route('/save-table-changes', methods=['POST'])
@admin_required
def save_table_changes():
    """Save changes to table data"""
    try:
        data = request.get_json()
        table_name = data.get('table_name')
        changes = data.get('changes', {})
        deleted_rows = data.get('deleted_rows', [])
        new_rows = data.get('new_rows', [])
        
        # Get all data to map row indices to actual data
        query = text(f"SELECT * FROM {table_name}")
        result = db.session.execute(query)
        columns = list(result.keys())
        all_rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Process updates
        for row_index_str, row_changes in changes.items():
            row_index = int(row_index_str)
            if row_index < len(all_rows):
                row_data = all_rows[row_index]
                
                # Build UPDATE query
                set_clauses = []
                where_clauses = []
                params = {}
                
                for column, new_value in row_changes.items():
                    set_clauses.append(f"{column} = :{column}_new")
                    params[f"{column}_new"] = new_value
                
                # Use first column as primary key for WHERE clause (simplified approach)
                primary_key = list(columns)[0]
                where_clauses.append(f"{primary_key} = :{primary_key}_old")
                params[f"{primary_key}_old"] = row_data[primary_key]
                
                update_query = text(f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}")
                db.session.execute(update_query, params)
        
        # Process deletions
        for row_index_str in deleted_rows:
            row_index = int(row_index_str)
            if row_index < len(all_rows):
                row_data = all_rows[row_index]
                
                # Use first column as primary key for WHERE clause
                primary_key = list(columns)[0]
                delete_query = text(f"DELETE FROM {table_name} WHERE {primary_key} = :{primary_key}")
                db.session.execute(delete_query, {primary_key: row_data[primary_key]})
        
        # Process new rows
        for new_row_data in new_rows:
            row_data = new_row_data.get('data', {})
            
            # Build INSERT query
            columns_list = list(columns)
            placeholders = [f":{col}" for col in columns_list]
            
            insert_query = text(f"INSERT INTO {table_name} ({', '.join(columns_list)}) VALUES ({', '.join(placeholders)})")
            db.session.execute(insert_query, row_data)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({"success": True, "message": "Changes saved successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/api/table/<table_name>')
@admin_required
def api_table_data(table_name):
    """API endpoint for table data (for AJAX requests)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = text(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {(page-1)*per_page}")
        result = db.session.execute(query)
        
        columns = list(result.keys())
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
        
        columns = list(result.keys())
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