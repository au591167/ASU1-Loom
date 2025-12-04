# Database Setup Guide for pandaserver.ddns.net

This guide will help you set up PostgreSQL on your server (pandaserver.ddns.net / 4.20.69.11) for the ASU1-Loom project.

## Prerequisites

- SSH access to pandaserver.ddns.net
- Root or sudo privileges
- Ubuntu/Debian-based system (adjust commands for other distros)

## Step 1: Install PostgreSQL

### On Ubuntu/Debian:
```bash
# SSH into your server
ssh user@pandaserver.ddns.net

# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Check PostgreSQL status
sudo systemctl status postgresql

# Enable PostgreSQL to start on boot
sudo systemctl enable postgresql
```

### On CentOS/RHEL:
```bash
# Install PostgreSQL
sudo yum install postgresql-server postgresql-contrib -y

# Initialize database
sudo postgresql-setup initdb

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 2: Configure PostgreSQL for Remote Access

### 1. Edit PostgreSQL Configuration
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Find and modify this line (uncomment and change):
listen_addresses = '*'

# Save and exit (Ctrl+X, Y, Enter)
```

### 2. Configure Client Authentication
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Add this line at the end to allow remote connections:
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             0.0.0.0/0               md5
host    all             all             ::/0                    md5

# Save and exit
```

### 3. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

## Step 3: Create Database and User

### 1. Access PostgreSQL
```bash
# Switch to postgres user
sudo -i -u postgres

# Open PostgreSQL prompt
psql
```

### 2. Create Database and User
```sql
-- Create the database
CREATE DATABASE loom_db;

-- Create the user with a strong password
CREATE USER loom_user WITH ENCRYPTED PASSWORD 'YOUR_SECURE_PASSWORD_HERE';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE loom_db TO loom_user;

-- Connect to the database
\c loom_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO loom_user;

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO loom_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO loom_user;

-- Exit psql
\q

-- Exit postgres user
exit
```

## Step 4: Configure Firewall

### Using UFW (Ubuntu):
```bash
# Allow PostgreSQL port
sudo ufw allow 5432/tcp

# Check firewall status
sudo ufw status
```

### Using firewalld (CentOS/RHEL):
```bash
# Allow PostgreSQL port
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload

# Check firewall status
sudo firewall-cmd --list-all
```

## Step 5: Initialize Database Schema

### Option A: Using the init.sql file
```bash
# Copy the init.sql file to your server
scp database/init.sql user@pandaserver.ddns.net:/tmp/

# SSH into server
ssh user@pandaserver.ddns.net

# Run the SQL file
sudo -u postgres psql -d loom_db -f /tmp/init.sql

# Clean up
rm /tmp/init.sql
```

### Option B: Manual table creation
```bash
# SSH into server
ssh user@pandaserver.ddns.net

# Access PostgreSQL
sudo -u postgres psql -d loom_db
```

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create containers table
CREATE TABLE IF NOT EXISTS containers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    image VARCHAR(255) NOT NULL,
    tag VARCHAR(50) DEFAULT 'latest',
    container_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'created',
    subdomain VARCHAR(255) UNIQUE NOT NULL,
    port INTEGER NOT NULL,
    environment TEXT,
    volumes TEXT,
    networks TEXT,
    labels TEXT,
    cpu_limit FLOAT,
    memory_limit INTEGER,
    restart_policy VARCHAR(50) DEFAULT 'unless-stopped',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_containers_status ON containers(status);
CREATE INDEX idx_containers_user_id ON containers(user_id);
CREATE INDEX idx_containers_subdomain ON containers(subdomain);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for containers table
CREATE TRIGGER update_containers_updated_at 
    BEFORE UPDATE ON containers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Exit
\q
```

## Step 6: Test Connection

### From your local machine:
```bash
# Test connection using psql
psql -h pandaserver.ddns.net -U loom_user -d loom_db

# Or using Python
python -c "import psycopg2; conn = psycopg2.connect('postgresql://loom_user:YOUR_PASSWORD@pandaserver.ddns.net:5432/loom_db'); print('✅ Connection successful!'); conn.close()"
```

