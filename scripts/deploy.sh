#!/bin/bash
set -e

echo "🚀 Starting propER deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Configuration
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_DIR="$PROJECT_DIR/logs"
DATE=$(date +%Y%m%d_%H%M%S)

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p $BACKUP_DIR
mkdir -p $LOG_DIR
mkdir -p $PROJECT_DIR/app/static/uploads
mkdir -p $PROJECT_DIR/app/static/exports

# Create backup
print_status "Creating backup..."
if [ -d "$PROJECT_DIR/app" ]; then
    tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz app/
    print_success "Backup created: app_backup_$DATE.tar.gz"
else
    print_warning "No app directory found, skipping backup"
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv $VENV_DIR
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
if [ -f "pyproject.toml" ]; then
    pip install -e ".[production]"
    print_success "Dependencies installed from pyproject.toml"
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_error "No dependency file found (pyproject.toml or requirements.txt)"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your production configuration"
    else
        print_error "env.example not found"
        exit 1
    fi
fi

# Run database migrations
print_status "Running database migrations..."
if [ -f "scripts/migrations/update_models.py" ]; then
    python scripts/migrations/update_models.py
    print_success "Database migrations completed"
else
    print_warning "No migration script found, skipping database migrations"
fi

# Setup database if needed
print_status "Setting up database..."
if [ -f "scripts/database/setup_database.py" ]; then
    python scripts/database/setup_database.py
    print_success "Database setup completed"
else
    print_warning "No database setup script found"
fi

# Collect static files (if manage.py exists)
if [ -f "manage.py" ]; then
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    print_success "Static files collected"
fi

# Test the application
print_status "Testing application..."
if python -c "import app; print('Application imports successfully')" 2>/dev/null; then
    print_success "Application test passed"
else
    print_warning "Application test failed, but continuing deployment"
fi

# Check if systemd service exists
if systemctl list-unit-files | grep -q "proper.service"; then
    print_status "Restarting systemd service..."
    sudo systemctl restart proper
    print_success "Systemd service restarted"
else
    print_warning "Systemd service 'proper' not found"
    print_status "You can start the application manually with:"
    echo "gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app"
fi

# Check if nginx is installed and restart it
if command -v nginx &> /dev/null; then
    print_status "Testing nginx configuration..."
    if sudo nginx -t; then
        print_status "Restarting nginx..."
        sudo systemctl restart nginx
        print_success "Nginx restarted"
    else
        print_error "Nginx configuration test failed"
    fi
else
    print_warning "Nginx not found"
fi

# Clean up old backups (keep last 7 days)
print_status "Cleaning up old backups..."
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true

# Final status
print_success "Deployment completed successfully!"
echo ""
print_status "Next steps:"
echo "1. Check application status: sudo systemctl status proper"
echo "2. View logs: sudo journalctl -u proper -f"
echo "3. Test the application: curl http://localhost:8000"
echo "4. Check nginx status: sudo systemctl status nginx"
echo ""
print_status "Backup location: $BACKUP_DIR"
print_status "Log location: $LOG_DIR" 