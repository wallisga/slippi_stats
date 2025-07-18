#!/bin/bash
# VM Startup Script for Slippi Server
# This script runs automatically when the VM is created

# Update system packages
apt-get update
apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx sqlite3

# Create application directory
mkdir -p /opt/slippi-server
mkdir -p /opt/slippi-server/app
mkdir -p /opt/slippi-server/backups

# Create slippi user
useradd -m -s /bin/bash slippi
chown -R slippi:slippi /opt/slippi-server

# Add this section to your setup.sh after creating the slippi user
echo "Setting up Git for deployments..."

# Install git
apt-get install -y git

# Add Git deployment section to server setup script
cat >> /tmp/server_setup.sh << 'GITEOF'

# Set up Git for deployments
echo "Setting up Git deployment..."
sudo -u slippi git config --global user.name "Slippi Server"
sudo -u slippi git config --global user.email "slippi@$(hostname)"

# Create deployment script
cat > /opt/slippi-server/deploy.sh << 'DEPLOYEOF'
#!/bin/bash
set -e

echo "🚀 Deploying Slippi Stats Server..."

APP_DIR="/opt/slippi-server/app"
BACKUP_DIR="/opt/slippi-server/backups"
SERVICE_NAME="slippi-server"

# Create backup
echo "📦 Creating backup..."
timestamp=$(date +"%Y%m%d_%H%M%S")
if [ -f "$APP_DIR/slippi_data.db" ]; then
    cp "$APP_DIR/slippi_data.db" "$BACKUP_DIR/slippi_data_$timestamp.db"
    echo "✅ Database backed up"
fi

# Update code
echo "📥 Updating code..."
cd "$APP_DIR"
git fetch origin
git reset --hard origin/main

# Install dependencies
echo "📚 Installing dependencies..."
/opt/slippi-server/venv/bin/pip install -r requirements.txt

# Restart service
echo "🔄 Restarting service..."
systemctl restart "$SERVICE_NAME"

echo "✅ Deployment completed!"
DEPLOYEOF

chmod +x /opt/slippi-server/deploy.sh
chown slippi:slippi /opt/slippi-server/deploy.sh

GITEOF

# Copy server setup script to VM
cat > /tmp/server_setup.sh << 'EOF'
#!/bin/bash
# Slippi Server Setup Script
# This script sets up the Slippi server application on the VM

# Exit on any error
set -e

echo "Starting Slippi server setup..."

# Create Python virtual environment
cd /opt/slippi-server
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install flask gunicorn requests

# Change ownership to slippi user
chown -R slippi:slippi /opt/slippi-server

# Create database backup script
cat > /opt/slippi-server/backup.sh << 'EOB'
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="/opt/slippi-server/backups"
DB_FILE="/opt/slippi-server/app/slippi_data.db"

mkdir -p $BACKUP_DIR
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/slippi_data_$TIMESTAMP.db'"

# Keep only last 10 backups
ls -t $BACKUP_DIR/slippi_data_*.db | tail -n +11 | xargs -r rm
EOB

chmod +x /opt/slippi-server/backup.sh

# Set up cron job for daily backups
echo "0 2 * * * /opt/slippi-server/backup.sh" | crontab -

# Set up systemd service
cat > /etc/systemd/system/slippi-server.service << 'EOG'
[Unit]
Description=Slippi API Server
After=network.target

[Service]
User=slippi
Group=slippi
WorkingDirectory=/opt/slippi-server/app
Environment="PATH=/opt/slippi-server/venv/bin"
ExecStart=/opt/slippi-server/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOG

# Enable service (but don't start yet)
systemctl enable slippi-server

echo
echo "Slippi server setup complete!"
echo "Now you need to:"
echo "1. Upload your server code to /opt/slippi-server/app/"
echo "2. Start the service with: systemctl start slippi-server"
echo
echo "You can check the service status with: systemctl status slippi-server"
echo "And view logs with: journalctl -u slippi-server -f"
EOF

chmod +x /tmp/server_setup.sh