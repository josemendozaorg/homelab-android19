# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in the android-19-proxmox directory.

## ⚠️ CRITICAL: Docker Execution Environment

**ALL deployment commands MUST run through the Makefile with Docker.**

The development container provides:
- All dependencies (Ansible, Terraform, Python, pytest)
- Mounted SSH keys for authentication
- Consistent execution environment
- Proper tool versions

**Correct workflow:**
```bash
# From repository root - ALWAYS use Makefile
make deploy-lxc-adguard-dns
make proxmox-tf-plan
make test-unit

# OR use interactive shell for exploration
make env-shell
# Now inside container:
cd android-19-proxmox
python -m pytest tests/unit/ -v
```

**NEVER run commands directly on host machine:**
```bash
# ❌ WRONG - Missing dependencies, wrong environment
terraform apply
ansible-playbook playbook.yml
pytest tests/
```

## Directory Overview

This directory manages the Android #19 Proxmox server (192.168.0.19) using a two-layer architecture:
1. **Terraform** - Infrastructure provisioning (creating VMs/containers)
2. **Ansible** - Service configuration (installing software, configuring services)

## Directory Structure

```
android-19-proxmox/
├── provisioning-by-terraform/     # Layer 1: Infrastructure as Code
│   ├── main.tf                     # VM/container definitions
│   ├── providers.tf                # Proxmox provider config
│   ├── rebuild-state.sh            # State recovery script
│   └── terraform.tfvars            # API credentials (not committed)
├── configuration-by-ansible/       # Layer 2: Service configuration
│   ├── host-*/                     # Physical machine roles
│   ├── lxc-*/                      # LXC container roles
│   ├── vm-*/                       # Virtual machine roles
│   └── *.yml                       # Playbooks for each service
├── tests/                          # Test organization
│   ├── unit/                       # Role structure validation
│   ├── integration/                # Ansible playbook execution tests
│   └── bdd/                        # Acceptance tests
├── infrastructure-catalog.yml      # Single source of truth
├── pytest.ini                      # Test configuration
└── specs/                          # Feature specifications
```

## Infrastructure Catalog

**File:** `infrastructure-catalog.yml`

The catalog is the **single source of truth** for all infrastructure:
- Service IDs (container/VM IDs)
- IP addresses
- Resource allocations (CPU, RAM, disk)
- Service types and descriptions

**Network Strategy:**
- Containers: 192.168.0.20-99 (ID matches IP last octet)
- VMs: 192.168.0.100-199 (ID matches IP last octet)
- DHCP pool: 192.168.0.200-249

**Usage Pattern:**
```yaml
# All roles reference the catalog
vars_files:
  - "../infrastructure-catalog.yml"

# Access service info
{{ catalog.services[125].ip }}      # AdGuard DNS IP
{{ catalog.services[140].name }}    # VM name
```

## Role Naming Conventions

All Ansible roles use prefixed naming:
- **host-*** - Physical machine roles (e.g., `host-proxmox`, `host-proxmox-gpu-passthrough`)
- **lxc-*** - LXC container roles (e.g., `lxc-adguard`)
- **vm-*** - Virtual machine roles (e.g., `vm-llm-aimachine`, `vm-coolify`)

**Playbook naming:** `{service-name}-setup.yml` (e.g., `adguard-setup.yml`)

## Adding New Services

### 1. Update Infrastructure Catalog
```yaml
# infrastructure-catalog.yml
services:
  135:  # Choose unused ID matching IP last octet
    name: "myservice"
    type: "container"  # or "vm"
    ip: "192.168.0.35"
    description: "My new service"
    template: "debian-12-standard_12.12-1_amd64.tar.zst"
    resources:
      cores: 2
      memory: 2048
      disk: 32
    storage: "vm-storage"
```

### 2. Provision with Terraform
```bash
# From repository root - use Makefile
make proxmox-tf-plan   # Review changes
make proxmox-tf-apply  # Create infrastructure

# Terraform commands shown for reference (run inside Docker container only):
# cd provisioning-by-terraform
# terraform plan
# terraform apply
```

