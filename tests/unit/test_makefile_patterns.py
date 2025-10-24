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
