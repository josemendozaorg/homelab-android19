"""
Unit tests for Makefile command execution pattern validation.

Tests ensure all Makefile targets follow the established pattern of executing
commands through the Docker development container instead of directly on the host.
"""

import os
import re
from pathlib import Path


def test_should_execute_setup_ssh_in_container_when_target_invoked():
    """
    Validates that setup-ssh target executes the script inside the container.

    BEHAVIOR: The setup-ssh target should use $(DOCKER_COMPOSE) exec pattern
    to run the setup-ssh.sh script inside the homelab-dev container, not
    directly on the host system.

    CURRENT STATE: Currently uses direct bash execution (non-compliant)
    EXPECTED: Should use containerized execution pattern
    """
    # Get Makefile path
    project_root = Path(__file__).parent.parent.parent
    makefile_path = project_root / "Makefile"

    assert makefile_path.exists(), f"Makefile not found at {makefile_path}"

    # Read Makefile
    with open(makefile_path, 'r') as f:
        makefile_content = f.read()

    # Find the setup-ssh target
    # Pattern: setup-ssh: (anything) followed by the command
    setup_ssh_pattern = r'setup-ssh:.*?\n\t(.+?)(?:\n[^\t]|\n$)'
    match = re.search(setup_ssh_pattern, makefile_content, re.DOTALL)

    assert match, "setup-ssh target not found in Makefile"

    command = match.group(1).strip()

    # Check that command does NOT use direct bash execution
    # Direct bash execution looks like: @bash scripts/...
    assert not re.match(r'@?bash\s+scripts/', command), \
        f"setup-ssh uses direct bash execution (non-compliant): {command}"

    # Check that command DOES use container execution pattern
    # Container execution should include $(DOCKER_COMPOSE) exec
    assert '$(DOCKER_COMPOSE)' in command, \
        f"setup-ssh should use $(DOCKER_COMPOSE) exec pattern: {command}"

    assert 'exec' in command, \
        f"setup-ssh should use 'exec' to run in container: {command}"

    assert 'homelab-dev' in command, \
        f"setup-ssh should execute in homelab-dev container: {command}"


def test_should_not_use_direct_docker_commands_when_cleaning_environment():
    """
    Validates that env-clean target does not use direct docker commands on host.

    BEHAVIOR: The env-clean target should only use Docker Compose commands
    (via $(DOCKER_COMPOSE) variable) and should NOT execute direct 'docker'
    commands on the host system.

    RATIONALE: Direct 'docker' commands affect ALL Docker resources on the host,
    not just this project. The target should only clean up project-specific
    resources using Docker Compose.

    CURRENT STATE: Uses 'docker system prune -f' (non-compliant)
    EXPECTED: Should only use $(DOCKER_COMPOSE) commands
    """
    # Get Makefile path
    project_root = Path(__file__).parent.parent.parent
    makefile_path = project_root / "Makefile"

    assert makefile_path.exists(), f"Makefile not found at {makefile_path}"

    # Read Makefile
    with open(makefile_path, 'r') as f:
        makefile_content = f.read()

    # Find the env-clean target with all its commands
    # Pattern: env-clean: (anything) followed by all tab-indented commands
    env_clean_pattern = r'env-clean:.*?\n((?:\t.+\n)+)'
    match = re.search(env_clean_pattern, makefile_content, re.MULTILINE)

    assert match, "env-clean target not found in Makefile"

    commands_block = match.group(1)

    # Check that NO direct 'docker' commands are used
    # Direct docker commands look like: docker <subcommand>
    # But $(DOCKER_COMPOSE) is okay
    # Pattern: match 'docker' NOT preceded by $( or other make variable syntax
    direct_docker_pattern = r'(?<!\$\()(?<!\w)docker\s+'

    direct_docker_match = re.search(direct_docker_pattern, commands_block)

    assert not direct_docker_match, \
        f"env-clean uses direct docker command (non-compliant). " \
        f"Found: {direct_docker_match.group(0) if direct_docker_match else 'N/A'}. " \
        f"Commands block: {commands_block.strip()}"


def test_should_use_ansible_variables_when_running_ansible_commands():
    """
    Validates that all Ansible commands use container execution variables.

    BEHAVIOR: Any Makefile target running Ansible should use:
    - $(ANSIBLE_EXEC) for non-interactive execution
    - $(ANSIBLE_INTERACTIVE) for interactive execution

    RATIONALE: Direct 'ansible' or 'ansible-playbook' commands run on the host
    system with host's Python environment, not in the controlled container
    environment with all dependencies.

    EXPECTED: All ansible/ansible-playbook commands should be preceded by
    $(ANSIBLE_EXEC) or $(ANSIBLE_INTERACTIVE) variables
    """
    # Get Makefile path
    project_root = Path(__file__).parent.parent.parent
    makefile_path = project_root / "Makefile"

    assert makefile_path.exists(), f"Makefile not found at {makefile_path}"

    # Read Makefile
    with open(makefile_path, 'r') as f:
        makefile_content = f.read()

    # Extract all command lines (tab-indented lines)
    # Pattern: lines starting with tab
    command_lines = []
    for line in makefile_content.split('\n'):
        if line.startswith('\t'):
            command_lines.append(line.strip())

    # Check for direct ansible/ansible-playbook commands
    # Pattern: 'ansible' or 'ansible-playbook' NOT preceded by $(
    # We need to exclude $(ANSIBLE_EXEC) and $(ANSIBLE_INTERACTIVE)
    violations = []
    for line_num, line in enumerate(command_lines, 1):
        # Skip variable definitions, comments, and echo statements
        if line.startswith('#') or ':=' in line:
            continue

        # Skip echo statements (they may mention 'ansible' in messages)
        if re.match(r'@?echo\s+', line):
            continue

        # Check if line contains 'ansible' or 'ansible-playbook'
        if 'ansible' in line.lower():
            # Ensure it's used with a variable (contains $(ANSIBLE_)
            if '$(ANSIBLE_EXEC)' not in line and '$(ANSIBLE_INTERACTIVE)' not in line:
                # Check if it's an actual ansible command (not just word 'ansible' in a path)
                if re.search(r'\bansible\b|\bansible-playbook\b', line, re.IGNORECASE):
                    violations.append(f"Line {line_num}: {line}")

    assert len(violations) == 0, \
        f"Found {len(violations)} Ansible command(s) not using container variables:\n" + \
        "\n".join(violations) + \
        "\n\nAll Ansible commands must use $(ANSIBLE_EXEC) or $(ANSIBLE_INTERACTIVE)"
