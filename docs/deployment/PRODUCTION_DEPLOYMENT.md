# Production Deployment Guide

This guide covers deploying propER to your production server.

## Server Information

- **Host**: your-server-ip
- **Domain**: your-domain.com
- **SSH Username**: your-username
- **SSH Password**: your-password
- **SSH Port**: 22 (default)

## Database Configuration

- **Database**: PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **Database Name**: your-database-name
- **Username**: your-db-user
- **Password**: your-db-password

## Prerequisites

### Server Requirements
- Ubuntu/Debian server
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Git

### Local Requirements
- WinSCP (for file transfer)
- PuTTY (for SSH access)
- Git

## Deployment Methods

### Method 1: Manual Deployment (Current Practice)

#### 1. Prepare Your Application
```bash
# On your local machine
git add .
git commit -m "Production deployment"
git push origin main
```

#### 2. Transfer Files via WinSCP
1. Open WinSCP
2. Connect to your server:
   - Host: your-server-ip
   - Username: your-username
   - Password: your-password
   - Port: 22
3. Navigate to your project directory
4. Upload the updated files

#### 3. SSH into Server via PuTTY
```bash
# Connect to server
ssh your-username@your-server-ip

# Navigate to project directory
cd /path/to/your/project

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
# or
pip install -e ".[production]"

# Run database migrations
python scripts/migrations/update_models.py

# Restart the application
sudo systemctl restart proper
# or
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Method 2: Automated Deployment (Recommended)

#### 1. Create Deployment Script
Create `scripts/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Variables
PROJECT_DIR="/path/to/your/project"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="$PROJECT_DIR/backups"

# Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
cp -r $PROJECT_DIR/app $BACKUP_DIR/app_$(date +%Y%m%d_%H%M%S)

# Pull latest changes
echo "📥 Pulling latest changes..."
cd $PROJECT_DIR
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e ".[production]"

# Run database migrations
echo "🗄️ Running database migrations..."
python scripts/migrations/update_models.py

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart proper
sudo systemctl restart nginx

echo "✅ Deployment completed successfully!"
```

#### 2. Make Script Executable
```bash
chmod +x scripts/deploy.sh
```

#### 3. Run Deployment
```bash
./scripts/deploy.sh
```

## Environment Configuration

### 1. Create Production .env File
```bash
# On the server
cp env.example .env
nano .env
```

### 2. Production .env Configuration
```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
FLASK_DEBUG=False

# Secret Key (generate a secure one)
SECRET_KEY=your-production-secret-key-here

# Database Configuration (Production)
DATABASE_URL=postgresql://your-user:your-password@localhost:5432/your-database
SQLALCHEMY_DATABASE_URI=postgresql://your-user:your-password@localhost:5432/your-database

# Database Connection Details
DB_NAME=your-database-name
DB_USER=your-db-user
DB_PASS=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Security Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=3600

# Application Configuration
COMPANY_NAME=YourCompanyName
ADMIN_EMAIL=admin@yourcompany.com
SUPPORT_EMAIL=support@yourcompany.com

# Production Server Configuration
PRODUCTION_HOST=your-server-ip
PRODUCTION_DOMAIN=your-domain.com
```

## Service Configuration

### 1. Create Systemd Service
Create `/etc/systemd/system/proper.service`:

```ini
[Unit]
Description=propER Application
After=network.target

[Service]
User=your-username
Group=your-username
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
ExecStart=/path/to/your/project/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable proper
sudo systemctl start proper
sudo systemctl status proper
```

### 3. Nginx Configuration
Create `/etc/nginx/sites-available/proper`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /path/to/your/project/app/static/uploads/;
        expires 30d;
    }
}
```

### 4. Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/proper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Database Setup

### 1. PostgreSQL Installation
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE your_database_name;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_db_user;
\q
```

### 3. Initialize Database
```bash
# Run database setup
python scripts/database/setup_database.py

# Insert initial data
python scripts/database/insert_all_data.py
```

## SSL/HTTPS Setup

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 3. Auto-renewal
```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logs

### 1. View Application Logs
```bash
# Systemd logs
sudo journalctl -u proper -f

# Application logs
tail -f logs/proper.log
```

### 2. Monitor Resources
```bash
# System resources
htop

# Disk usage
df -h

# Memory usage
free -h
```

## Backup Strategy

### 1. Database Backup
```bash
# Create backup script
cat > /path/to/your/project/scripts/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/your/project/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres your_database_name > $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /path/to/your/project/scripts/backup_db.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /path/to/your/project/scripts/backup_db.sh
```

### 2. Application Backup
```bash
# Backup application files
tar -czf /path/to/your/project/backups/app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/your/project/app/
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   sudo chown -R your-username:your-username /path/to/your/project
   chmod +x scripts/*.sh
   ```

2. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -U postgres -d your_database_name
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port 8000
   sudo lsof -i :8000
   
   # Kill process
   sudo kill -9 <PID>
   ```

4. **Static Files Not Loading**
   ```bash
   # Check Nginx configuration
   sudo nginx -t
   
   # Check file permissions
   ls -la /path/to/your/project/app/static/
   ```

## Security Considerations

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

3. **Backup Verification**
   - Test database restores regularly
   - Verify backup file integrity
   - Store backups off-site

## Performance Optimization

1. **Gunicorn Configuration**
   ```bash
   # Optimize for your server
   gunicorn -w 4 -b 0.0.0.0:8000 --worker-class gevent --worker-connections 1000 wsgi:app
   ```

2. **Database Optimization**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_cases_status ON cases(status);
   CREATE INDEX idx_users_email ON users(email);
   ```

3. **Caching**
   - Implement Redis for session storage
   - Use CDN for static files
   - Enable browser caching

This deployment guide provides a comprehensive approach to deploying propER in production while maintaining security, performance, and reliability. 