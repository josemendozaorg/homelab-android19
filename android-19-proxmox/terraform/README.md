# Terraform Configuration for Proxmox

This directory contains Terraform configuration for provisioning VMs and containers on Proxmox.

## Setup

1. **Copy configuration template:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Configure your Proxmox API token in terraform.tfvars**

3. **Initialize Terraform:**
   ```bash
   make tf-init
   ```

4. **Provision infrastructure** (Ansible will automatically prepare Proxmox):
   ```bash
   make tf-plan   # Includes Ansible prep + Terraform plan
   make tf-apply  # Includes Ansible prep + Terraform apply
   ```

## Template Management

Templates are automatically managed by Ansible before Terraform runs:

- **Ansible playbook** `android-19-proxmox/terraform-prep.yml` handles template downloads
- **Default template**: `debian-12-standard_12.12-1_amd64.tar.zst` (matches existing AdGuard container)
- **Automatic download**: Templates are downloaded if not present when running `make tf-plan` or `make tf-apply`

To use a different template:
1. Update `lxc_template` variable in your `terraform.tfvars`
2. Modify `terraform-prep.yml` to download the required template
3. Re-run `make tf-plan` to verify changes

## Test Container

The current configuration creates a test nginx container:
- **VM ID**: 130
- **IP**: 192.168.0.30
- **Hostname**: test-nginx
- **Resources**: 1 core, 512MB RAM

This can be used to verify the Terraform → Ansible workflow before migrating production services.