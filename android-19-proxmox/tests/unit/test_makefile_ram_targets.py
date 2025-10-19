"""Unit tests for Makefile RAM LED control targets.

These tests validate that the Makefile provides convenience targets
for RAM LED control operations.
"""
import pytest
import re
from pathlib import Path


@pytest.fixture
def makefile_path(project_root):
    """Return path to project Makefile."""
    return project_root.parent / "Makefile"


def test_makefile_should_have_ram_lights_off_target(makefile_path):
    """Makefile should have proxmox-ram-lights-off target.

    Validates:
    - Target exists in Makefile
    - Target invokes Ansible playbook
    - Target uses ram tag
    - Target sets ram_lights_state=off

    This supports BDD Scenario 6: Using Makefile Convenience Targets
    Linked to Task 6.1: Add Makefile targets for RAM LED control
    """
    # Arrange & Act
    with open(makefile_path) as f:
        content = f.read()

    # Assert - Target exists
    assert 'proxmox-ram-lights-off:' in content, \
        "Makefile should have proxmox-ram-lights-off target"

    # Assert - Target runs Ansible playbook
    # Extract the target's command (the line(s) after the target definition)
    target_match = re.search(
        r'proxmox-ram-lights-off:.*?\n\t(.+?)(?:\n\n|\nproxmox-|\Z)',
        content,
        re.DOTALL
    )
    assert target_match is not None, \
        "proxmox-ram-lights-off target should have a command"

    target_command = target_match.group(1)

    assert 'ansible-playbook' in target_command, \
        "Target should invoke ansible-playbook"

    assert '--tags ram' in target_command, \
        "Target should use --tags ram"

    assert 'ram_lights_state=off' in target_command, \
        "Target should set ram_lights_state=off"


def test_makefile_should_have_ram_lights_on_target(makefile_path):
    """Makefile should have proxmox-ram-lights-on target.

    Validates:
    - Target exists in Makefile
    - Target invokes Ansible playbook
    - Target uses ram tag
    - Target sets ram_lights_state=on

    This supports BDD Scenario 6: Using Makefile Convenience Targets
    Linked to Task 6.1: Add Makefile targets for RAM LED control
    """
    # Arrange & Act
    with open(makefile_path) as f:
        content = f.read()

    # Assert - Target exists
    assert 'proxmox-ram-lights-on:' in content, \
        "Makefile should have proxmox-ram-lights-on target"

    # Assert - Target runs Ansible playbook with correct parameters
    target_match = re.search(
        r'proxmox-ram-lights-on:.*?\n\t(.+?)(?:\n\n|\nproxmox-|\Z)',
        content,
        re.DOTALL
    )
    assert target_match is not None, \
        "proxmox-ram-lights-on target should have a command"

    target_command = target_match.group(1)

    assert 'ansible-playbook' in target_command, \
        "Target should invoke ansible-playbook"

    assert '--tags ram' in target_command, \
        "Target should use --tags ram"

    assert 'ram_lights_state=on' in target_command, \
        "Target should set ram_lights_state=on"


def test_makefile_should_have_ram_lights_status_target(makefile_path):
    """Makefile should have proxmox-ram-lights-status target.

    Validates:
    - Target exists in Makefile
    - Target invokes Ansible playbook
    - Target uses ram tag
    - Target sets ram_lights_action=status

    This supports BDD Scenario 6: Using Makefile Convenience Targets
    Linked to Task 6.1: Add Makefile targets for RAM LED control
    """
    # Arrange & Act
    with open(makefile_path) as f:
        content = f.read()

    # Assert - Target exists
    assert 'proxmox-ram-lights-status:' in content, \
        "Makefile should have proxmox-ram-lights-status target"

    # Assert - Target runs Ansible playbook with correct parameters
    target_match = re.search(
        r'proxmox-ram-lights-status:.*?\n\t(.+?)(?:\n\n|\nproxmox-|\Z)',
        content,
        re.DOTALL
    )
    assert target_match is not None, \
        "proxmox-ram-lights-status target should have a command"

    target_command = target_match.group(1)

    assert 'ansible-playbook' in target_command, \
        "Target should invoke ansible-playbook"

    assert '--tags ram' in target_command, \
        "Target should use --tags ram"

    assert 'ram_lights_action=status' in target_command, \
        "Target should set ram_lights_action=status"
