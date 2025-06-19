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