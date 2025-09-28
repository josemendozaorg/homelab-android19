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
   make proxmox-tf-init
   ```

4. **Provision infrastructure with cloud-init:**
   ```bash
   make proxmox-tf-plan   # Show execution plan
   make proxmox-tf-apply  # Apply configuration
   ```

## Container Provisioning

This Terraform configuration uses cloud-init for initial container setup:

- **Container template**: Debian 12 standard LXC template
- **Cloud-init**: Handles SSH key setup and basic configuration
- **Infrastructure catalog**: Reads from `../infrastructure-catalog.yml` for service definitions
- **Self-contained**: No external Ansible preparation required

To modify containers:
1. Update service definitions in `../infrastructure-catalog.yml`
2. Set `provisioner: terraform` for containers you want Terraform to manage
3. Run `make proxmox-tf-plan` to see changes

## Container Management

The configuration provisions containers defined in the infrastructure catalog:
- Containers with `provisioner: terraform` are managed by this configuration
- Each container gets cloud-init setup with SSH keys
- Containers are automatically started and connectivity is verified
- Resources (CPU, memory, disk) are defined in the infrastructure catalog