### Expected output:
```
Password for user loom_user: [enter your password]
psql (15.x)
Type "help" for help.

loom_db=>
```

## Step 7: Update Your .env File

Update your local `.env` file with the correct credentials:

```env
DATABASE_URL=postgresql+asyncpg://loom_user:YOUR_SECURE_PASSWORD@pandaserver.ddns.net:5432/loom_db
POSTGRES_USER=loom_user
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
POSTGRES_DB=loom_db
```

## Security Best Practices

### 1. Use Strong Passwords
```bash
# Generate a strong password
openssl rand -base64 32
```

### 2. Restrict Access by IP (Optional but Recommended)
Edit `/etc/postgresql/15/main/pg_hba.conf`:
```
# Instead of 0.0.0.0/0, use your specific IP
host    loom_db         loom_user       YOUR_IP_ADDRESS/32      md5
```

### 3. Enable SSL/TLS (Recommended for Production)
```bash
# Generate self-signed certificate
sudo openssl req -new -x509 -days 365 -nodes -text -out /etc/postgresql/15/main/server.crt -keyout /etc/postgresql/15/main/server.key

# Set permissions
sudo chmod 600 /etc/postgresql/15/main/server.key
sudo chown postgres:postgres /etc/postgresql/15/main/server.key
sudo chown postgres:postgres /etc/postgresql/15/main/server.crt

# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Add/modify:
ssl = on
ssl_cert_file = '/etc/postgresql/15/main/server.crt'
ssl_key_file = '/etc/postgresql/15/main/server.key'

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 4. Regular Backups
```bash
# Create backup script
sudo nano /usr/local/bin/backup-loom-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump loom_db > $BACKUP_DIR/loom_db_$TIMESTAMP.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "loom_db_*.sql" -mtime +7 -delete

echo "Backup completed: loom_db_$TIMESTAMP.sql"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-loom-db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add this line:
0 2 * * * /usr/local/bin/backup-loom-db.sh
```

## Troubleshooting

### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if PostgreSQL is listening on port 5432
sudo netstat -plnt | grep 5432

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Authentication Failed
```bash
# Verify user exists
sudo -u postgres psql -c "\du"

# Reset password if needed
sudo -u postgres psql -c "ALTER USER loom_user WITH PASSWORD 'new_password';"
```

### Cannot Connect Remotely
```bash
# Check firewall
sudo ufw status
sudo iptables -L -n | grep 5432

# Verify pg_hba.conf settings
sudo cat /etc/postgresql/15/main/pg_hba.conf | grep -v "^#"

# Verify postgresql.conf
sudo cat /etc/postgresql/15/main/postgresql.conf | grep listen_addresses
```

### Permission Denied
```sql
-- Grant all necessary permissions
\c loom_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO loom_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO loom_user;
```

## Monitoring

### Check Database Size
```sql
SELECT pg_size_pretty(pg_database_size('loom_db'));
```

### Check Active Connections
```sql
SELECT * FROM pg_stat_activity WHERE datname = 'loom_db';
```

### Check Table Sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Quick Reference Commands

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Stop PostgreSQL
sudo systemctl stop postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql

# View logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Access PostgreSQL
sudo -u postgres psql

# Connect to loom_db
sudo -u postgres psql -d loom_db

# List databases
sudo -u postgres psql -c "\l"

# List users
sudo -u postgres psql -c "\du"
```

## Next Steps

After completing the database setup:

1. ✅ Update your local `.env` file with the correct credentials
2. ✅ Test the connection from your local machine
3. ✅ Run the ASU1-Loom backend to verify database connectivity
4. ✅ Check the TESTING_CHECKLIST.md for further testing steps

---

**Server:** pandaserver.ddns.net (4.20.69.11)  
**Database:** loom_db  
**User:** loom_user  
**Port:** 5432  
**Last Updated:** December 2025
