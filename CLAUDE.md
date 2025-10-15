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
- `make proxmox-host-setup` - Configure Proxmox host infrastructure
- `make proxmox-deploy` - Deploy base configuration to Android #19 Proxmox
- `make proxmox-services` - Deploy all Proxmox services

### Service-Level Deployment (Terraform + Ansible)
- `make deploy-lxc-adguard-dns` - Deploy AdGuard DNS server (LXC container)
- `make deploy-vm-omarchy-devmachine` - Deploy Omarchy development workstation (VM)
- `make deploy-proxmox-all` - Deploy all Proxmox VMs and LXCs

### Proxmox Infrastructure (Terraform)
- `make proxmox-tf-init` - Initialize Terraform for Proxmox
- `make proxmox-tf-plan` - Show execution plan for Proxmox infrastructure
- `make proxmox-tf-apply` - Apply Terraform configuration for Proxmox
- `make proxmox-tf-destroy` - Destroy Terraform-managed infrastructure
- `make proxmox-tf-show` - Show current state and outputs
- `make proxmox-tf-rebuild-state` - Rebuild state by importing existing infrastructure

### Complete Deployment
- `make proxmox-full-deploy` - **Complete end-to-end deployment: Terraform + Ansible**

## Architecture

### Directory Structure
- `android-16-bastion/` - Bastion host configuration and Ansible playbooks
- `android-19-proxmox/` - Proxmox server configuration with separated concerns
  - `provisioning-by-terraform/` - Infrastructure as Code for VM/container provisioning
  - `configuration-by-ansible/` - Ansible roles for service configuration
    - `host-*/` - Physical machine roles (host-proxmox)
    - `lxc-*/` - LXC container roles (lxc-adguard)
    - `vm-*/` - Virtual machine roles (vm-omarchy-dev)
  - `infrastructure-catalog.yml` - Service definitions and configuration
- `scripts/` - Helper scripts (SSH setup, etc.)
- `docs/` - Documentation including SSH setup guide

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

### Infrastructure Flow
1. **Terraform Provisioning**: Create VMs/containers on Proxmox with cloud-init
2. **Ansible Configuration**: Install software, configure services on each machine
3. **Validation**: Test connectivity and service availability

### Key Technologies
- **Docker/Docker Compose**: Development environment containerization
- **Ansible**: Configuration management (machine-specific only)
  - **Execution Method**: Connects to Proxmox host via SSH, uses `pct exec` commands to run tasks inside containers
  - **Container Management**: `ansible → ssh proxmox → pct exec container_id -- command`
  - **Benefits**: No SSH servers needed in containers, lightweight, uses Proxmox native management
- **Terraform**: Infrastructure provisioning with initialization
  - **LXC containers**: Uses Proxmox container initialization (SSH keys, user accounts)
  - **VMs**: Uses full cloud-init (custom scripts, packages, services)
- **Proxmox**: Virtualization platform for VMs and LXC containers
  - **Storage**: ZFS pool on 4TB NVMe disk for VM/container storage
  - **Benefits**: Compression, snapshots, data integrity, performance

## Important Files
- `Makefile` - Main automation interface with all commands
- `inventory.yml` - Ansible inventory defining machine groups
- `docker-compose.yml` - Development environment definition
- `android-19-proxmox/provisioning-by-terraform/terraform.tfvars` - Terraform configuration (not committed)
- `android-19-proxmox/infrastructure-catalog.yml` - Service definitions for Terraform
- `docs/SSH_SETUP.md` - Comprehensive SSH authentication setup guide

## SSH Authentication
SSH key authentication is required for Ansible to communicate with both machines. If you encounter "Permission denied" errors, run `make setup-ssh` or follow the detailed guide in `docs/SSH_SETUP.md`.

## ⚠️ CRITICAL WARNING: Network Configuration
**NEVER run network configuration tasks on production Proxmox hosts without extreme caution!**

### What Happened (Lesson Learned)
The Ansible network configuration in `host-proxmox/tasks/network.yml` overwrites `/etc/network/interfaces` with a template. This caused complete loss of SSH and web access because:

1. **Template Assumptions**: The template assumes specific interface names (e.g., `eno1`) that may not exist
2. **No Validation**: No verification that the new config matches existing working setup
3. **Immediate Apply**: Network restart happens immediately, breaking connectivity if config is wrong
4. **Complete Lockout**: Both SSH (port 22) and web UI (port 8006) become unreachable

