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
- `make bastion-deploy`: Deploy configuration to Android #16 Bastion.

## Architecture & Source of Truth

### Project Structure
- `android-16-bastion/`: Configuration for the gateway/bastion host.
- `android-19-proxmox/`: Main infrastructure (AMD Ryzen 9950X3D).
  - `provisioning-by-terraform/`: Hardware and resource allocation.
  - `configuration-by-ansible/`: OS, package, and service setup.
- `infrastructure-catalog.yml`: The **primary source of truth** for all machine IDs, IPs, and resource limits. **Always read this file first.**

### Provisioning vs Configuration
1. **Provisioning (Terraform)**: Handles hardware resources, VM/Container creation, CPU/RAM/Disk allocation.
2. **Configuration (Ansible)**: Handles OS setup, packages, config files, and service management.

## Code Style & Guidelines

### Ansible Conventions
- **Naming**: Roles must use prefixes: `host-*` (physical), `lxc-*` (containers), `vm-*` (virtual machines).
- **Execution**:
  - **LXC**: Connect to Proxmox host via SSH; use `pct exec {id} -- {cmd}`.
  - **VM/Bastion**: Connect directly via SSH using the IP from the catalog.
- **Namespacing**: ALWAYS use the `ansible.builtin.` prefix for core modules (e.g., `ansible.builtin.copy`).
- **Structure**: Modularize tasks into `tasks/{feature}.yml` and include them in `main.yml`.
- **Formatting**: 2-space indentation. Keep `main.yml` as a high-level orchestrator.

### Terraform Conventions
- **Location**: `android-19-proxmox/provisioning-by-terraform/`.
- **Variables**: Sensitive or local overrides belong in `terraform.tfvars` (ignored by git).
- **Workflow**: Always run `terraform plan` before `apply`.

### Python Style
- **Testing**: Use `pytest`. Follow patterns in `android-19-proxmox/tests/unit/`.
- **Linting**: Use `ruff check .`.
- **Typing**: Use type hints for all new utility scripts.

## Development Workflow (TDD)
Agents MUST follow the 8-step TDD process:
1. **Red**: Write a failing test in `tests/unit/` documenting the desired change.
2. **Green**: Implement the minimum code to pass the test.
3. **Refactor**: Clean up the implementation.
4. **Verify**: Run the full test suite and `make env-check`.
5. **Commit**: Create atomic commits reflecting the TDD steps.

## Common Task Patterns

### Adding a new Machine/Service
1. Add entry to `android-19-proxmox/infrastructure-catalog.yml`.
2. Define resources in Terraform (`main.tf` or service-specific file).
3. Create an Ansible role in `configuration-by-ansible/`.
4. Add a `deploy-vm-{name}` target to the root `Makefile`.

### DNS Management
- **AdGuard Rewrites**: Update `lxc-adguard/defaults/main.yml` and run `make adguard-setup`.
- **VM DNS**: Use `tasks/dns-configure.yml` with `systemd-resolved` pointing to `catalog.network.dns`.

## Troubleshooting
- **SSH Failure**: Run `make setup-ssh`. Ensure keys are in the `homelab-dev` container.
- **APT Lock**: On new VMs, wait for `cloud-init status --done`. Include `tasks/verify-cloudinit.yml`.
- **State Mismatch**: Use `make proxmox-tf-rebuild-state` to sync Terraform state.

## Security & Safety
- **Secrets**: Use `infrastructure-catalog.yml` or non-committed `.env` files. NEVER hardcode keys.
- **Network**: NEVER modify Proxmox host `/etc/network/interfaces` via Ansible.
- **Privilege**: Use `become: yes` only when necessary.
- **Commit Style**: Use conventional commits (`feat:`, `fix:`, `test:`, `refactor:`, `chore:`).
