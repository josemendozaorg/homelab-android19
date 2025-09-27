# Terraform Configuration for Proxmox

This directory contains Terraform configuration for provisioning VMs and containers on Proxmox.

## Setup

1. **Copy configuration template:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Configure your Proxmox API token in terraform.tfvars**

3. **Verify LXC template exists in Proxmox:**
   ```bash
   # SSH to Proxmox server and check available templates
   pveam list local

   # If template doesn't exist, download it:
   pveam update
   pveam download local debian-12-standard_12.12-1_amd64.tar.zst
   ```

4. **Initialize and apply:**
   ```bash
   make tf-init
   make tf-plan
   make tf-apply
   ```

## Template Management

The default LXC template is `debian-12-standard_12.12-1_amd64.tar.zst` (matches the existing AdGuard container).

To use a different template:
1. Check what's available: `pveam list local`
2. Update `lxc_template` variable in your `terraform.tfvars`
3. Re-run `make tf-plan` to verify changes

## Test Container

The current configuration creates a test nginx container:
- **VM ID**: 130
- **IP**: 192.168.0.30
- **Hostname**: test-nginx
- **Resources**: 1 core, 512MB RAM

This can be used to verify the Terraform → Ansible workflow before migrating production services.