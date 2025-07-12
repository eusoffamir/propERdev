#!/bin/bash
set -e

echo "🗄️ Starting database backup..."

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

# Configuration
PROJECT_DIR=$(pwd)
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="propdb"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Load environment variables if .env exists
if [ -f ".env" ]; then
    print_status "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
    
    # Override with .env values if they exist
    if [ ! -z "$DB_NAME" ]; then
        DB_NAME=$DB_NAME
    fi
    if [ ! -z "$DB_USER" ]; then
        DB_USER=$DB_USER
    fi
    if [ ! -z "$DB_HOST" ]; then
        DB_HOST=$DB_HOST
    fi
    if [ ! -z "$DB_PORT" ]; then
        DB_PORT=$DB_PORT
    fi
fi

# Check if PostgreSQL is running
print_status "Checking PostgreSQL status..."
if ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; then
    print_error "PostgreSQL is not running or not accessible"
    print_status "Trying to start PostgreSQL..."
    sudo systemctl start postgresql
    sleep 2
    
    if ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; then
        print_error "PostgreSQL is still not accessible"
        exit 1
    fi
fi

print_success "PostgreSQL is running"

# Create backup filename
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# Perform database backup
print_status "Creating database backup..."
print_status "Database: $DB_NAME"
print_status "User: $DB_USER"
print_status "Host: $DB_HOST"
print_status "Port: $DB_PORT"

# Set PGPASSWORD environment variable for password authentication
export PGPASSWORD="proper123"

# Create the backup
if pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_FILE; then
    print_success "Database backup created: $BACKUP_FILE"
    
    # Get backup file size
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    print_status "Backup size: $BACKUP_SIZE"
    
    # Verify backup file
    if [ -s $BACKUP_FILE ]; then
        print_success "Backup file is not empty and appears valid"
    else
        print_error "Backup file is empty or invalid"
        exit 1
    fi
else
    print_error "Database backup failed"
    exit 1
fi

# Create compressed backup
print_status "Creating compressed backup..."
gzip $BACKUP_FILE
COMPRESSED_FILE="$BACKUP_FILE.gz"
print_success "Compressed backup created: $COMPRESSED_FILE"

# Get compressed file size
COMPRESSED_SIZE=$(du -h $COMPRESSED_FILE | cut -f1)
print_status "Compressed backup size: $COMPRESSED_SIZE"

# Clean up old backups (keep last 7 days)
print_status "Cleaning up old backups..."
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete 2>/dev/null || true

# List recent backups
print_status "Recent backups:"
ls -lh $BACKUP_DIR/db_backup_*.sql.gz 2>/dev/null | tail -5 || print_warning "No recent backups found"

# Create backup summary
SUMMARY_FILE="$BACKUP_DIR/backup_summary_$DATE.txt"
cat > $SUMMARY_FILE << EOF
Database Backup Summary
======================

Date: $(date)
Database: $DB_NAME
Host: $DB_HOST
Port: $DB_PORT
User: $DB_USER

Backup Files:
- SQL: $BACKUP_FILE (removed after compression)
- Compressed: $COMPRESSED_FILE ($COMPRESSED_SIZE)

Backup Location: $BACKUP_DIR
Total Backups: $(ls $BACKUP_DIR/db_backup_*.sql.gz 2>/dev/null | wc -l)

EOF

print_success "Backup summary created: $SUMMARY_FILE"

# Test backup restoration (optional - uncomment if you want to test)
# print_status "Testing backup restoration..."
# TEST_DB="test_restore_$DATE"
# createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $TEST_DB
# gunzip -c $COMPRESSED_FILE | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TEST_DB
# dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $TEST_DB
# print_success "Backup restoration test completed"

print_success "Database backup completed successfully!"
echo ""
print_status "Backup location: $BACKUP_DIR"
print_status "Latest backup: $COMPRESSED_FILE"
print_status "Summary: $SUMMARY_FILE" 