### 3. Create Ansible Role
```bash
# Create role structure (can do on host or in container)
cd android-19-proxmox/configuration-by-ansible
mkdir -p lxc-myservice/{tasks,defaults,templates}
```

**Role structure:**
- `tasks/main.yml` - Task definitions
- `defaults/main.yml` - Default variables
- `templates/` - Jinja2 templates

### 4. Create Playbook
```yaml
# configuration-by-ansible/myservice-setup.yml
---
- name: Configure My Service
  hosts: proxmox

  vars_files:
    - "../infrastructure-catalog.yml"

  roles:
    - lxc-myservice
```

### 5. Add Makefile Target
```makefile
# In root Makefile
deploy-lxc-myservice-capability: proxmox-tf-init ## Deploy MyService (LXC container)
	@echo "🚀 Deploying MyService..."
	$(DOCKER_RUN) terraform -chdir=android-19-proxmox/provisioning-by-terraform apply -auto-approve
	$(DOCKER_RUN) ansible-playbook --inventory inventory.yml android-19-proxmox/configuration-by-ansible/myservice-setup.yml
```

### 6. Add Tests
```python
# tests/unit/test_myservice.py
def test_myservice_role_structure(project_root):
    """Validate role structure exists."""
    role_path = project_root / "configuration-by-ansible/lxc-myservice"
    assert role_path.exists()
    assert (role_path / "tasks/main.yml").exists()
```

### 7. Deploy
```bash
# From repository root - ALWAYS use Makefile
make deploy-lxc-myservice-capability
```

## Testing

### Test Organization
- **Unit tests** (`tests/unit/`) - Role structure, YAML syntax, configuration validation
- **Integration tests** (`tests/integration/`) - Ansible playbook execution, task orchestration
- **BDD tests** (`tests/bdd/`) - End-to-end acceptance tests

### Running Tests

**Preferred method - Use Makefile (runs in Docker):**
```bash
# From repository root
make test-unit       # Run all unit tests
make test-catalog    # Validate infrastructure catalog
make test-all        # Run all tests (unit + connectivity)
```

**Alternative - Interactive shell for test development:**
```bash
# Enter development container
make env-shell

# Now inside container with all dependencies:
cd android-19-proxmox

# All unit tests
python -m pytest tests/unit/ -v

# Specific test file
python -m pytest tests/unit/test_grub_pcie_aspm.py -v

# By marker (see pytest.ini for all markers)
python -m pytest -m "unit and adguard"
python -m pytest -m "integration and gpu"
python -m pytest -m "bdd and coolify"

# Validate infrastructure catalog
python -m pytest -m catalog
```

**NEVER run pytest directly on host** - dependencies may be missing or versions incompatible.

### Test Markers
Common markers defined in `pytest.ini`:
- `unit`, `integration`, `bdd` - Test type
- `terraform`, `ansible` - Tool-specific tests
- `adguard`, `coolify`, `gpu`, `dhcp` - Service-specific tests
- `slow`, `deployment` - Performance classification
- `safe`, `network_critical` - Safety classification

## Terraform Operations

### Common Commands (from repository root)
```bash
make proxmox-tf-init      # Initialize Terraform
make proxmox-tf-plan      # Show execution plan
make proxmox-tf-apply     # Apply changes
make proxmox-tf-destroy   # Destroy infrastructure
make proxmox-tf-show      # Show current state
```

### State Recovery
If Terraform state is lost:
```bash
make proxmox-tf-rebuild-state  # Automatically rebuild state
make proxmox-tf-plan           # Verify state
```

The rebuild script:
- Reads `infrastructure-catalog.yml`
- Checks existing infrastructure on Proxmox
- Imports resources into state
- Creates automatic backups

## Ansible Execution Model

### Container Management
Ansible does NOT SSH directly to containers. It uses Proxmox as a proxy:

```
[Ansible] → SSH → [Proxmox Host] → pct exec → [Container]
            192.168.0.19                       (125, 130, etc.)
```

