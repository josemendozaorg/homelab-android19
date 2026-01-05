# AGENTS.md

This guide is for autonomous coding agents operating in the homelab-android19 repository.

## Command Reference

### Environment & Setup
- `make env-setup`: Build and start the development Docker container.
- `make env-shell`: Open an interactive shell inside the dev container.
- `make setup-ssh`: Configure SSH key authentication (required for Ansible).
- `make env-check`: Validate Ansible syntax for all playbooks.

### Testing
- `make test-unit`: Run all unit tests.
- `make test-all`: Run unit tests and machine connectivity pings.
- **Single Test File**: `pytest android-19-proxmox/tests/unit/test_name.py -v`
- **Specific Test Case**: `pytest android-19-proxmox/tests/unit/test_name.py::test_function_name -v`
- **Catalog Validation**: `make test-catalog`

### Deployment
- `make deploy-vm-{name}-{capability}`: Full orchestration (Terraform + Ansible).
- `make proxmox-deploy`: Run base Ansible playbooks for Proxmox.
- `make adguard-setup`: Configure AdGuard DNS services.

## Code Style & Guidelines

### Ansible Conventions
- **Naming**: Roles must use prefixes: `host-*` (physical), `lxc-*` (containers), `vm-*` (virtual machines).
- **Execution**: Connect to Proxmox host via SSH; use `pct exec {id} -- {cmd}` for containers.
- **Structure**:
  - `defaults/main.yml`: Role variables.
  - `tasks/main.yml`: Orchestration (use `include_tasks`).
  - `tasks/{feature}.yml`: Modular task files.
- **Formatting**: 2-space indentation for all YAML files.
- **Modularity**: Keep tasks idempotent and focused. Avoid giant `main.yml` files.

### Infrastructure Management
- **Source of Truth**: `android-19-proxmox/infrastructure-catalog.yml` contains all IP, ID, and resource definitions.
- **Terraform**: Use for provisioning (cloning templates/creating containers).
- **Ansible**: Use for configuration and software installation.

### Python Style
- **Testing**: Use `pytest`. Follow the existing pattern in `android-19-proxmox/tests/unit/`.
- **Linting**: Use `ruff check .` for Python code.
- **Typing**: Use type hints for new Python utility scripts.

### Error Handling
- **Ansible**: Use `failed_when` with descriptive messages. Use `ansible.builtin.assert` to validate preconditions (e.g., verifying cloud-init completion).
- **Terraform**: Always run `terraform plan` before `apply`.

## Development Workflow (TDD)
Agents MUST follow the 8-step TDD process:
1. **Red**: Write a failing test in `tests/unit/` documenting the desired change.
2. **Green**: Implement the minimum code (Ansible task/Terraform config) to pass the test.
3. **Refactor**: Clean up the implementation while keeping tests passing.
4. **Verify**: Run the full test suite to ensure no regressions.
5. **Commit**: Create atomic commits reflecting the TDD steps.

## Common Task Patterns

### Adding a new DNS Rewrite
1. Update `android-19-proxmox/configuration-by-ansible/lxc-adguard/defaults/main.yml`.
2. Add the domain/IP mapping to `adguard_dns_rewrites`.
3. Run `make adguard-setup`.

### Configuring Host DNS on a new VM
1. Create `tasks/dns-configure.yml` in the role.
2. Use `systemd-resolved` configuration in `/etc/systemd/resolved.conf.d/adguard.conf`.
3. Set `DNS={{ catalog.network.dns }}` and `Domains=homelab ~.`.
4. Include this task early in `tasks/main.yml`.

### Docker DNS for Containers
1. Create `tasks/configure-docker-dns.yml`.
2. Write `/etc/docker/daemon.json` with `{ "dns": ["192.168.0.25", "1.1.1.1"] }`.
3. Restart Docker service.

## Troubleshooting for Agents

### Permission Denied (SSH)
- Symptom: Ansible fails to connect to `android19` or `bastion`.
- Solution: Run `make setup-ssh`. Verify the `homelab-dev` container has access to your host's SSH agent or keys.

### Cloud-init Incomplete
- Symptom: Ansible tasks fail on a newly created VM because APT is locked or user doesn't exist.
- Solution: Ensure `tasks/verify-cloudinit.yml` is included and waits for `cloud-init status --done`.

### Terraform State Mismatch
- Symptom: `terraform apply` wants to recreate existing resources.
- Solution: Run `make proxmox-tf-rebuild-state` to import existing infrastructure.

### YAML Syntax Errors
- Symptom: `make env-check` fails.
- Solution: Check indentation (must be 2 spaces) and ensure Jinja2 brackets are correctly closed.

## Working with Proxmox LXC vs VMs

### LXC Containers (e.g., AdGuard)
- Managed via `proxmox_virtual_environment_container` in Terraform.
- Ansible connects to the **Proxmox Host** and uses `pct exec {id} -- {command}`.
- Do NOT try to SSH directly into containers from Ansible.

### Virtual Machines (e.g., AI Machine, Coolify)
- Managed via `proxmox_virtual_environment_vm` in Terraform.
- Uses **Cloud-init** for initial provisioning.
- Template `9000` (Ubuntu 24.04) is the standard base.
- Ansible connects **directly** to the VM's IP via SSH.
- Always include `tasks/verify-cloudinit.yml` before starting configuration.

## Commit Message Style
Follow the project's existing commit style:
- `feat: ...` for new features or infrastructure additions.
- `fix: ...` for bug fixes or configuration corrections.
- `test: ...` for adding or improving tests.
- `refactor: ...` for code cleanup.
- `chore: ...` for maintenance tasks.
- **Inventory**: `inventory.yml` defines the groups. `android19` is the Proxmox host.
- **Catalog**: `android-19-proxmox/infrastructure-catalog.yml` is the primary source of truth for IDs, IPs, and resource allocations. Always read this file before suggesting or implementing infrastructure changes.
- **Provisioning vs Configuration**:
  - Provisioning (Terraform): Hardware, VM creation, CPU/RAM/Disk, network interface existence.
  - Configuration (Ansible): OS packages, config files, service status, user groups.

## Project Architecture & Context
- **Inventory**: `inventory.yml` defines the groups. `android19` is the Proxmox host.
- **Catalog**: `android-19-proxmox/infrastructure-catalog.yml` is the primary source of truth for IDs, IPs, and resource allocations. Always read this file before suggesting or implementing infrastructure changes.
- **Provisioning vs Configuration**:
  - Provisioning (Terraform): Hardware, VM creation, CPU/RAM/Disk, network interface existence.
  - Configuration (Ansible): OS packages, config files, service status, user groups.

## Security
- **Secrets**: Never hardcode keys or passwords. Use the infrastructure catalog or encrypted variables.
- **Network**: NEVER modify Proxmox host network interfaces (`/etc/network/interfaces`) without extreme caution. It is currently disabled in `host-proxmox/tasks/main.yml`.
- **Privilege Escalation**: Use `become: yes` only when necessary for system-level tasks.
