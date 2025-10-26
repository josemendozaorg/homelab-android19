# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in the android-16-bastion directory.

## ⚠️ CRITICAL: Docker Execution Environment

**ALL deployment commands MUST run through the Makefile with Docker.**

The development container provides:
- All dependencies (Ansible, Python)
- Mounted SSH keys for authentication
- Consistent execution environment

**Correct workflow:**
```bash
# From repository root - ALWAYS use Makefile
make bastion-deploy
make test-ping-bastion

# OR use interactive shell
make env-shell
# Now inside container:
ansible-playbook -i inventory.yml android-16-bastion/playbook.yml
```

**NEVER run ansible-playbook directly on host machine:**
```bash
# ❌ WRONG - Missing dependencies, SSH keys may not be configured
ansible-playbook playbook.yml
```

## Directory Overview

This directory manages the Android #16 bastion host (192.168.0.10) - a simple gateway/jump host providing secure entry to the homelab network.

**Purpose:**
- Secure SSH gateway for remote access
- CloudFlare integration for external connectivity
- Network entry point with security best practices

## Directory Structure

```
android-16-bastion/
├── tasks/
│   └── dns-configure.yml    # DNS configuration tasks
├── playbook.yml             # Main configuration playbook
└── setup.yml                # Initial setup playbook
```

This is a simple structure - just Ansible playbooks and tasks, no Terraform provisioning.

## Configuration Approach

The bastion host uses a straightforward Ansible-only approach:
1. **No infrastructure provisioning** - Physical machine, already exists
2. **Simple playbooks** - Just configuration tasks
3. **Minimal dependencies** - References infrastructure catalog for DNS server IP

## Infrastructure Catalog Integration

Even though this is a simple machine, it references the infrastructure catalog for DNS configuration:

```yaml
# playbook.yml
vars_files:
  - "../android-19-proxmox/infrastructure-catalog.yml"
```

**Why?**
- Gets AdGuard DNS server IP (192.168.0.25 from service ID 125)
- Maintains consistency with Proxmox infrastructure
- Single source of truth for all IP addresses

## DNS Configuration

The bastion host can be configured to use AdGuard Home DNS for network-wide DNS features like `.homelab` domain resolution.

### DNS Configuration Task
**File:** `tasks/dns-configure.yml`

This task:
- Reads AdGuard DNS IP from infrastructure catalog
- Configures NetworkManager to use AdGuard as DNS server
- Sets DNS priority to ensure configuration persists

### Running DNS Configuration
```bash
# From repository root
make bastion-deploy

# Or directly with Ansible
ansible-playbook -i ../inventory.yml playbook.yml --tags dns
```

## Common Operations

### Deploy Full Configuration
```bash
# From repository root - ALWAYS use Makefile
make bastion-deploy
```

This runs the main playbook which:
1. Tests connectivity
2. Sets hostname to `android16-bastion`
3. Configures DNS to use AdGuard Home

### Deploy Only DNS Configuration

**Option 1: Using Makefile with tags (preferred)**
```bash
# From repository root
make bastion-deploy ANSIBLE_TAGS="dns"

# Or modify Makefile to add specific target:
# bastion-deploy-dns: ## Deploy only DNS configuration
# 	$(DOCKER_RUN) ansible-playbook --inventory inventory.yml \
# 		android-16-bastion/playbook.yml --tags dns
```

**Option 2: Interactive shell**
```bash
make env-shell
# Inside container:
ansible-playbook -i inventory.yml android-16-bastion/playbook.yml --tags dns
exit
```

### Test Connectivity
```bash
# From repository root - use Makefile
make test-ping-bastion
```

## Playbook Structure

### playbook.yml (Main Configuration)
```yaml
- name: Configure Android #16 Bastion Host
  hosts: bastion

  vars_files:
    - "../android-19-proxmox/infrastructure-catalog.yml"

  tasks:
    - name: Test connection
      ping:

    - name: Set hostname
      hostname:
        name: android16-bastion
      become: yes

    - name: Include DNS configuration tasks
      ansible.builtin.include_tasks:
        file: tasks/dns-configure.yml
      tags:
        - dns
```

**Key features:**
- Runs on `bastion` host group (defined in root `inventory.yml`)
- Loads infrastructure catalog for DNS IP
- Uses tags for selective execution

## Development Workflow

### Adding New Configuration Tasks

1. **Create task file** (on host is fine)
```bash
# Add new task file
touch android-16-bastion/tasks/my-new-config.yml
```

2. **Include in playbook** (edit on host)
```yaml
# playbook.yml
- name: Include my new configuration
  ansible.builtin.include_tasks:
    file: tasks/my-new-config.yml
  tags:
    - myconfig
```

3. **Test** (MUST use Makefile or Docker container)
```bash
# Option 1: Add Makefile target (preferred)
# In root Makefile:
# bastion-deploy-myconfig: ## Deploy my new configuration
# 	$(DOCKER_RUN) ansible-playbook --inventory inventory.yml \
# 		android-16-bastion/playbook.yml --tags myconfig

make bastion-deploy-myconfig

# Option 2: Use interactive shell
make env-shell
# Inside container:
ansible-playbook -i inventory.yml android-16-bastion/playbook.yml --tags myconfig
exit
```

**Key principle:** File editing happens on host, but execution MUST use Makefile or `make env-shell`.

### Testing Configuration Changes

Before deploying to the actual bastion:
1. Review changes in version control
2. Test syntax inside development container: `make env-shell`
3. Have physical access ready (in case SSH breaks)
4. Deploy during maintenance window using: `make bastion-deploy`

## Network Configuration Warning

**CAUTION:** The bastion host is the gateway to your homelab. Breaking SSH access here means losing remote access entirely.

**Best practices:**
- Always have physical access available
- Test network changes in non-production first
- Avoid modifying network interfaces during critical times
- Keep backup SSH keys and known working configurations

## SSH Authentication

The bastion requires SSH key authentication configured. If you encounter "Permission denied" errors:

```bash
# From repository root - use Makefile
make setup-ssh

# This runs the SSH setup script in Docker container
# Manual setup (if needed):
# ssh-copy-id dev@192.168.0.10
```

The Docker container has your `~/.ssh` directory mounted, so SSH keys are available for Ansible connections.

See root `docs/SSH_SETUP.md` for comprehensive SSH setup guide.

## References

- Root `CLAUDE.md` - Repository-wide guidance
- Root `inventory.yml` - Bastion host definition
- Root `Makefile` - Automation commands (`make bastion-deploy`)
- `android-19-proxmox/infrastructure-catalog.yml` - DNS server IP (service 125)
- `docs/SSH_SETUP.md` - SSH authentication setup

## Future Enhancements

Potential additions for the bastion host:
- Fail2ban for brute force protection
- UFW firewall configuration
- CloudFlare tunnel setup automation
- SSH hardening tasks
- Intrusion detection monitoring

When adding features:
1. Create task files in `tasks/`
2. Include in `playbook.yml` with tags
3. Document in this CLAUDE.md
4. Test thoroughly (SSH breakage = no remote access!)
