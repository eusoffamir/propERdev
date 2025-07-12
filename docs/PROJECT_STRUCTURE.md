# Project Structure

This document provides a detailed overview of the propER project structure and organization.

## Overview

propER follows a modern, scalable Flask application architecture with clear separation of concerns and professional development practices.

## Directory Structure

```
propER/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── app.py                   # Main application instance
│   ├── routes.py                # Route registration
│   ├── core/                    # Core application components
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   └── db.py                # Database connection
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model class
│   │   ├── users.py             # User management models
│   │   ├── cases.py             # Case management models
│   │   ├── properties.py        # Property models
│   │   ├── clients.py           # Client models
│   │   ├── invoices.py          # Invoice models
│   │   ├── reports.py           # Report models
│   │   └── ...                  # Other models
│   ├── routes/                  # Flask blueprints
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── dashboard.py         # Dashboard routes
│   │   ├── cases.py             # Case management routes
│   │   ├── users.py             # User management routes
│   │   ├── reports.py           # Report routes
│   │   ├── admin.py             # Admin routes
│   │   └── settings.py          # Settings routes
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   └── controllers.py       # Business logic controllers
│   ├── middleware/              # Custom middleware
│   │   └── __init__.py
│   ├── exceptions/              # Custom exceptions
│   │   └── __init__.py
│   ├── templates/               # Jinja2 templates
│   │   ├── base/                # Base templates
│   │   ├── auth/                # Authentication templates
│   │   ├── dashboard/           # Dashboard templates
│   │   ├── cases/               # Case templates
│   │   ├── users/               # User templates
│   │   ├── reports/             # Report templates
│   │   ├── admin/               # Admin templates
│   │   └── billing/             # Billing templates
│   ├── static/                  # Static files
│   │   ├── css/                 # Stylesheets
│   │   ├── js/                  # JavaScript files
│   │   ├── images/              # Images and icons
│   │   ├── uploads/             # User uploads
│   │   └── exports/             # Generated exports
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── auth.py              # Authentication utilities
│       └── db.py                # Database utilities
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_db_connection.py
│   │   └── simple_test.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   └── test_admin_access.py
│   └── e2e/                     # End-to-end tests
│       └── __init__.py
├── scripts/                     # Utility scripts
│   ├── __init__.py
│   ├── setup_dev.py             # Development setup script
│   ├── database/                # Database scripts
│   │   ├── __init__.py
│   │   ├── setup_database.py    # Database initialization
│   │   ├── init_database.py     # Database setup
│   │   ├── init_db.py           # Database initialization
│   │   ├── insert_all_data.py   # Data insertion
│   │   ├── data/                # Data files
│   │   ├── output/              # Generated outputs
│   │   └── skipped_agents.txt   # Log files
│   ├── migrations/              # Migration scripts
│   │   ├── __init__.py
│   │   └── update_models.py     # Model updates
│   └── utils/                   # Development utilities
│       ├── __init__.py
│       └── db_viewer.py         # Database viewer utility
├── docs/                        # Documentation
│   ├── __init__.py
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── api/                     # API documentation
│   └── deployment/              # Deployment guides
│       ├── DATABASE_SETUP.md
│       └── DATABASE_MIGRATION_SUMMARY.md
├── pyproject.toml               # Project configuration
├── Makefile                     # Development tasks
├── requirements.txt             # Legacy dependencies
├── env.example                  # Environment template
├── .gitignore                   # Git ignore rules
├── .dockerignore                # Docker ignore rules
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose
├── run.py                       # Development server
├── wsgi.py                      # Production server
├── manage.py                    # Management commands
└── README.md                    # Project documentation
```

## Key Design Principles

### 1. Separation of Concerns
- **Models**: Data layer with SQLAlchemy ORM
- **Routes**: HTTP request handling and routing
- **Services**: Business logic and controllers
- **Templates**: Presentation layer
- **Static**: Client-side assets

### 2. Modularity
- Each major feature has its own blueprint
- Models are organized by domain
- Templates follow the same structure as routes

### 3. Scalability
- Blueprint-based routing for easy feature addition
- Service layer for business logic separation
- Database migrations for schema evolution
- Comprehensive testing structure

### 4. Development Experience
- Clear project structure
- Automated setup scripts
- Development tools (Makefile, pyproject.toml)
- Code quality tools (linting, formatting, type checking)

## File Naming Conventions

### Python Files
- Use snake_case for file names
- Use descriptive names that indicate purpose
- Group related functionality in modules

### Templates
- Use snake_case for template names
- Group by feature/blueprint
- Use descriptive names for clarity

### Static Files
- Use kebab-case for CSS/JS files
- Use descriptive names for images
- Organize by type (css/, js/, images/)

## Import Structure

### Application Imports
```python
# Core components
from app.core.config import Config
from app.core.db import db

# Models
from app.models.users import User
from app.models.cases import Case

# Routes
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp

# Services
from app.services.controllers import UserController
```

### Test Imports
```python
# Test utilities
from tests.conftest import client, db_session

# Application imports for testing
from app.models.users import User
from app.services.controllers import UserController
```

## Configuration Management

### Environment Variables
- Use `.env` file for local development
- Use `env.example` as template
- Never commit `.env` files to version control

### Configuration Classes
- `Config`: Base configuration
- `DevelopmentConfig`: Development settings
- `ProductionConfig`: Production settings
- `TestingConfig`: Testing settings

## Database Organization

### Models
- Each model in its own file
- Base model with common functionality
- Clear relationships between models
- Proper indexing and constraints

### Migrations
- Version-controlled schema changes
- Reversible migrations when possible
- Clear migration descriptions

## Testing Strategy

### Test Types
- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows

### Test Organization
- Mirror the application structure
- Use descriptive test names
- Include setup and teardown
- Use fixtures for common data

## Deployment Structure

### Development
- Local SQLite database
- Debug mode enabled
- Hot reloading
- Development-specific settings

### Production
- PostgreSQL database
- Gunicorn WSGI server
- Environment-specific configuration
- Docker containerization

## Security Considerations

### File Organization
- Sensitive files in `.gitignore`
- Environment variables for secrets
- Secure file upload handling
- Proper access controls

### Code Organization
- Input validation in services
- Authentication middleware
- Role-based access control
- Secure session management

## Performance Considerations

### Static Files
- Organized by type
- Optimized for delivery
- CDN-ready structure
- Caching strategies

### Database
- Proper indexing
- Query optimization
- Connection pooling
- Migration strategies

## Maintenance

### Code Quality
- Automated linting
- Code formatting
- Type checking
- Test coverage

### Documentation
- Inline code documentation
- API documentation
- Setup instructions
- Deployment guides

This structure provides a solid foundation for a professional, scalable Flask application that can grow with your business needs. 