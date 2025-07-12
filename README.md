# propER

_Professional Property Management SaaS System_

propER is a modern, scalable SaaS application built with Flask for property and legal case management. It features role-based dashboards, team performance tracking, user management, and comprehensive reporting capabilities.

---

## 🚀 Features

- **Modern Flask Architecture**: Clean app factory pattern with blueprints
- **Role-Based Access Control**: Admin, Agent, and Leader dashboards
- **Property & Legal Case Management**: Complete case lifecycle tracking
- **Team Performance Analytics**: Revenue, commission, and leaderboard tracking
- **User Management**: Registration, roles, password reset, team management
- **PDF Generation**: Professional invoices and receipts
- **Database Management**: Web-based database viewer for admins
- **RESTful API**: Well-structured endpoints with proper HTTP methods
- **PostgreSQL Backend**: Production-grade database with migrations
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Comprehensive Testing**: Unit, integration, and e2e tests
- **Code Quality**: Linting, formatting, and type checking

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite for development)
- Docker (optional)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/propER.git
cd propER
```

### 2. Install Dependencies
```bash
# Install with pip
pip install -e ".[dev]"

# Or with make
make install-dev
```

### 3. Environment Setup
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your configuration
# Generate a secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Database Setup
```bash
# Setup database
make setup-db

# Or manually
python scripts/database/setup_database.py
```

### 5. Run the Application
```bash
# Development server
make run

# Or manually
python run.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🐳 Docker Deployment

### Quick Start with Docker
```bash
# Build and run with Docker Compose
make docker-compose-up

# Or manually
docker-compose up --build
```

### Production Deployment
```bash
# Build production image
make docker-build

# Run production container
make docker-run
```

## 🚀 Production Deployment

### Quick Deployment (WinSCP + PuTTY)
```bash
# 1. Transfer files via WinSCP to your-server-ip
# 2. SSH via PuTTY and run:
make deploy
```

### Manual Deployment
```bash
# SSH into server
ssh your-username@your-server-ip

# Navigate to project and deploy
cd /path/to/your/propER
source venv/bin/activate
make deploy
```

### Database Backup
```bash
# Create backup
make backup

# Restore from backup
gunzip -c backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U postgres -d propdb
```

**Server Details:**
- **Host**: your-server-ip
- **Domain**: your-domain.com
- **Database**: PostgreSQL (your-database-name)
- **SSH**: your-username@your-server-ip

See [Quick Deployment Guide](docs/deployment/QUICK_DEPLOYMENT.md) for detailed instructions.

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit      # Unit tests only
make test-integration  # Integration tests only
make test-e2e       # End-to-end tests only

# Run with coverage
make test-cov
```

---

## 🔧 Development

### Code Quality
```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Run all checks
make check
```

### Database Management
```bash
# Run migrations
make migrate

# Setup database
make setup-db
```

### Pre-commit Checks
```bash
# Prepare for commit (clean, install, check)
make pre-commit
```

---

## 📁 Project Structure

```
propER/
├── app/                    # Main application package
│   ├── core/              # Core components (db, config)
│   ├── models/            # SQLAlchemy models
│   ├── routes/            # Flask blueprints
│   ├── services/          # Business logic services
│   ├── middleware/        # Custom middleware
│   ├── exceptions/        # Custom exceptions
│   ├── templates/         # Jinja2 templates
│   ├── static/            # Static files (CSS, JS, images)
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── scripts/               # Utility scripts
│   ├── database/          # Database scripts
│   ├── migrations/        # Migration scripts
│   └── utils/             # Development utilities
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   └── deployment/        # Deployment guides
├── pyproject.toml         # Project configuration
├── Makefile               # Development tasks
├── requirements.txt       # Legacy dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose
├── run.py                 # Application entry point
└── wsgi.py                # WSGI entry point
```

---

## 🎯 Usage

### Default Users
- **Admin**: Full system access
- **Agent**: Case management and reporting
- **Leader**: Team management and analytics

### Key Features
- **Dashboard**: Real-time analytics and team performance
- **Cases**: Complete case lifecycle management
- **Reports**: Generate and export professional reports
- **Users**: Team management and role assignment
- **Settings**: System and user preferences
- **Database Viewer**: (Admin only) Browse and export data

---

## 📚 Documentation

- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Database Setup](docs/deployment/DATABASE_SETUP.md)
- [Migration Guide](docs/deployment/DATABASE_MIGRATION_SUMMARY.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and checks (`make pre-commit`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Use conventional commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- Built with [Flask](https://flask.palletsprojects.com/), [SQLAlchemy](https://www.sqlalchemy.org/), and [PostgreSQL](https://www.postgresql.org/)
- Modern UI inspired by leading SaaS platforms
- Icons and design elements from [Bootstrap](https://getbootstrap.com/)

---

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/propER/issues)
- **Email**: support@proper.com
