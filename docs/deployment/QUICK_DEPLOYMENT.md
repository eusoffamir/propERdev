# Quick Deployment Guide

This guide covers the quick deployment process using your current workflow (WinSCP + PuTTY).

## Your Current Setup

- **Server**: 51.38.158.159
- **Domain**: proper.propin.dev
- **SSH**: mac@51.38.158.159 (port 22)
- **Database**: PostgreSQL (propdb)
- **Tools**: WinSCP + PuTTY

## Quick Deployment Steps

### 1. Prepare Your Code
```bash
# On your local machine
git add .
git commit -m "Production update"
git push origin main
```

### 2. Transfer Files via WinSCP
1. **Open WinSCP**
2. **Connect to server**:
   - Host: `51.38.158.159`
   - Username: `mac`
   - Password: `nasiayam2010`
   - Port: `22`
3. **Navigate to your project directory** (e.g., `/home/mac/propER`)
4. **Upload the updated files** (drag and drop)

### 3. SSH via PuTTY and Deploy
```bash
# Connect via PuTTY
ssh mac@51.38.158.159

# Navigate to project
cd /path/to/your/propER

# Activate virtual environment
source venv/bin/activate

# Quick deployment
make deploy
# OR manually:
# pip install -r requirements.txt
# python scripts/migrations/update_models.py
# sudo systemctl restart proper
```

## Alternative Manual Commands

If you prefer manual deployment:

```bash
# SSH into server
ssh mac@51.38.158.159

# Navigate to project
cd /path/to/your/propER

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# OR for production dependencies:
pip install -e ".[production]"

# Run database migrations
python scripts/migrations/update_models.py

# Setup database if needed
python scripts/database/setup_database.py

# Insert data if needed
python scripts/database/insert_all_data.py

# Restart application
sudo systemctl restart proper
# OR run manually:
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# Check status
sudo systemctl status proper
```

## Database Operations

### Backup Database
```bash
# Create backup
make backup
# OR manually:
./scripts/backup_db.sh
```

### Restore Database
```bash
# Restore from backup
gunzip -c backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U postgres -d propdb
```

## Useful Commands

### Check Application Status
```bash
# Check if application is running
sudo systemctl status proper

# View application logs
sudo journalctl -u proper -f

# Check nginx status
sudo systemctl status nginx
```

### Database Commands
```bash
# Connect to database
psql -h localhost -U postgres -d propdb

# List tables
\dt

# Check database size
SELECT pg_size_pretty(pg_database_size('propdb'));

# Exit database
\q
```

### File Operations
```bash
# Check disk space
df -h

# Check file permissions
ls -la

# Fix permissions if needed
sudo chown -R mac:mac /path/to/your/propER
chmod +x scripts/*.sh
```

## Troubleshooting

### Application Not Starting
```bash
# Check logs
sudo journalctl -u proper -f

# Check if port is in use
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Test connection
psql -h localhost -U postgres -d propdb
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R mac:mac /path/to/your/propER

# Fix permissions
chmod +x scripts/*.sh
chmod 755 app/static/uploads/
```

## Environment Variables

Make sure your `.env` file on the server has:

```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://postgres:proper123@localhost:5432/propdb
SECRET_KEY=your-production-secret-key
```

## Quick Commands Reference

| Command | Description |
|---------|-------------|
| `make deploy` | Full deployment |
| `make backup` | Database backup |
| `make run` | Run locally |
| `sudo systemctl restart proper` | Restart application |
| `sudo systemctl status proper` | Check status |
| `sudo journalctl -u proper -f` | View logs |

## Tips

1. **Always backup before deployment**: `make backup`
2. **Check logs if something goes wrong**: `sudo journalctl -u proper -f`
3. **Test locally first**: `make run`
4. **Keep your virtual environment updated**: `pip install -r requirements.txt`
5. **Monitor disk space**: `df -h`

This quick guide should help you deploy efficiently using your current workflow! 