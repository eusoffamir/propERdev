# propER Database Setup Guide

This guide will help you set up the database for the propER system using SQLAlchemy and PostgreSQL.

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.8+** with pip
3. **Virtual environment** (recommended)

## Database Configuration

### 1. PostgreSQL Setup

First, ensure PostgreSQL is running and create the database:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE propdb;

-- Create user (optional, you can use postgres user)
CREATE USER propuser WITH PASSWORD 'proppass123';
GRANT ALL PRIVILEGES ON DATABASE propdb TO propuser;

-- Exit psql
\q
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Database Configuration
DATABASE_URL=postgresql://postgres:proper123@localhost:5432/propdb
TEST_DATABASE_URL=postgresql://postgres:proper123@localhost:5432/propdb_test

# Server Configuration
HOST=127.0.0.1
PORT=5000
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Models Structure

The system uses the following models:

### Core Models
- **User**: System users (Admin, Leader, Agent)
- **Role**: User roles and permissions
- **Client**: Property clients/buyers
- **Case**: Property transactions and cases
- **Invoice**: Commission invoices
- **CompanySetting**: Company information for PDFs

### Financial Models
- **CommissionRecord**: Detailed commission tracking
- **Ledger**: Payment tracking
- **EDClosure**: ED calculations
- **EDSummary**: Quarterly ED performance
- **FinancialReport**: Financial reporting

### System Models
- **RegistrationRequest**: User registration requests
- **ActivityLog**: System activity logging
- **Notification**: User notifications
- **Property**: Property information

## Database Initialization

### Option 1: Using Flask CLI (Recommended)

```bash
# Initialize database with tables and seed data
python manage.py init-db

# Seed data only
python manage.py seed-data

# Drop all tables
python manage.py drop-db

# Create new user
python manage.py create-user
```

### Option 2: Direct Python Script

```bash
python setup_database.py
```

### Option 3: Manual Setup

```python
from app import create_app
from app.db import db

app = create_app('development')

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Your seeding code here
    print("Database initialized!")
```

## Default Users

After initialization, the following users are created:

| Role | Email | Password | Team |
|------|-------|----------|------|
| Admin | eusoff@proper.com | eusoff | Admin |
| Leader | azimi@proper.com | azimi | Team A |
| Agent | mizan@proper.com | mizan | Team A |

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(role_id),
    team VARCHAR(100),
    phone VARCHAR(20),
    ren_no VARCHAR(50),
    nric VARCHAR(20),
    tiering_pct FLOAT,
    position VARCHAR(100),
    notes VARCHAR(255),
    expiry_year INTEGER,
    registration_fee_paid BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    added_by INTEGER REFERENCES users(user_id),
    reset_token VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Cases Table
```sql
CREATE TABLE cases (
    case_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(client_id),
    agent_id INTEGER REFERENCES users(user_id),
    leader_id INTEGER REFERENCES users(user_id),
    case_no VARCHAR(100),
    invoice_no VARCHAR(100),
    property_address VARCHAR(255),
    purchase_price FLOAT,
    commission_total FLOAT,
    payment_status VARCHAR(50),
    case_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Database Migrations

To handle database schema changes, use Flask-Migrate:

```bash
# Initialize migrations
flask db init

# Create a new migration
flask db migrate -m "Add new field"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Check PostgreSQL is running and credentials are correct
2. **Import Error**: Ensure all dependencies are installed
3. **Permission Error**: Check database user permissions
4. **Table Already Exists**: Drop tables first or use migrations

### Reset Database

```bash
# Drop all tables
python manage.py drop-db

# Reinitialize
python manage.py init-db
```

## Production Setup

For production deployment:

1. Use environment variables for sensitive data
2. Set up proper database backups
3. Configure connection pooling
4. Use SSL connections
5. Set up monitoring and logging

## Support

For database issues, check:
- PostgreSQL logs
- Application logs
- Database connection settings
- Model definitions in `app/models/` 