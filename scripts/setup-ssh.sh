#!/bin/bash
# SSH Setup Script for Homelab Infrastructure
# This script sets up SSH key authentication for Ansible to connect to Proxmox and Bastion hosts

set -e

echo "🔐 SSH Key Setup for Homelab Infrastructure"
echo "==========================================="
echo ""

# Default hosts
PROXMOX_HOST="${PROXMOX_HOST:-192.168.0.19}"
PROXMOX_USER="${PROXMOX_USER:-root}"
BASTION_HOST="${BASTION_HOST:-192.168.0.10}"
BASTION_USER="${BASTION_USER:-josemendoza}"
SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY_PATH" ]; then
    print_warning "SSH key not found at $SSH_KEY_PATH"
    echo "Generating new SSH key..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "homelab-ansible"
    print_status "SSH key generated at $SSH_KEY_PATH"
else
    print_status "SSH key found at $SSH_KEY_PATH"
fi

# Function to setup SSH for a host
setup_ssh_host() {
    local host=$1
    local user=$2
    local description=$3

    echo ""
    echo "Setting up SSH for $description ($user@$host)..."

    # Check if we can already connect without password
    if ssh -o BatchMode=yes -o ConnectTimeout=5 "$user@$host" "echo 'SSH test'" &>/dev/null; then
        print_status "SSH key authentication already working for $description"
        return 0
    fi

    # Copy SSH key
    print_warning "SSH key not configured for $description"
    echo "You'll be prompted for the password for $user@$host"

    if ssh-copy-id -i "$SSH_KEY_PATH.pub" "$user@$host" 2>/dev/null; then
        print_status "SSH key copied to $description"
    else
        print_error "Failed to copy SSH key to $description"
        echo "You can manually copy with:"
        echo "  cat $SSH_KEY_PATH.pub | ssh $user@$host 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'"
        return 1
    fi

    # Test connection
    if ssh -o BatchMode=yes "$user@$host" "echo 'SSH test'" &>/dev/null; then
        print_status "SSH connection test successful for $description"
    else
        print_error "SSH connection test failed for $description"
        return 1
    fi
}

# Setup Proxmox
setup_ssh_host "$PROXMOX_HOST" "$PROXMOX_USER" "Proxmox Server"

# Ask if user wants to setup Bastion
echo ""
read -p "Do you want to set up SSH for the Bastion host? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    setup_ssh_host "$BASTION_HOST" "$BASTION_USER" "Bastion Host"
fi

# Test with Ansible
echo ""
echo "Testing Ansible connectivity..."
echo "================================"

# Test if docker compose is available
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Rebuilding Docker container with SSH keys..."
    docker compose down
    docker compose up -d --build

    echo "Testing Ansible ping to Proxmox..."
    if docker compose exec -T homelab-dev ansible proxmox -i inventory.yml -m ping; then
        print_status "Ansible can connect to Proxmox!"
    else
        print_error "Ansible connection to Proxmox failed"
        echo "Check the error message above and ensure:"
        echo "  1. SSH keys are properly copied"
        echo "  2. Docker container has access to SSH keys"
        echo "  3. Inventory file has correct host information"
    fi
else
    print_warning "Docker not available. Skipping Ansible tests."
    echo "After setting up Docker, run: make test-ping-proxmox"
fi

echo ""
echo "🎉 SSH Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Run 'make test-ping-proxmox' to verify Ansible connectivity"
echo "  2. Run 'make proxmox-tf-apply' to create infrastructure with Terraform"
echo ""