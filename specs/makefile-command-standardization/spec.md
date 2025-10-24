# Specification: Makefile Command Execution Standardization

**Status:** Approved
**Created:** 2025-10-23
**Approved:** 2025-10-23

## Overview

All commands in the Makefile should follow the established pattern of executing through the Docker development container (homelab-dev). This ensures consistent execution environment, proper SSH key mounting, and reliable dependency management.

### Purpose

Currently, some Makefile targets execute commands directly on the host system (e.g., bash scripts, docker commands) instead of using the containerized execution pattern. This creates inconsistencies and potential environment-related issues. This specification defines the standardization required to ensure all tool executions happen inside the container.

### Stakeholders

- Infrastructure developers using the Makefile for deployments
- CI/CD pipelines that depend on Makefile targets
- DevOps team maintaining the homelab infrastructure

## Functional Requirements

### Core Functionality

- All Ansible commands must use $(ANSIBLE_EXEC) or $(ANSIBLE_INTERACTIVE) variables
- All Terraform commands must use $(DOCKER_COMPOSE) exec with sh -c wrapper pattern
- All bash script executions must run inside the homelab-dev container
- No direct host-level command execution (bash, docker, ansible, terraform, ssh)

### User Interactions

Users interact with the system exclusively through `make` commands. All underlying tool executions are transparent but must happen inside the container for consistency.

### Current Issues

**Identified non-compliant commands:**
1. **Line 66**: `bash scripts/setup-ssh.sh` - Direct bash execution on host
2. **Line 79**: `docker system prune -f` - Direct docker execution on host

## BDD Scenarios

### Scenario 1: SSH Setup Executes in Container

**Given** the development environment is running
**When** a user runs `make setup-ssh`
**Then** the setup-ssh.sh script should execute inside the homelab-dev container
**And** the script should have access to mounted SSH keys at /root/.ssh
**And** the script should succeed with exit code 0

### Scenario 2: Environment Cleanup Without Host Docker Commands

**Given** the development environment is running
**When** a user runs `make env-clean`
**Then** Docker Compose should stop and remove containers
**And** volumes should be removed
**And** no direct `docker` commands should execute on the host system

### Scenario 3: Ansible Commands Use Container Execution

**Given** any Makefile target that runs Ansible
**When** examining the command execution pattern
**Then** the command should use $(ANSIBLE_EXEC) for non-interactive execution
**Or** the command should use $(ANSIBLE_INTERACTIVE) for interactive execution
**And** no direct `ansible` or `ansible-playbook` commands should run on the host

### Scenario 4: Terraform Commands Use Container Execution

**Given** any Makefile target that runs Terraform
**When** examining the command execution pattern
**Then** the command should use $(DOCKER_COMPOSE) exec -T homelab-dev
**And** the command should use sh -c wrapper for directory changes
**And** no direct `terraform` commands should run on the host

### Scenario 5: Script Execution Through Container

**Given** a Makefile target needs to run a bash script
**When** the target executes
**Then** the script should run inside the homelab-dev container
**And** the container should have access to the scripts directory
**And** the script output should be visible to the user

### Scenario 6: Backward Compatibility Maintained

**Given** existing CI/CD pipelines using Makefile targets
**When** commands are updated to container execution pattern
**Then** all targets should produce identical results
**And** all targets should have the same exit codes
**And** no new environment variables or dependencies should be required

### Scenario 7: Pattern Validation Test

**Given** the complete Makefile
**When** running automated pattern validation
**Then** no direct bash/docker/ssh/ansible/terraform commands should be found
**And** all tool executions should use defined variables (ANSIBLE_EXEC, DOCKER_COMPOSE)
**And** validation should pass with 100% compliance

## Acceptance Criteria

### Functional Criteria

- [ ] `make setup-ssh` executes inside homelab-dev container
- [ ] SSH setup script has access to mounted keys at /root/.ssh
- [ ] `make env-clean` stops containers without direct docker commands
- [ ] All Ansible commands use $(ANSIBLE_EXEC) or $(ANSIBLE_INTERACTIVE)
- [ ] All Terraform commands use $(DOCKER_COMPOSE) exec pattern
- [ ] All bash scripts execute inside the container
- [ ] No direct host-level tool execution (bash, docker, ansible, terraform, ssh)

### Quality Criteria

- [ ] Test coverage ≥ 80% for Makefile pattern validation
- [ ] All existing Makefile targets maintain backward compatibility
- [ ] Automated pattern validation test passes with 100% compliance
- [ ] Documentation updated to reflect container execution pattern
- [ ] All BDD scenarios pass

## Non-Functional Requirements

### Performance

No performance degradation expected. Container execution overhead is negligible as the container is already running.

### Security

Enhanced security through:
- Consistent execution environment
- Proper SSH key mounting (read-only)
- No direct host system access from scripts

### Maintainability

Improved maintainability through:
- Consistent command patterns across all targets
- Easier debugging (all execution in controlled environment)
- Automated validation prevents pattern violations

## Constraints and Assumptions

### Technical Constraints

- Must maintain existing variable definitions (DOCKER_COMPOSE, ANSIBLE_EXEC, ANSIBLE_INTERACTIVE)
- Must preserve all existing target functionality
- Must not break existing CI/CD pipelines
- SSH key mounting must remain functional
- Interactive vs non-interactive execution must be preserved where needed

### Assumptions

- Docker Compose environment is always available when running Makefile targets
- The homelab-dev container has all required tools installed
- SSH keys are properly mounted in the container

### Dependencies

- Docker and Docker Compose must be installed on the host
- The homelab-dev container must be running for most targets
- The docker-compose.yml file defines proper volume mounts

## Out of Scope

- Adding new Makefile targets
- Changing Makefile help documentation
- Modifying variable naming conventions
- Refactoring target organization
- Performance optimization of container startup

## Open Questions

None at this time. All requirements are clearly defined.

## Approval

- **Created by:** Claude Code (AI)
- **Date:** 2025-10-23
- **Approved by:** User
- **Approved date:** 2025-10-23
- **Status:** Approved
