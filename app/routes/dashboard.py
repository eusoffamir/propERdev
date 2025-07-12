from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from app.utils.db import get_db
from app.utils.auth import login_required, role_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard route with role-based views"""
    user_id = session.get('user_id')
    user_role = session.get('role')
    user_name = session.get('user_name')
    team = session.get('team')

    if not user_id or not user_role:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    now = datetime.now()
    this_month = now.strftime('%Y-%m')

    # -------------------------
    # ADMIN DASHBOARD
    # -------------------------
    if user_role == 'Admin':
        cur.execute("SELECT * FROM cases ORDER BY date_created DESC")
        cases = cur.fetchall()
        total_revenue = sum(c['total_amount'] or 0 for c in cases)

        cur.execute("""
            SELECT u.user_id, u.name, u.tiering_pct, 
                   COUNT(c.case_id) as num_cases,
                   SUM(c.total_amount) as revenue
            FROM users u
            LEFT JOIN cases c ON u.user_id = c.agent_id
            WHERE u.role = 'Agent'
            GROUP BY u.user_id
            ORDER BY revenue DESC
            LIMIT 3
        """)
        agent_rows = cur.fetchall()

        team_commission = 0
        agent_performance = []
        for row in agent_rows:
            pct = row['tiering_pct'] or 0
            revenue = row['revenue'] or 0
            commission = int(revenue * pct / 100)
            team_commission += commission
            agent_performance.append({
                'name': row['name'],
                'cases': row['num_cases'],
                'sales': revenue,
                'commission': commission
            })

        chart_labels = []
        chart_values = []
        for i in range(6):
            month_str = (now - timedelta(days=30 * i)).strftime('%Y-%m')
            monthly_total = sum(c['total_amount'] or 0 for c in cases if c['date_created'].startswith(month_str))
            chart_labels.insert(0, month_str)
            chart_values.insert(0, monthly_total)

        team_revenue_month = sum(c['total_amount'] or 0 for c in cases if c['date_created'].startswith(this_month))

        team_commission_month = 0
        for row in agent_rows:
            monthly_sales = sum(
                c['total_amount'] or 0 for c in cases
                if c['date_created'].startswith(this_month) and c['agent_id'] == row['user_id']
            )
            pct = row['tiering_pct'] or 0
            team_commission_month += int(monthly_sales * pct / 100)

        cur.close()
        conn.close()
        return render_template(
            'dashboard/dashboard_admin.html',
            user_role=user_role,
            user_name=user_name,
            team_cases=cases,
            team_revenue=total_revenue,
            team_commission=team_commission,
            team_size=len(agent_rows),
            agent_performance=agent_performance,
            chart_labels=chart_labels,
            chart_values=chart_values,
            team_revenue_month=team_revenue_month,
            team_commission_month=team_commission_month
        )

    # -------------------------
    # LEADER DASHBOARD
    # -------------------------
    elif user_role == 'Leader':
        cur.execute("SELECT user_id, name, tiering_pct FROM users WHERE team = %s AND role = 'Agent'", (team,))
        team_agents = cur.fetchall()
        team_agent_ids = [a['user_id'] for a in team_agents]

        if team_agent_ids:
            format_ids = ','.join(['%s'] * len(team_agent_ids))
            cur.execute(f"SELECT * FROM cases WHERE agent_id IN ({format_ids})", team_agent_ids)
            team_cases = cur.fetchall()
        else:
            team_cases = []

        team_revenue = sum(c['total_amount'] or 0 for c in team_cases)

        agent_performance = []
        for agent in team_agents:
            agent_cases = [c for c in team_cases if c['agent_id'] == agent['user_id']]
            sales = sum(c['total_amount'] or 0 for c in agent_cases)
            commission = int(sales * (agent['tiering_pct'] or 0) / 100)
            agent_performance.append({
                'name': agent['name'],
                'cases': len(agent_cases),
                'sales': sales,
                'commission': commission
            })

        team_commission = sum(a['commission'] for a in agent_performance)

        team_cases_display = []
        agent_id_to_name = {a['user_id']: a['name'] for a in team_agents}
        for c in team_cases:
            cd = dict(c)
            cd['agent_name'] = agent_id_to_name.get(c['agent_id'], "Unknown")
            team_cases_display.append(cd)

        team_revenue_month = sum(c['total_amount'] or 0 for c in team_cases if c['date_created'].startswith(this_month))
        team_commission_month = team_commission

        chart_labels = []
        chart_values = []
        for i in range(6):
            month = (now - timedelta(days=30 * i)).strftime('%Y-%m')
            monthly_revenue = sum(
                c['total_amount'] or 0 for c in team_cases if c['date_created'].startswith(month)
            )
            chart_labels.insert(0, month)
            chart_values.insert(0, monthly_revenue)

        cur.close()
        conn.close()
        return render_template(
            'dashboard/dashboard_leader.html',
            user_role=user_role,
            user_name=user_name,
            team_cases=team_cases_display,
            team_revenue=team_revenue,
            team_revenue_month=team_revenue_month,
            team_commission=team_commission,
            team_commission_month=team_commission_month,
            team_size=len(team_agents),
            last_login='-',  # Optional
            agent_performance=agent_performance,
            chart_labels=chart_labels,
            chart_values=chart_values
        )

    # -------------------------
    # AGENT DASHBOARD
    # -------------------------
    else:
        cur.execute("SELECT * FROM cases WHERE agent_id = %s", (user_id,))
        user_cases = cur.fetchall()

        user_commission = sum(c['total_amount'] or 0 for c in user_cases)
        chart_labels = []
        chart_values = []

        for i in range(6):
            month = (now - timedelta(days=30 * i)).strftime('%Y-%m')
            monthly_total = sum(
                c['total_amount'] or 0 for c in user_cases if c['date_created'].startswith(month)
            )
            chart_labels.insert(0, month)
            chart_values.insert(0, monthly_total)

        cur.close()
        conn.close()
        return render_template(
            'dashboard/dashboard_agent.html',
            user_role=user_role,
            user_name=user_name,
            user_cases=user_cases,
            user_commission=user_commission,
            user_unpaid=0,  # Placeholder
            chart_labels=chart_labels,
            chart_values=chart_values
        )

@dashboard_bp.route('/submit_case', methods=['POST'])
@login_required
def submit_case():
    """Submit a new case (demo/placeholder)"""
    client_name = request.form['client_name']
    case_details = request.form['case_details']
    agent_id = session['user_id']

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO cases (client_name, case_details, agent_id, date_created) VALUES (%s, %s, %s, %s)',
        (client_name, case_details, agent_id, datetime.now().strftime('%Y-%m-%d'))
    )
    conn.commit()
    cur.close()
    conn.close()

    flash('Case submitted successfully!', 'success')
    return redirect(url_for('dashboard.index')) 