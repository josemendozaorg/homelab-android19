# AGENTS.md - Agent Guidelines & Repository Standards

This document defines the standards, workflows, and technical specifications for autonomous agents (and humans) operating in the `homelab-android19` repository.

## 🏗️ Project Architecture & Mental Model

This repository manages a hybrid infrastructure across two physical nodes:
1. **Android #16**: Bastion host (Gateway).
2. **Android #19**: Main Proxmox hypervisor (AMD Ryzen 9950X3D).

### The Two-Step Workflow
Every service deployment follows this strict separation of concerns:
1. **Provisioning (Terraform)**: Handles hardware resources, VM/Container creation, CPU/RAM/Disk allocation.
2. **Configuration (Ansible)**: Handles OS setup, packages, config files, and service lifecycle.

### Source of Truth
- **`infrastructure-catalog.yml`**: The absolute source of truth for all machine IDs, IPs, and resource limits. **Always read this file first** before making any changes.

## 📁 Repository Structure

- `android-16-bastion/`: Configuration for the gateway host.
- `android-19-proxmox/`: Main Proxmox infrastructure.
  - `provisioning-by-terraform/`: Hardware resource allocation.
  - `configuration-by-ansible/`: Service and OS setup.
- `inventory.yml`: Ansible inventory file.
- `Makefile`: Main orchestration entry point.

---

## 🛠️ Build, Lint, and Test Commands

All commands should preferably be run via the `Makefile` to ensure consistency within the Docker development environment.

### Environment Management
- `make env-setup`: Build and start the dev container.
- `make env-shell`: Open an interactive shell inside the container.
- `make env-check`: Validate Ansible syntax and inventory.

### Linting & Formatting
- `make lint`: Runs `black --check` for Python, `ansible-lint` for Ansible, and `terraform fmt -check`.
- `make format`: Runs `black` and `terraform fmt` to fix formatting issues.

### Testing
- `make test-unit`: Runs all unit tests (structural validation).
- `make test-all`: Runs unit tests and connectivity pings.
- `make test-single FILE=path/to/test.py`: Runs a specific test file.
- `pytest path/to/test.py::test_name -v`: Run a specific test case inside `env-shell`.

---

## 💻 Code Style Guidelines

### Python Standards
- **Imports**: Group imports into three blocks separated by a newline:
  1. Standard library imports.
  2. Third-party library imports.
  3. Local project imports.
- **Typing**: All new Python code MUST use type hints for function signatures and class members.
- **Naming**: 
  - Functions/Variables: `snake_case`.
  - Classes: `PascalCase`.
  - Constants: `UPPER_SNAKE_CASE`.
- **Formatting**: Adhere to PEP 8 (enforced by `black`).
- **Error Handling**: Use specific exception types. Avoid silent `except: pass`. Log or re-raise with context.

### Ansible Standards
- **Naming**: 
  - Roles: `{type}-{name}` (e.g., `lxc-adguard`, `vm-coolify`).
  - Tasks: Descriptive sentences starting with a capital letter.
- **Modularity**: Use `include_tasks` to break down large `main.yml` files into feature-specific files.
- **Best Practices**:
  - Always use the `ansible.builtin.` prefix for core modules.
  - Use `become: yes` only when necessary.
  - Prefer the `template` module over `copy` for files containing variables.
- **Error Handling**: Use `failed_when` for custom failure logic and `assert` tasks to verify state before proceeding.

---

## 🧪 Development Workflow (TDD)

We follow a strict 8-step Test-Driven Development process to ensure infrastructure stability:

1. **Task Selection**: Identify the smallest, most isolated unit of work (e.g., adding a single Ansible task).
2. **Design**: Draft the implementation plan. Confirm architectural assumptions and naming with the user.
3. **Red**: Write a failing test in `tests/unit/`. This test should validate the *absence* of the change or the *intended state*.
4. **Green**: Implement the minimum necessary code (Ansible, Terraform, or Python) to make the test pass.
5. **Verify**: Run the specific test using `make test-single FILE=...` or `pytest`. Ensure it transitions from Red to Green.
6. **Integrity**: Run the full unit test suite (`make test-unit`) to guarantee no existing functionality was regressed.
7. **Refactor**: Clean up the implementation. Check for duplication, improve variable names, and ensure adherence to style guidelines.
8. **Commit**: Create an atomic commit following the Conventional Commits specification.

### Example TDD Cycle for Ansible
- **Task**: Add a new configuration file to a role.
- **Red**: Add a `test_config_exists` test in the role's unit test file. Run test -> Fail.
- **Green**: Add the `ansible.builtin.template` task to the role. Run test -> Pass.
- **Commit**: `feat(role-name): add new configuration file`

---

## ⚠️ Security & Safety Rules

- **Network Lockdown**: **NEVER** modify the Proxmox host `/etc/network/interfaces` via automated tasks. This has caused total lockouts in the past. Network configuration is currently disabled for safety.
- **Secrets**: **NEVER** commit secrets (API keys, passwords, private keys) to the repository.
  - Use `terraform.tfvars` (git-ignored) for Terraform.
  - Use `.env` files or Ansible Vault for sensitive configuration.
- **Interactive Commands**: Avoid `git rebase -i` or other interactive prompts that hang in headless environments.

---

## 📝 Commit Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:`: New feature or infrastructure addition.
- `fix:`: Bug fix or configuration correction.
- `test:`: Adding or improving tests.
- `refactor:`: Code change that neither fixes a bug nor adds a feature.
- `chore:`: Maintenance or tooling updates.

---

## 🤖 Agent Context (Rules)

When operating as an agent in this repository, you are expected to be highly autonomous yet safe.

### Operational Principles
- **Analyze First**: Use `grep` and `glob` to understand existing patterns before proposing changes.
- **TDD Mandatory**: Do not implement features without corresponding tests.
- **Context Awareness**: Be aware that you are running in a Linux environment inside a Docker container.
- **Safety First**: Prioritize infrastructure stability over rapid changes. If a change is risky (like network or firewall rules), ask for explicit confirmation.
- **Minimalism**: Only add what is necessary. Favor existing patterns over new abstractions unless the task explicitly requires a refactor.

### Interaction Guidelines
- **Transparency**: Briefly explain the purpose of modifying commands (e.g., `bash` with `edit` or `write`).
- **Confirmation**: Seek confirmation for irreversible actions (e.g., `terraform destroy` or `rm -rf`).
- **Idempotency**: Ensure all Ansible tasks and Terraform resources are idempotent. Running the same command twice should result in "ok" or "no changes" the second time.

## 🚠 Infrastructure & Connectivity

### Ansible Execution Method
Ansible does NOT connect directly to LXC containers. Instead, it uses the Proxmox host as a proxy:
`[Ansible] → SSH → [Proxmox Host] → pct exec → [Container]`

**Benefits:**
- Lightweight containers (no SSH servers needed).
- Single entry point for security.
- Proxmox native management integration.

### VM Management
Virtual Machines (VMs) are configured via direct SSH once they have booted and cloud-init has finished its initial setup.

---
*Last Updated: Jan 2026*
