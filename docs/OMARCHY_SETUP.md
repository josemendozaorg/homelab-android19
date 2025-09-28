# Omarchy Development VM Setup Guide

## Overview

This guide covers the deployment of an Omarchy (Arch Linux + Hyprland) development VM on the Proxmox server. Omarchy is an opinionated setup that provides a fully-configured development environment with a tiling window manager.

## Prerequisites

- Working Proxmox server (Android #19)
- SSH access to Proxmox configured (`make setup-ssh`)
- Development environment running (`make env-setup`)
- At least 60GB free storage on Proxmox
- 8GB+ RAM available for the VM

## Quick Start

```bash
# Complete deployment (ISO download + VM provisioning)
make omarchy-full-deploy

# After manual OS installation, configure the VM
make omarchy-configure
```

## Detailed Setup Process

### 1. Download Omarchy ISO to Proxmox

```bash
make omarchy-iso-setup
```

This downloads the Omarchy ISO (1.4GB) from https://iso.omarchy.org/ to the Proxmox ISO storage.

### 2. Plan Infrastructure Changes

```bash
make omarchy-tf-plan
```

Review the planned VM creation with:
- VM ID: 101
- IP: 192.168.0.101
- Resources: 4 cores, 8GB RAM, 60GB disk
- UEFI boot with q35 chipset

### 3. Provision the VM

```bash
make omarchy-tf-apply
```

This creates the VM in Proxmox with the ISO mounted for installation.

### 4. Manual OS Installation

1. Access Proxmox web UI at https://192.168.0.19:8006
2. Select VM 101 (omarchy-dev)
3. Open Console
4. Start the VM
5. Follow Omarchy installation wizard:
   - Select installation type
   - Configure disk partitioning
   - Set up user account
   - Complete installation

**Important Notes:**
- Disable Secure Boot and TPM in BIOS if needed
- The installation process is interactive
- Network will be configured via cloud-init (192.168.0.101)

### 5. Post-Installation Configuration

After OS installation completes:

```bash
make omarchy-configure
```

This will:
- Ensure VM is running
- Install QEMU guest agent (if possible)
- Configure hardware optimizations
- Set up backup schedule

## VM Management

### Check VM Status

```bash
# Via Proxmox host
ssh proxmox@192.168.0.19 "qm status 101"
```

### Access the VM

```bash
# SSH (after installation)
ssh user@192.168.0.101

# Proxmox console
# Access via web UI at https://192.168.0.19:8006
```

### Start/Stop VM

```bash
# Start
ssh proxmox@192.168.0.19 "qm start 101"

# Stop
ssh proxmox@192.168.0.19 "qm stop 101"
```

### Destroy VM

```bash
# Remove VM and reclaim resources
make omarchy-destroy
```

## Architecture Details

### Infrastructure Definition

The VM is defined in `android-19-proxmox/infrastructure-catalog.yml`:
- ID: 101 (matching IP last octet)
- Type: VM (not container)
- Network: 192.168.0.101/24

### Terraform Provisioning

Located in `android-19-proxmox/terraform/main.tf`:
- Resource: `proxmox_virtual_environment_vm`
- Configured for UEFI boot
- Virtio network driver for performance
- QXL graphics for desktop environment

### Ansible Configuration

Two playbooks handle setup:
- `omarchy-setup.yml`: ISO download to Proxmox
- `omarchy-configure.yml`: Post-installation optimization

## Troubleshooting

### ISO Download Issues

If ISO download fails:
```bash
# Manual download on Proxmox
ssh proxmox@192.168.0.19
cd /var/lib/vz/template/iso/
wget https://iso.omarchy.org/omarchy-online.iso
```

### VM Won't Start

Check BIOS settings:
- Secure Boot: Must be disabled
- TPM: Must be disabled
- Virtualization: Must be enabled

### Network Issues

Verify network configuration:
```bash
# Check IP assignment
ssh proxmox@192.168.0.19 "qm guest cmd 101 network-get-interfaces"

# Check cloud-init status
ssh proxmox@192.168.0.19 "qm cloudinit dump 101 network"
```

### Installation Fails

Common issues:
- Insufficient disk space (needs 60GB)
- Memory allocation failed (needs 8GB)
- ISO corrupted (re-download with `make omarchy-iso-setup`)

## Customization

### Modify VM Resources

Edit `android-19-proxmox/infrastructure-catalog.yml`:
```yaml
101:
  name: "omarchy-dev"
  resources:
    cores: 6      # Increase CPU cores
    memory: 16384 # Increase RAM (MB)
    disk: 100     # Increase disk (GB)
```

Then apply changes:
```bash
make omarchy-tf-apply
```

### Custom Omarchy Build

For a custom Omarchy installation, you can build your own ISO:
```bash
# On a Linux system with Docker
git clone https://github.com/omacom-io/omarchy-iso
cd omarchy-iso
OMARCHY_INSTALLER_REF="custom-branch" ./bin/omarchy-iso-make
```

## References

- [Omarchy Official Site](https://omarchy.org/)
- [Omarchy GitHub](https://github.com/basecamp/omarchy)
- [Omarchy Manual](https://learn.omacom.io/2/the-omarchy-manual)
- [Hyprland Documentation](https://wiki.hyprland.org/)
- [Arch Linux Wiki](https://wiki.archlinux.org/)

## Support

For issues specific to this homelab setup:
- Check logs: `make env-shell` then examine Ansible output
- Verify connectivity: `make test-ping`
- Review Terraform state: `make omarchy-tf-plan`

For Omarchy-specific issues:
- [Omarchy Discussions](https://github.com/basecamp/omarchy/discussions)
- [Omarchy Issues](https://github.com/basecamp/omarchy/issues)