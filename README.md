# HomeLab Android19

Named after the Dragon Ball character Android #19 - strong, smart, beautiful and powerful.

## Infrastructure

### Machine 1: Bastion Host Android #16
Old laptop configured with CloudFlare as gateway from internet to internal home lab.

### Machine 2: Main Server Android #19

#### Hardware Specs

**Core Components**
- **CPU**: AMD Ryzen 9 9950X3D AM5 5.7GHz - 3184 PLN - PURCHASED
- **GPU**: ZOTAC GAMING RTX 5060Ti 16GB TWIN EDGE DLSS 4 - 2116 PLN - PURCHASED
- **Motherboard**: ASUS PROART X870E-CREATOR WIFI - 2049 PLN - PURCHASED
- **RAM**: Kingston Fury Renegade RGB 96GB (2x48GB 6400MHz DDR5 CL32) - 1291 PLN - PURCHASED

**Storage**
- **OS Disk**: Samsung 990 Evo Plus 2TB (Proxmox) - 519 PLN - PURCHASED
- **VM Storage**: Samsung 990 Evo Plus 4TB M.2 PCIe - 1039 PLN - PURCHASED
- **Redundancy**: Samsung 990 Evo Plus 4TB M.2 PCIe - 1039 PLN - PLANNED

**Power & Cooling**
- **PSU**: Corsair HX1200i - 1958 PLN - PURCHASED
- **UPS**: APC Back-UPS Pro Gaming 2200VA 1320W - 1399 PLN - PURCHASED
- **Cooler**: ARCTIC Liquid Freezer III Pro 360 A-RGB - 429 PLN - PURCHASED
- **3 Fans**: Arctic P14 PWM PST A-RGB - 226 PLN - PURCHASED

**Case**
- **Chassis**: Lian Li O11 Dynamic EVO XL White - 997.60 PLN - PURCHASED

**Planned Additions**
- Terramaster D5 Hybrid NAS enclosure - Price TBD - PLANNED

## Repository Structure

- `android-16-bastion/` - Configuration and documentation for Android #16 bastion host
- `android-19-proxmox/` - Configuration and documentation for Android #19 Proxmox server
  - `provisioning-by-terraform/` - Infrastructure as Code for container/VM provisioning
  - `configuration-by-ansible/` - Ansible roles for service configuration
    - `host-*/` - Physical machine roles (host-proxmox)
    - `lxc-*/` - LXC container roles (lxc-adguard)
    - `vm-*/` - Virtual machine roles (vm-omarchy-dev)
  - `infrastructure-catalog.yml` - Service definitions and configuration

## Repository Content

This repository aims to contain:
- Hardware catalog
- Software catalog
- Configuration files
- Automation scripts
- Infrastructure as Code
- Home lab documentation

## Getting Started

### Prerequisites
1. Docker and Docker Compose installed
2. SSH key authentication to Proxmox (see [SSH Setup Guide](docs/SSH_SETUP.md))
3. Proxmox API token for Terraform

### Quick Start
```bash
# 1. Set up SSH keys (if not already done)
ssh-copy-id root@192.168.0.19

# 2. Build development environment
make env-setup

# 3. Test connectivity
make test-ping

# 4. Deploy everything (Terraform + Ansible)
make proxmox-full-deploy
```

### Troubleshooting
- **SSH Permission Denied**: See [SSH Setup Guide](docs/SSH_SETUP.md)
- **Terraform API Issues**: Check your API token in `android-19-proxmox/provisioning-by-terraform/terraform.tfvars`
- **Docker Issues**: Ensure Docker is running and you have proper permissions

## ⚠️ INFRASTRUCTURE SAFETY

### Network Configuration
**Network bridges are managed by Proxmox installation** - no Ansible configuration needed.

**Previous Issue**: Attempted to manage network configuration via Ansible, which caused complete remote lockout when interface names didn't match (assumed `eno1` vs actual `enp11s0/enp12s0`).

**Current Approach**: Let Proxmox handle network configuration during installation. The `vmbr0` bridge is created automatically and works correctly.

