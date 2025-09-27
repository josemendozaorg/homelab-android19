#!/bin/bash
# Script to help set up terraform.tfvars securely

echo "Setting up terraform.tfvars..."

cat > terraform.tfvars << 'EOF'
# Proxmox API token configuration
# To create a token in Proxmox:
# 1. Go to Datacenter -> Permissions -> API Tokens
# 2. Add new token for user (e.g., root or create terraform user)
# 3. Uncheck "Privilege Separation" for full permissions
# 4. Copy the token ID and secret

proxmox_api_token = "YOUR_USER@pve!YOUR_TOKEN_ID=YOUR-UUID-HERE"

# Example formats:
# proxmox_api_token = "root@pam!terraform=12345678-1234-1234-1234-123456789abc"
# proxmox_api_token = "terraform@pve!terraform=abcdef12-3456-7890-abcd-ef1234567890"

# LXC template (will be auto-downloaded by Ansible if not present)
lxc_template = "local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst"
EOF

echo ""
echo "terraform.tfvars created!"
echo ""
echo "IMPORTANT: Edit terraform.tfvars and replace YOUR_USER@pve!YOUR_TOKEN_ID=YOUR-UUID-HERE"
echo "with your actual Proxmox API token."
echo ""
echo "The file is already in .gitignore so it won't be committed to git."