### Current Status
Network configuration is **DISABLED** in `host-proxmox/tasks/main.yml` (when: false) to prevent this issue.

### Recovery Procedure
If network access is lost, **physical console access is required**:

```bash
# 1. Check what interfaces actually exist
ip link show

# 2. Restore from Ansible backup (if available)
ls /etc/network/interfaces.*
cp /etc/network/interfaces.backup /etc/network/interfaces

# 3. Restart networking
systemctl restart networking

# 4. If backup doesn't work, manually configure
nano /etc/network/interfaces
# Add working configuration based on actual interface names
```

### Safe Network Configuration
Before enabling network configuration:
1. **Always check existing interface names**: `ip link show`
2. **Update defaults to match reality**: Edit `host-proxmox/defaults/main.yml`
3. **Test in non-production first**: Use a test VM
4. **Have console access ready**: Physical or IPMI access

## Container Management Architecture

### Ansible Execution Method
Ansible does NOT connect directly to containers. Instead, it uses Proxmox as a proxy:

```
[Ansible] → SSH → [Proxmox Host] → pct exec → [Container]
            (192.168.0.19)                     (125, 130, etc.)
```

**Command Flow Example:**
```bash
# Ansible runs this on the Proxmox host:
pct exec 125 -- systemctl status AdGuardHome

# Which executes inside container 125:
systemctl status AdGuardHome
```

**Benefits of this approach:**
- **Lightweight containers**: No SSH servers required in each container
- **Security**: No need to manage SSH keys per container
- **Proxmox integration**: Uses native `pct` container management
- **Simplicity**: Single SSH connection to Proxmox manages all containers

## Terraform Initialization Strategy

### LXC Containers (current)
- Uses Proxmox's built-in container initialization
- Limited to SSH keys, user accounts, network configuration
- Ansible handles all software installation and service configuration

### VMs (future)
- Use full cloud-init with user-data scripts
- Can handle package installation, service setup, custom scripts
- Still use Ansible for complex configuration management

## Terraform State Recovery

If you lose your Terraform state file, you can rebuild it automatically:

### Recovery Process
```bash
# 1. Rebuilds state by importing existing infrastructure
make proxmox-tf-rebuild-state

# 2. Verify what will be changed/created
make proxmox-tf-plan

# 3. Apply if everything looks correct
make proxmox-tf-apply
```

### How it works
- Reads `infrastructure-catalog.yml` to know what should exist
- Checks what actually exists on Proxmox via SSH
- Imports existing containers into Terraform state
- Creates automatic backup of any existing state file

### Requirements
- SSH access to Proxmox must be working (`make setup-ssh`)
- Python3 with PyYAML for parsing the infrastructure catalog
- Infrastructure catalog must be up to date

## Testing

### Test Organization
Tests are located in `android-19-proxmox/tests/`:
- `tests/unit/` - Unit tests for Ansible role structure and configuration validation
- `tests/conftest.py` - Shared pytest fixtures (project_root, catalog, etc.)

### Running Tests

**Run all unit tests:**
```bash
cd android-19-proxmox
python -m pytest tests/unit/ -v
```

**Run specific test file:**
```bash
python -m pytest tests/unit/test_grub_pcie_aspm.py -v
```

**Run specific test:**
```bash
python -m pytest tests/unit/test_grub_pcie_aspm.py::test_pcie_aspm_task_files_exist -v
```

### Test Environment Setup

Tests require Python dependencies installed:
```bash
pip install pytest pyyaml requests
```

**Docker-based testing (recommended):**
The development container includes all test dependencies. Use it for consistent test execution:
```bash
# Enter development container
make env-shell

# Run tests inside container
cd android-19-proxmox
python -m pytest tests/unit/ -v
```

### Integration Testing with Docker

The Docker development environment provides:
- **Isolated testing environment**: All dependencies pre-installed (pytest, ansible, terraform)
- **SSH key mounting**: Your `~/.ssh` keys are mounted read-only for Ansible connectivity tests
- **Docker socket access**: For molecule-based integration tests (future)
- **Consistent Python environment**: Virtual environment at `/opt/venv` with all packages

