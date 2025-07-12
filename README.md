# propER

_Modular Flask-based SaaS CRM for Property & Legal Case Management_

propER is a professional, modular SaaS CRM system built with Flask, SQLAlchemy, and PostgreSQL. It is designed for property and legal case management, supporting role-based dashboards, team performance tracking, user management, and more. The system is production-ready, extensible, and easy to deploy with Docker.

---

## Features

- **Modular Flask App**: Clean app factory pattern, blueprints for each module (auth, dashboard, cases, users, reports, settings, admin)
- **Role-Based Dashboards**: Admin, Agent, and Leader dashboards with tailored views
- **Property & Legal Case Management**: Track cases, clients, properties, and activities
- **Team Performance & Commission Tracking**: Revenue, commission, and leaderboard analytics
- **User Management**: Registration, roles, password reset, and team management
- **PDF Generation**: Invoices and receipts as downloadable PDFs
- **Web-based Database Viewer**: Admins can browse and export any table from the web UI
- **RESTful Routing**: All endpoints use Flask blueprints and proper URL structure
- **PostgreSQL Backend**: Robust, production-grade database
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Testing**: Basic test suite included

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/propER.git
cd propER
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:proper123@localhost:5432/propdb
```

### 4. Initialize the Database
```bash
python setup_database.py
```
Or use the provided scripts in `app/scripts/` for data import.

### 5. Run the App
```bash
python run.py
```
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### 6. (Optional) Run with Docker
```bash
docker-compose up --build
```

---

## Usage

- **Login** as an admin, agent, or leader.
- **Dashboard**: See team stats, revenue, and recent activity.
- **Cases**: Add, view, and manage property/legal cases.
- **Reports**: Generate and export reports.
- **Manage Team**: Add/edit users, assign roles.
- **Settings**: Company and user settings.
- **Database Viewer**: (Admins only) Browse and export any table from the web UI.

---

## Project Structure

```
propER/
  app/
    models/           # SQLAlchemy models
    routes/           # Flask blueprints (modular routes)
    templates/        # Jinja2 templates
    static/           # CSS, images, etc.
    scripts/          # Data import/export scripts
    ...
  tests/              # Test suite
  requirements.txt    # Python dependencies
  Dockerfile          # Docker support
  docker-compose.yml  # Docker Compose config
  run.py              # App entry point
  README.md           # This file
```

---

## Database Viewer (Admin Only)
- Go to the Admin Dashboard and click **Database Viewer**.
- Browse all tables, view data, export to CSV, and see table structure.
- CLI alternative: `python db_viewer.py`

---

## Contributing
Pull requests and issues are welcome! Please open an issue to discuss your idea or bug before submitting a PR.

---

## License
[MIT](LICENSE)

---

## Credits
- Built with [Flask](https://flask.palletsprojects.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [PostgreSQL](https://www.postgresql.org/), and [Docker](https://www.docker.com/).
- UI inspired by modern SaaS dashboards.
