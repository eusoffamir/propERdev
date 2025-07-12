import psycopg2
import psycopg2.extras
from datetime import datetime

def get_db():
    """Get database connection with proper credentials"""
    return psycopg2.connect(
        dbname="propdb",
        user="propuser",
        password="proppass123",
        host="localhost",
        port="5432"
    )

def get_leader_names():
    """Get list of leader names for registration dropdown"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT name FROM users WHERE role='Leader'")
    leaders = cur.fetchall()
    cur.close()
    conn.close()
    return [l['name'] for l in leaders]

def nric_to_dob(nric):
    """Convert NRIC to date of birth"""
    nric_digits = ''.join([c for c in nric if c.isdigit()])
    if len(nric_digits) < 6:
        return None
    yy = int(nric_digits[:2])
    mm = int(nric_digits[2:4])
    dd = int(nric_digits[4:6])
    now = datetime.now()
    cur_year_2d = int(now.strftime("%y"))
    yyyy = 2000 + yy if yy <= cur_year_2d else 1900 + yy
    try:
        dob = datetime(yyyy, mm, dd)
        return dob.strftime('%Y-%m-%d')
    except Exception:
        return None 