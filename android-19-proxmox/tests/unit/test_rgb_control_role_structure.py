"""Unit tests for RGB control role structure within host-proxmox role.

These tests validate that the Ansible role provides proper structure for
RGB LED light control functionality.
"""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def host_proxmox_role_path(project_root):
    """Return path to host-proxmox role directory."""
    return project_root / "configuration-by-ansible" / "host-proxmox"


def test_should_provide_rgb_control_task_structure_for_host_proxmox_role(host_proxmox_role_path):
    """RGB control task file should exist with valid structure for host-proxmox role.

    Validates:
    - tasks/rgb-control.yml exists
    - File is valid YAML
    - File has basic structure (is a list)

    This supports BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    rgb_control_task_file = host_proxmox_role_path / "tasks" / "rgb-control.yml"

    # Act & Assert - File exists
    assert rgb_control_task_file.exists(), \
        f"RGB control task file should exist at {rgb_control_task_file}"

    # Act & Assert - Valid YAML
    with open(rgb_control_task_file) as f:
        content = yaml.safe_load(f)

    # Assert - Basic structure (should be a list for Ansible tasks)
    assert isinstance(content, list), \
        "RGB control task file should contain a list of tasks"


def test_should_define_rgb_control_default_variables_in_host_proxmox_role(host_proxmox_role_path):
    """RGB control default variables should be defined in host-proxmox role.

    Validates:
    - defaults/main.yml contains rgb_lights_enabled variable
    - defaults/main.yml contains rgb_lights_state variable
    - Variables have appropriate default values

    This supports BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    defaults_file = host_proxmox_role_path / "defaults" / "main.yml"

    # Act
    assert defaults_file.exists(), "defaults/main.yml should exist"

    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    # Assert - Required RGB variables are defined
    assert 'rgb_lights_enabled' in defaults, \
        "rgb_lights_enabled variable should be defined in defaults"

    assert 'rgb_lights_state' in defaults, \
        "rgb_lights_state variable should be defined in defaults"

    # Assert - Variables have sensible types/values
    assert isinstance(defaults['rgb_lights_enabled'], bool), \
        "rgb_lights_enabled should be a boolean"

    assert defaults['rgb_lights_state'] in ['on', 'off'], \
        "rgb_lights_state should be 'on' or 'off'"


def test_should_include_rgb_control_tasks_in_host_proxmox_main_tasks(host_proxmox_role_path):
    """RGB control task file should be included in main task list.

    Validates:
    - tasks/main.yml includes rgb-control.yml
    - Include is enabled (not commented out)

    This supports BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    main_tasks_file = host_proxmox_role_path / "tasks" / "main.yml"

    # Act
    assert main_tasks_file.exists(), "tasks/main.yml should exist"

    with open(main_tasks_file) as f:
        content = f.read()
        tasks = yaml.safe_load(f.read())  # Parse for structure validation

    # Assert - rgb-control.yml is included
    assert 'rgb-control.yml' in content, \
        "tasks/main.yml should include rgb-control.yml task file"

    # Assert - Include is not commented out
    # Check that the line containing rgb-control.yml doesn't start with #
    for line in content.split('\n'):
        if 'rgb-control.yml' in line:
            stripped = line.strip()
            assert not stripped.startswith('#'), \
                "rgb-control.yml include should not be commented out"
            break