**Example:**
```bash
# Ansible executes on Proxmox host:
pct exec 125 -- systemctl status AdGuardHome

# Which runs inside container 125
```

**Benefits:**
- No SSH servers in containers
- Single SSH connection manages all containers
- Uses Proxmox native `pct` commands

### VM Management
VMs are configured via SSH after cloud-init or manual setup completes.

## Development Workflow

### Step-by-Step Process
1. **Update catalog** - Add/modify service definition in `infrastructure-catalog.yml`
2. **Write test** - Create failing test documenting expected behavior
3. **Provision** - Use Makefile to run Terraform (in Docker)
4. **Configure** - Create/update Ansible role and playbook
5. **Test** - Verify with unit and integration tests (via Makefile)
6. **Deploy** - Run complete deployment via Makefile target

### Example: Adding LXC Container

**IMPORTANT: All commands use Makefile or run inside Docker container.**

```bash
# 1. Edit infrastructure-catalog.yml (add service definition)
vim android-19-proxmox/infrastructure-catalog.yml

# 2. Write test (can do on host or in container)
vim android-19-proxmox/tests/unit/test_mynewservice.py

# 3. Run test to verify it fails (use Docker)
make env-shell
# Inside container:
cd android-19-proxmox
python -m pytest tests/unit/test_mynewservice.py -v  # Should fail
exit

# 4. Create role and playbook (on host is fine for file creation)
mkdir -p android-19-proxmox/configuration-by-ansible/lxc-mynewservice/{tasks,defaults}
vim android-19-proxmox/configuration-by-ansible/lxc-mynewservice/tasks/main.yml
vim android-19-proxmox/configuration-by-ansible/mynewservice-setup.yml

# 5. Add Makefile target (on host)
vim Makefile
# Add deploy-lxc-mynewservice-capability target

# 6. Test again (should pass now)
make test-unit

# 7. Deploy (ALWAYS use Makefile)
make deploy-lxc-mynewservice-capability
```

**Key principle:** File editing can happen on host, but all execution (Terraform, Ansible, pytest) MUST use Makefile or happen inside `make env-shell`.

## VM Types

### Cloud-init VMs (Automated)
- Clone from template 9000 (Ubuntu 24.04 cloud image)
- Boot ready-to-use in ~30 seconds
- Examples: vm-llm-aimachine (VM 140), vm-coolify (VM 150)

**Catalog configuration:**
```yaml
140:
  name: "vm-llm-aimachine"
  template_vm_id: 9000
  cloud_init: true
  cloud_init_user: "ubuntu"
```

### ISO-based VMs (Manual)
- Boot from ISO media
- Require manual OS installation
- Examples: ubuntu-desktop-dev (VM 103), omarchy (VM 101)

## TDD Workflow

This project follows strict Test-Driven Development:

1. **Small changes** - One focused change at a time
2. **Test first** - Write failing test or use `@pytest.mark.xfail`
3. **Implement** - Minimal code to pass test
4. **Verify** - Run unit AND integration tests
5. **Commit** - Atomic commits with clear messages

See root CLAUDE.md for detailed TDD workflow and examples.

## Common Pitfalls

### Network Configuration
**WARNING:** Network configuration tasks in `host-proxmox` can cause complete connectivity loss if misconfigured. These tasks are DISABLED by default (`when: false`).

Before enabling:
1. Verify interface names: `ip link show`
2. Update role defaults to match reality
3. Have physical console access ready

### Infrastructure Catalog Sync
Always update the catalog when:
- Creating new VMs/containers
- Changing IP addresses
- Modifying resource allocations

The catalog should match Terraform state and actual infrastructure.

### Container Template Names
LXC templates must exist on Proxmox storage. Check available templates:
```bash
pveam available  # List available templates
pveam download local debian-12-standard_12.12-1_amd64.tar.zst
```

## References

- Root `CLAUDE.md` - Repository-wide guidance
- Root `Makefile` - All automation commands
- `docs/SSH_SETUP.md` - SSH authentication setup
- `specs/*/spec.md` - Feature specifications
