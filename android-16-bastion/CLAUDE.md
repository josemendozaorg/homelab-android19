# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Context

This is the Android #16 Bastion Host configuration repository, part of a larger homelab infrastructure. Android #16 serves as the secure gateway from the internet to the internal network, configured with CloudFlare for external access.

## Infrastructure Overview

The bastion host is part of a two-machine setup:
- **Android #16 (this repo)**: Bastion host at 192.168.0.10, accessed as user `josemendoza`
- **Android #19**: Main Proxmox server at 192.168.0.19, accessed as user `root`

The parent repository contains Docker-based Ansible development environment for managing both machines.

## Development Commands

All commands should be run from the parent directory (`../`) using Make:

### Environment Setup
```bash
make env-setup              # Build and start Docker development environment
make env-shell              # Open interactive shell in development container
make env-clean              # Clean up Docker resources
```

### Testing Connectivity
```bash
make test-ping-bastion      # Test connection to this bastion host
make test-ping              # Test connection to all machines
```

### Bastion-Specific Commands
```bash
make bastion-setup-sudo     # Configure passwordless sudo (run once, requires password)
make bastion-deploy         # Deploy configuration to bastion host
```

## Architecture

### Ansible Playbooks
- `playbook.yml`: Main configuration playbook for bastion host
  - Sets hostname to `android16-bastion`
  - Basic connectivity tests

- `setup.yml`: Initial setup playbook
  - Configures passwordless sudo for the ansible user
  - Run with `make bastion-setup-sudo` from parent directory

### Inventory Configuration
The bastion host is configured in `../inventory.yml` as:
- Group: `bastion`
- Hostname: `android16`
- IP: `192.168.0.10`
- User: `josemendoza`

## Development Workflow

1. Make changes to playbooks in this directory
2. Test syntax: `make env-check` (from parent directory)
3. Test connectivity: `make test-ping-bastion`
4. Deploy changes: `make bastion-deploy`

## Key Notes

- All Ansible operations run through Docker containers defined in parent directory
- The development environment handles SSH key management automatically
- Bastion host acts as the secure entry point to the internal network
- CloudFlare integration is configured separately (not in these playbooks)