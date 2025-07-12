# propER - Property Excel Realty CRM System

A comprehensive Flask-based SaaS CRM system for property/legal case management with PostgreSQL backend, SQLAlchemy models, and modular blueprint architecture.

## 🏗️ System Architecture

### Application Structure
```
propER - Copy/
├── run.py                 # 🚀 Main entry point
├── main.py               # 📝 Legacy monolithic app (being phased out)
├── app/                  # 🏢 Modular Flask application
│   ├── __init__.py       # 📦 Package initialization
│   ├── app.py           # 🔧 Flask app factory
│   ├── config.py        # ⚙️ Configuration management
│   ├── db.py            # 🗄️ Database initialization
│   ├── models/          # 📊 SQLAlchemy models
│   ├── routes/          # 🛣️ Blueprint routes
│   ├── templates/       # 🎨 HTML templates
│   └── static/          # 📁 Static files (CSS, images)
├── scripts/             # 🔧 Database setup scripts
└── tests/               # 🧪 Test files
```

## 🔄 How Everything Connects

### 1. Application Startup Flow
```
run.py → app/__init__.py → app/app.py → create_app() → register_routes() → Blueprints
```

**Step-by-step:**
1. **`run.py`** - Entry point that calls `create_app('development')`
2. **`app/__init__.py`** - Imports and exports `create_app` from `app.app`
3. **`app/app.py`** - Flask app factory that:
   - Loads configuration from `config.py`
   - Initializes database with `db.py`
   - Registers blueprints from `routes/__init__.py`
   - Creates database tables

### 2. Route Registration Flow
```
app/routes/__init__.py → register_routes() → auth_bp + root_bp → Templates
```

**Current Blueprints:**
- **`auth_bp`** (`app/routes/auth.py`) - Authentication routes (login, register, forgot password)
- **`root_bp`** (`app/routes/root.py`) - Root route that redirects to login

### 3. Database Architecture
```
app/db.py → SQLAlchemy + Migrate → app/models/ → PostgreSQL
```

**Database Components:**
- **`db.py`** - SQLAlchemy and Flask-Migrate initialization
- **`models/`** - SQLAlchemy models inheriting from `BaseModel`
- **PostgreSQL** - Production database with proper user/role management

### 4. Template Structure
```
app/templates/
├── auth/           # 🔐 Authentication pages
├── base/           # 🏗️ Base templates
├── dashboard/      # 📊 Dashboard pages
├── cases/          # 📋 Case management
├── users/          # 👥 User management
├── reports/        # 📈 Reports
└── billing/        # 💰 Billing templates
```

## 🚀 How to Run the Application

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Required Python packages (see `requirements.txt`)

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up database (if not already done)
python setup_database.py

# 3. Run the application
python run.py
```

### Database Setup
```bash
# Create database and user
python manage.py setup-db

# Or use the setup script
python setup_database.py
```

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV` - Environment (development/production)
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key

### Database Configuration
```python
# Default development config
SQLALCHEMY_DATABASE_URI = 'postgresql://propuser:proppass123@localhost:5432/propdb'
```

## 🛣️ Route Structure

### Authentication Routes (`auth_bp`)
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET/POST /register` - User registration
- `GET/POST /forgot_password` - Password reset request
- `GET/POST /reset_password/<token>` - Password reset

### Root Routes (`root_bp`)
- `GET /` - Redirects to login page

### Legacy Routes (in `main.py`)
- Dashboard, cases, reports, users, settings (being migrated to blueprints)

## 📊 Database Models

### Core Models
- **User** - System users with roles (Admin, Leader, Agent)
- **Role** - User roles and permissions
- **Client** - Client information
- **Case** - Legal/property cases
- **Invoice** - Billing and invoicing
- **Property** - Property listings

### Supporting Models
- **RegistrationRequest** - Pending user registrations
- **CommissionRecord** - Commission tracking
- **ActivityLog** - System activity logging
- **Notification** - User notifications
- **FinancialReport** - Financial reporting

## 🔄 Migration from Monolithic to Modular

### Current State
- **Modular Structure**: New blueprint-based architecture in `app/` directory
- **Legacy Code**: Original monolithic app still in `main.py` for backward compatibility
- **Hybrid Approach**: Some routes in blueprints, others still in main.py

### Migration Progress
✅ **Completed:**
- Authentication routes (login, register, forgot password)
- Database models and SQLAlchemy setup
- Configuration management
- App factory pattern

🔄 **In Progress:**
- Dashboard routes
- Case management routes
- User management routes
- Report routes

📋 **To Do:**
- Complete blueprint migration
- Remove legacy `main.py` routes
- Add proper error handling
- Implement proper session management

## 🧪 Testing

### Test Structure
```
tests/
├── test_app.py      # Application tests
└── test_data.py     # Data validation tests
```

### Running Tests
```bash
python -m pytest tests/
```

## 🐳 Docker Support

### Docker Configuration
- `Dockerfile` - Application container
- `docker-compose.yml` - Multi-container setup
- `.dockerignore` - Docker ignore patterns

### Running with Docker
```bash
docker-compose up --build
```

## 🔍 Debugging

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **Blueprint Routes**: Check that routes are properly registered in `app/routes/__init__.py`
3. **Template Errors**: Verify `url_for()` calls use correct blueprint prefixes (e.g., `auth.login`)

### Debug Mode
The application runs in debug mode by default, providing:
- Auto-reload on code changes
- Detailed error messages
- Debugger PIN for interactive debugging

## 📝 Development Notes

### Key Design Decisions
1. **Modular Architecture**: Blueprint-based for better maintainability
2. **Database**: PostgreSQL with SQLAlchemy ORM
3. **Authentication**: Session-based with password hashing
4. **Templates**: Jinja2 with blueprint-aware routing
5. **Configuration**: Environment-based configuration management

### Best Practices
- Use blueprint prefixes in `url_for()` calls
- Inherit from `BaseModel` for all database models
- Use proper database transactions
- Implement proper error handling
- Follow Flask application factory pattern

## 🤝 Contributing

1. Follow the modular architecture pattern
2. Add new routes to appropriate blueprints
3. Update templates to use correct blueprint prefixes
4. Test database migrations
5. Update documentation

## 📄 License

This project is proprietary software for Property Excel Realty.
