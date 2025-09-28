# SSH Setup for Ansible → Proxmox Communication

## Problem
When you see this error:
```
Permission denied (publickey,password)
```

It means Ansible cannot SSH to your Proxmox host. This guide will help you set up passwordless SSH authentication.

## Solution: Set Up SSH Key Authentication

### Step 1: Generate SSH Key (if you don't have one)
```bash
# On your local machine (Windows/WSL/Linux)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

### Step 2: Copy SSH Key to Proxmox
```bash
# Copy your public key to the Proxmox server
ssh-copy-id root@192.168.0.19

# You'll be prompted for the root password
# Enter it once, and you won't need it again
```

### Step 3: Test SSH Connection
```bash
# Test direct SSH (should work without password)
ssh root@192.168.0.19 "echo 'SSH key auth working!'"
```

### Step 4: Test Ansible Connection
```bash
# Rebuild Docker container to include your SSH keys
docker compose down
docker compose up -d --build

# Test Ansible can connect
make test-ping-proxmox
```

## Alternative: For Bastion Host
If you're setting up the bastion host (192.168.0.10):
```bash
ssh-copy-id josemendoza@192.168.0.10
```

## Troubleshooting

### If ssh-copy-id fails:
```bash
# Manually copy the key
cat ~/.ssh/id_rsa.pub | ssh root@192.168.0.19 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### If you're on Windows without ssh-copy-id:
```powershell
# PowerShell method
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh root@192.168.0.19 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Check SSH key permissions:
```bash
# On Proxmox server
ssh root@192.168.0.19 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

## Security Notes
- Keep your private key (`~/.ssh/id_rsa`) secure
- Never share or commit your private key
- The public key (`~/.ssh/id_rsa.pub`) is safe to share
- Consider using SSH key passphrases for additional security

## Quick One-Liner Setup
```bash
# Generate key and copy to Proxmox in one command
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" && ssh-copy-id root@192.168.0.19
```

## Verify Everything Works
After setup, these commands should work without passwords:
```bash
# Direct SSH
ssh root@192.168.0.19 hostname

# Ansible ping
make test-ping-proxmox

# Run Ansible playbooks
make proxmox-terraform-prep
```