**Lesson**: Don't try to automate what's already working. Proxmox installation handles network setup properly.

### PCIe Network Card Stability

**Issue**: Intel network card (igc enp11s0) randomly disconnects from PCIe bus after several days of uptime, causing complete loss of connectivity.

**Symptoms**:
- Network card disappears from `ip link` output
- Kernel logs show: "PCIe link lost, device now detached"
- Requires physical console access to recover
- Complete loss of SSH and web UI access

**Solution**: Disable PCIe Active State Power Management (ASPM)

```bash
# Configure GRUB to disable PCIe ASPM
make proxmox-host-pcie-aspm
```

**What it does**:
- Adds `pcie_aspm=off` kernel boot parameter to GRUB configuration
- Creates timestamped backup of GRUB config before modification
- Idempotent - safe to run multiple times
- Displays reboot notification (manual reboot required)

**Verification** (after reboot):
```bash
# Check if parameter is active
cat /proc/cmdline | grep pcie_aspm=off
```

**Reference**: See [spec-proxmox-pcie-aspm-fix.md](specs/pcie-aspm-kernel-parameter/spec-proxmox-pcie-aspm-fix.md) for technical details.

### Safety Procedures

**1. Configuration Validation**
```bash
# Validate configuration without making changes
make proxmox-host-check                    # Check all host configuration
```

**2. Best Practices**
- Always run `make proxmox-host-check` first to validate changes
- Never disable preflight checks (`proxmox_preflight_checks: false`)
- Let Proxmox manage its own network configuration

## Architecture

### Infrastructure Management
This homelab uses a **service-oriented approach** with clear separation:

1. **Terraform** (`provisioning-by-terraform/`): Provisions infrastructure (containers, VMs, networking)
2. **Ansible** (`configuration-by-ansible/`): Configures services and applications
3. **Makefile**: Orchestrates services combining both Terraform and Ansible

### Naming Conventions

#### Ansible Role Naming
All Ansible roles follow a prefixed naming pattern:
- **host-*** - Physical machine roles (e.g., host-proxmox)
- **lxc-*** - LXC container roles (e.g., lxc-adguard)
- **vm-*** - Virtual machine roles (e.g., vm-omarchy-dev)

#### Makefile Target Naming
Service deployment targets follow a structured naming pattern:
- **deploy-{type}-{name}-{capability}** - Complete orchestration (Terraform + Ansible)
  - `{type}` = `lxc` or `vm` (infrastructure type)
  - `{name}` = Service name (e.g., adguard, omarchy)
  - `{capability}` = Homelab function (e.g., dns, devmachine, vpn, containerplatform)

**Examples:**
- `deploy-lxc-adguard-dns` - AdGuard DNS server running in LXC container
- `deploy-vm-omarchy-devmachine` - Omarchy development workstation running in VM
- `deploy-lxc-nextcloud-fileserver` - Nextcloud file server in LXC container
- `deploy-vm-docker-containerplatform` - Docker host VM for containers

### Container Management
Ansible manages LXC containers through Proxmox, not direct SSH:

```
[Ansible] → SSH → [Proxmox Host] → pct exec → [Container]
                  (192.168.0.19)              (125, 130, etc.)
```

**Why this approach?**
- **Lightweight**: Containers don't need SSH servers
- **Secure**: No SSH key management per container
- **Native**: Uses Proxmox's built-in container tools
- **Simple**: One SSH connection manages all containers

### Workflow

**One-Command Deployment:**
```bash
make proxmox-full-deploy  # Does everything: Terraform + Ansible
```

**Service-Level Deployment:**
```bash
# Deploy individual services (Terraform + Ansible)
make deploy-lxc-adguard-dns        # AdGuard DNS server (LXC)
make deploy-vm-omarchy-devmachine   # Omarchy development workstation (VM)

# Deploy all services
make deploy-proxmox-all
```

**Step-by-Step Workflow:**
```bash
# 1. Setup Proxmox host infrastructure
make proxmox-host-setup

# 2. Provision infrastructure
make proxmox-tf-apply

# 3. Configure services
make proxmox-services

# 4. Validate deployment
make test-ping
```