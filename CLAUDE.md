# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a homelab infrastructure management repository for a two-machine setup:
- **Android #16**: Bastion host (old laptop with CloudFlare gateway)
- **Android #19**: Main Proxmox server (high-end AMD Ryzen 9950X3D system)

The project uses Infrastructure as Code principles with Docker, Ansible, and Terraform for automated deployment and configuration management.

## Development Environment

### Prerequisites
- Docker and Docker Compose
- SSH key authentication to Proxmox (see `docs/SSH_SETUP.md`)
- Proxmox API token for Terraform

### Setup Commands
```bash
# Build and start development environment
make env-setup

# Open interactive shell in container
make env-shell

# Test connectivity to all machines
make test-ping

# Set up SSH key authentication
make setup-ssh
```

## Common Commands

### Environment Management
- `make env-setup` - Build and start development environment
- `make env-shell` - Open interactive shell in development container
- `make env-clean` - Stop containers and clean Docker resources
- `make env-check` - Validate Ansible configuration

### Testing & Connectivity
- `make test-ping` - Test connection to all machines
- `make test-ping-bastion` - Test bastion host only
- `make test-ping-proxmox` - Test Proxmox server only

### Machine-Specific Deployment
- `make bastion-deploy` - Deploy configuration to Android #16 bastion
- `make proxmox-deploy` - Deploy base configuration to Android #19 Proxmox
- `make proxmox-services` - Deploy all Proxmox services
- `make proxmox-adguard` - Deploy AdGuard Home service only

### Proxmox Infrastructure (Terraform)
- `make proxmox-tf-init` - Initialize Terraform for Proxmox
- `make proxmox-tf-plan` - Show execution plan for Proxmox infrastructure
- `make proxmox-tf-apply` - Apply Terraform configuration for Proxmox
- `make proxmox-tf-destroy` - Destroy Terraform-managed infrastructure
- `make proxmox-tf-show` - Show current state and outputs

## Architecture

### Directory Structure
- `android-16-bastion/` - Bastion host configuration and Ansible playbooks
- `android-19-proxmox/` - Proxmox server configuration, Ansible playbooks, and Terraform
  - `terraform/` - Infrastructure as Code for VM/container provisioning
  - `infrastructure-catalog.yml` - Service definitions and configuration
- `scripts/` - Helper scripts (SSH setup, etc.)
- `docs/` - Documentation including SSH setup guide

### Infrastructure Flow
1. **Terraform Provisioning**: Create VMs/containers on Proxmox with cloud-init
2. **Ansible Configuration**: Install software, configure services on each machine
3. **Validation**: Test connectivity and service availability

### Key Technologies
- **Docker/Docker Compose**: Development environment containerization
- **Ansible**: Configuration management (machine-specific only)
- **Terraform**: Infrastructure provisioning with cloud-init
- **Proxmox**: Virtualization platform for VMs and LXC containers

## Important Files
- `Makefile` - Main automation interface with all commands
- `inventory.yml` - Ansible inventory defining machine groups
- `docker-compose.yml` - Development environment definition
- `android-19-proxmox/terraform/terraform.tfvars` - Terraform configuration (not committed)
- `android-19-proxmox/infrastructure-catalog.yml` - Service definitions for Terraform
- `docs/SSH_SETUP.md` - Comprehensive SSH authentication setup guide

## SSH Authentication
SSH key authentication is required for Ansible to communicate with both machines. If you encounter "Permission denied" errors, run `make setup-ssh` or follow the detailed guide in `docs/SSH_SETUP.md`.

## Development Workflow
1. Set up environment: `make env-setup`
2. Test connectivity: `make test-ping`
3. Make configuration changes in appropriate machine directories
4. Deploy to specific machines: `make bastion-deploy` or `make proxmox-deploy`
5. For infrastructure changes: `make proxmox-tf-plan` → `make proxmox-tf-apply`
6. Validate with: `make test-ping` or service-specific tests