**Key Docker features for testing:**
- `molecule` and `molecule-docker` installed for Ansible role testing
- Can run integration tests that spin up containers
- Ansible and all required Python libraries available

## Development Workflow

### Quick Start (Complete Deployment)
1. Set up environment: `make env-setup`
2. Test connectivity: `make test-ping`
3. **Deploy everything**: `make proxmox-full-deploy`
4. Validate deployment: `make test-ping`

### Step-by-Step Workflow
1. Set up environment: `make env-setup`
2. Test connectivity: `make test-ping`
3. Make configuration changes in appropriate machine directories
4. Deploy to specific machines: `make bastion-deploy` or `make proxmox-deploy`
5. For infrastructure changes: `make proxmox-tf-plan` → `make proxmox-tf-apply`
6. Validate with: `make test-ping` or service-specific tests

## TDD Development Example

This project follows strict Test-Driven Development (TDD) practices with small, testable incremental changes.

### Example: Fixing Hardcoded SSH Key Security Issue

**Problem:** SSH key was hardcoded in `defaults/main.yml` (security risk)

**TDD Workflow (2 commits):**

#### Commit 1: Document Issue with Failing Test
```python
# tests/unit/test_playbooks.py
@pytest.mark.xfail(reason="Known issue: SSH key is currently hardcoded")
def test_ubuntu_desktop_no_hardcoded_ssh_key(project_root):
    """SSH public key should not be hardcoded in defaults file."""
    # Test that validates security issue
    assert not ssh_key.startswith('ssh-rsa'), "Key should not be hardcoded"
```
- Test: `make test-unit` → **17 passed, 1 xfailed**
- Documents the security issue
- Specifies what "fixed" means

#### Commit 2: Fix Issue, Test Passes
```yaml
# defaults/main.yml - Before
ssh_public_key: "ssh-rsa AAAA...hardcoded..."

# defaults/main.yml - After
ssh_public_key: "{{ lookup('file', lookup('env', 'HOME') + '/.ssh/id_rsa.pub') }}"
```
- Test: `make test-unit` → **18 passed, 0 xfailed**
- Security issue fixed
- Test validates the fix automatically

**Benefits of this approach:**
- ✅ **Small changes:** Each commit is tiny and focused
- ✅ **Always testable:** Every change has automated validation
- ✅ **Documents intent:** Test shows what should happen
- ✅ **Safe refactoring:** Test catches regressions
- ✅ **Clear history:** Git log shows problem → solution

**Key Principles:**
1. **One small change at a time** (strict requirement)
2. **Test first** (or document with xfail)
3. **Automated validation** (`make test-unit`)
4. **Commit immediately** after each small working step
5. **Never skip tests** - they prevent future breakage

### TDD Workflow Enforcement

When using the `/tdd` workflow commands, follow the **8-step mandatory process**:

1. **Choose Task** - Select smallest testable unit
2. **Design Solution** - List all assumptions, get user confirmation
3. **Write Failing Test** (RED) - Test must fail initially
4. **Implement Minimum Code** (GREEN) - Only enough to pass test
5. **Verify Test Passes** - Run unit tests AND integration tests
6. **Run Full Test Suite** - Ensure no regressions
7. **Refactor** (if needed) - Improve code while tests pass
8. **Commit Changes** - Atomic commit with clear message

**Critical Validation Checkpoints:**

At Step 5, you MUST verify:
```
- [ ] Integration tests have been identified or created
- [ ] Integration tests have been executed
- [ ] ALL integration tests PASS

IF no integration tests exist and none were created: STOP. Create at least one integration test.
```

**Integration Tests vs Unit Tests:**
- **Unit tests**: Validate file structure, YAML syntax, module usage (structural validation)
- **Integration tests**: Verify actual execution, Ansible playbook loading, end-to-end workflows

**Common mistake to avoid:**
Do NOT treat structural YAML validation as "integration tests". True integration tests should:
- Run `ansible-playbook --syntax-check` on the role
- Test actual Ansible execution context
- Verify task orchestration and dependencies
- Use Docker/molecule for isolated testing environments

**If integration tests are missing:**
Use the Docker development environment with molecule to create proper integration tests:
```bash
# Enter container
make env-shell

# Create molecule scenario
cd android-19-proxmox/configuration-by-ansible/host-proxmox
molecule init scenario --driver-name docker

# Run integration tests
molecule test
```