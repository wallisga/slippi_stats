#!/bin/bash
# Slippi Server GCP Setup Script
# This script sets up the necessary GCP infrastructure for a Slippi server

# Exit on any error
set -e

# Configuration - Edit these variables as needed
PROJECT_ID="slippi-server-project"
REGION="us-central1"
ZONE="us-central1-a"
VM_NAME="slippi-server-vm"
VM_TYPE="e2-micro"
NETWORK="slippi-network"
SUBNET="slippi-subnet"

# Display the configuration
echo "GCP Slippi Server Setup"
echo "======================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"
echo "VM Name: $VM_NAME"
echo "VM Type: $VM_TYPE"
echo "Network: $NETWORK"
echo "Subnet: $SUBNET"
echo

# Confirm with user
read -p "Continue with this configuration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup canceled."
    exit 1
fi

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Set region and zone
echo "Setting region and zone..."
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# Create network infrastructure
echo "Creating network infrastructure..."
echo "Creating VPC network..."
gcloud compute networks create $NETWORK --subnet-mode=custom

echo "Creating subnet..."
gcloud compute networks subnets create $SUBNET \
    --network=$NETWORK \
    --region=$REGION \
    --range="10.0.0.0/24"

echo "Creating firewall rules..."
gcloud compute firewall-rules create allow-ssh \
    --network=$NETWORK \
    --allow=tcp:22 \
    --source-ranges="35.235.240.0/20"

gcloud compute firewall-rules create allow-https \
    --network=$NETWORK \
    --allow=tcp:443 \
    --source-ranges="0.0.0.0/0"

gcloud compute firewall-rules create allow-http \
    --network=$NETWORK \
    --allow=tcp:80 \
    --source-ranges="0.0.0.0/0"

gcloud compute firewall-rules create allow-slippi-api \
    --network=$NETWORK \
    --allow=tcp:5000 \
    --source-ranges="0.0.0.0/0"

# Create Cloud Router and NAT
echo "Setting up Cloud NAT for outbound connectivity..."
gcloud compute routers create slippi-router \
    --network=$NETWORK \
    --region=$REGION

gcloud compute routers nats create slippi-nat \
    --router=slippi-router \
    --region=$REGION \
    --nat-all-subnet-ip-ranges \
    --auto-allocate-nat-external-ips

# Create the VM
echo "Creating VM..."
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$VM_TYPE \
    --subnet=$SUBNET \
    --no-address \
    --metadata-from-file=startup-script=vm_startup.sh \
    --tags=http-server,https-server,slippi-api \
    --scopes=storage-ro,logging-write

# Create instance group
echo "Creating instance group..."
gcloud compute instance-groups unmanaged create slippi-instance-group \
    --zone=$ZONE

echo "Adding VM to instance group..."
gcloud compute instance-groups unmanaged add-instances slippi-instance-group \
    --zone=$ZONE \
    --instances=$VM_NAME

# Set up load balancer
echo "Setting up load balancer..."
echo "Creating health check..."
gcloud compute health-checks create http slippi-health-check \
    --port=5000 \
    --request-path="/api/stats"

echo "Creating backend service..."
gcloud compute backend-services create slippi-backend \
    --protocol=HTTP \
    --port-name=http \
    --health-checks=slippi-health-check \
    --global

echo "Adding instance group as backend..."
gcloud compute backend-services add-backend slippi-backend \
    --instance-group=slippi-instance-group \
    --instance-group-zone=$ZONE \
    --global

echo "Creating URL map..."
gcloud compute url-maps create slippi-url-map \
    --default-service=slippi-backend

echo "Creating HTTP proxy..."
gcloud compute target-http-proxies create slippi-http-proxy \
    --url-map=slippi-url-map

echo "Creating static IP..."
gcloud compute addresses create slippi-ip \
    --global

SLIPPI_IP=$(gcloud compute addresses describe slippi-ip --global --format="value(address)")

echo "Creating forwarding rule..."
gcloud compute forwarding-rules create slippi-http-forwarding-rule \
    --address=$SLIPPI_IP \
    --global \
    --target-http-proxy=slippi-http-proxy \
    --ports=80

# Print connection information
echo
echo "Setup complete!"
echo "===================="
echo "Your Slippi server IP address: $SLIPPI_IP"
echo
echo "To connect to your VM, use:"
echo "gcloud compute ssh $VM_NAME --tunnel-through-iap"
echo
echo "After connecting, run the server setup script:"
echo "sudo bash /tmp/server_setup.sh"