#!/bin/bash
# Script to upload server code to the VM

# Configuration
VM_NAME="slippi-server-vm"
APP_DIR="./server"  # Directory containing your server code (main.py)
REMOTE_DIR="/opt/slippi-server/app"

# Check if server code directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Server code directory '$APP_DIR' not found."
    echo "Please create this directory and place your server code (main.py, etc.) inside it."
    exit 1
fi

# Check if main.py exists
if [ ! -f "$APP_DIR/main.py" ]; then
    echo "Error: main.py not found in '$APP_DIR'."
    echo "Please ensure your server code is properly structured."
    exit 1
fi

# Create wsgi.py if it doesn't exist
if [ ! -f "$APP_DIR/wsgi.py" ]; then
    echo "Creating wsgi.py..."
    cat > "$APP_DIR/wsgi.py" << 'EOF'
from main import app

if __name__ == "__main__":
    app.run(host='0.0.0.0')
EOF
    echo "wsgi.py created."
fi

# Upload files to VM
echo "Uploading server code to VM..."
gcloud compute scp --recurse "$APP_DIR"/* "$VM_NAME":"$REMOTE_DIR" --tunnel-through-iap

# Set ownership and permissions
echo "Setting permissions..."
gcloud compute ssh "$VM_NAME" --tunnel-through-iap --command="sudo chown -R slippi:slippi $REMOTE_DIR && sudo chmod -R 755 $REMOTE_DIR"

# Start/restart the service
echo "Restarting the service..."
gcloud compute ssh "$VM_NAME" --tunnel-through-iap --command="sudo systemctl restart slippi-server"

# Check service status
echo "Checking service status..."
gcloud compute ssh "$VM_NAME" --tunnel-through-iap --command="sudo systemctl status slippi-server | head -n 15"

echo
echo "Upload complete!"
echo "You can check the logs with:"
echo "gcloud compute ssh $VM_NAME --tunnel-through-iap --command=\"sudo journalctl -u slippi-server -f\""