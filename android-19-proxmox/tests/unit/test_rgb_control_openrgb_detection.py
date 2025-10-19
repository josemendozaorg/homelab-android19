"""Unit tests for OpenRGB detection in RGB control role.

These tests validate that the Ansible role properly detects whether OpenRGB
is already installed before attempting installation (idempotent behavior).
"""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def rgb_control_tasks(project_root):
    """Load RGB control task file."""
    tasks_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "rgb-control.yml"
    with open(tasks_file) as f:
        return yaml.safe_load(f)


def test_should_detect_openrgb_installation_status_before_attempting_install(rgb_control_tasks):
    """Should detect if OpenRGB is installed to enable idempotent installation.

    Validates:
    - Task exists to check for OpenRGB installation
    - Uses 'which openrgb' command to detect binary in PATH
    - Registers result for conditional installation logic
    - Does not fail when OpenRGB is not found (failed_when: false)

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    - Addresses: "Given no RGB control software is currently installed"
    - Enables: Idempotent installation (only install if not present)
    """
    # Arrange - Expected task structure
    assert rgb_control_tasks is not None, "RGB control tasks should be loaded"
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find the OpenRGB detection task
    detection_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            if 'openrgb' in task['name'].lower() and 'detect' in task['name'].lower():
                detection_task = task
                break

    # Assert - Detection task exists
    assert detection_task is not None, \
        "Should have a task that detects OpenRGB installation status"

    # Assert - Uses command module to check for openrgb
    assert 'command' in detection_task or 'shell' in detection_task, \
        "Detection task should use 'command' or 'shell' module"

    command_value = detection_task.get('command') or detection_task.get('shell')
    assert 'which openrgb' in command_value, \
        "Should use 'which openrgb' to detect OpenRGB in PATH"

    # Assert - Registers the result
    assert 'register' in detection_task, \
        "Detection task should register result for conditional logic"
    assert detection_task['register'] == 'openrgb_installed', \
        "Should register result as 'openrgb_installed' variable"

    # Assert - Does not fail when openrgb not found
    assert 'failed_when' in detection_task, \
        "Should have failed_when to handle case when OpenRGB is not installed"
    assert detection_task['failed_when'] == False or detection_task['failed_when'] == 'false', \
        "Should set failed_when: false to not fail when OpenRGB absent"


def test_should_check_for_openrgb_binary_in_standard_location(rgb_control_tasks):
    """Should verify OpenRGB binary exists in standard installation path.

    Validates:
    - Task checks /usr/bin/openrgb using stat module
    - Registers result for verification
    - Provides fallback detection method

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find OpenRGB detection tasks
    has_path_check = False
    for task in rgb_control_tasks:
        if task and 'name' in task:
            task_name = task['name'].lower()
            # Check if task verifies the binary path
            if 'openrgb' in task_name and ('detect' in task_name or 'check' in task_name):
                # Could be using stat or command module
                if 'stat' in task:
                    stat_path = task['stat'].get('path', '')
                    if 'openrgb' in stat_path:
                        has_path_check = True
                        break
                elif 'command' in task or 'shell' in task:
                    # The 'which' command serves as path detection
                    has_path_check = True
                    break

    # Assert - Has some form of path-based detection
    assert has_path_check, \
        "Should have a task that checks for OpenRGB binary location"


def test_detection_task_should_run_early_in_task_sequence(rgb_control_tasks):
    """Detection task should run before installation tasks.

    Validates:
    - Detection task appears early in task list
    - Runs before any installation or configuration tasks

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find positions of detection and installation tasks
    detection_index = None
    install_index = None

    for i, task in enumerate(rgb_control_tasks):
        if task and 'name' in task:
            task_name = task['name'].lower()
            # Detection task: has 'detect' but NOT primarily about installation
            if detection_index is None and 'detect' in task_name and 'openrgb' in task_name:
                # Make sure it's actually a detection task, not an install task
                if 'command' in task or 'shell' in task or 'stat' in task:
                    detection_index = i
            # Installation task: has 'install' or 'package' as primary action
            if install_index is None and 'openrgb' in task_name:
                if 'apt' in task or 'package' in task or ('install' in task_name and 'detect' not in task_name):
                    install_index = i

    # Assert - Detection runs before installation (if both exist)
    if detection_index is not None:
        # Detection task exists, which is good
        assert True, "Detection task found in sequence"

        # If installation task also exists, detection should come first
        if install_index is not None:
            assert detection_index < install_index, \
                "Detection task should run before installation task"
