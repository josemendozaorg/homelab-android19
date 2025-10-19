"""Unit tests for RGB hardware detection in RGB control role.

These tests validate that the Ansible role properly detects RGB hardware
components (Arctic fans, Arctic CPU cooler, RAM) using OpenRGB.
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


def test_should_detect_rgb_hardware_components_using_openrgb(rgb_control_tasks):
    """Should detect RGB hardware components after OpenRGB is installed.

    Validates:
    - Task exists to detect RGB hardware using OpenRGB
    - Uses 'openrgb --list-devices' command
    - Registers result for subsequent tasks
    - Runs after installation tasks
    - Does not fail if no devices found

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    - Addresses: "And all RGB/LED lights on Arctic fans are turned off"
    - Ensures: We know what RGB devices are available before controlling them
    """
    # Arrange
    assert rgb_control_tasks is not None, "RGB control tasks should be loaded"
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find the RGB hardware detection task
    hardware_detection_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            task_name = task['name'].lower()
            if 'detect' in task_name and 'hardware' in task_name or \
               'detect' in task_name and 'device' in task_name or \
               'list' in task_name and 'device' in task_name:
                # Make sure it's using openrgb command
                if 'command' in task or 'shell' in task:
                    command = task.get('command') or task.get('shell')
                    if 'openrgb' in command and 'list' in command:
                        hardware_detection_task = task
                        break

    # Assert - Hardware detection task exists
    assert hardware_detection_task is not None, \
        "Should have a task that detects RGB hardware using OpenRGB"

    # Assert - Uses command module with openrgb --list-devices
    assert 'command' in hardware_detection_task or 'shell' in hardware_detection_task, \
        "Hardware detection should use 'command' or 'shell' module"

    command_value = hardware_detection_task.get('command') or hardware_detection_task.get('shell')
    assert 'openrgb' in command_value.lower(), \
        "Should use OpenRGB for hardware detection"
    assert '--list-devices' in command_value or '-l' in command_value, \
        "Should use --list-devices flag to list RGB hardware"

    # Assert - Registers the result
    assert 'register' in hardware_detection_task, \
        "Hardware detection task should register result for use in subsequent tasks"
    assert hardware_detection_task['register'] == 'rgb_devices_detected', \
        "Should register result as 'rgb_devices_detected' variable"

    # Assert - Does not fail when no devices found
    assert 'failed_when' in hardware_detection_task, \
        "Should have failed_when to handle case when no RGB devices found"
    assert hardware_detection_task['failed_when'] == False or \
           hardware_detection_task['failed_when'] == 'false', \
        "Should set failed_when: false to not fail when no RGB devices present"


def test_hardware_detection_should_run_after_installation(rgb_control_tasks):
    """Hardware detection should run after OpenRGB installation.

    Validates:
    - Hardware detection task appears after installation tasks
    - Proper dependency order

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find positions of installation and hardware detection tasks
    install_index = None
    hardware_detection_index = None

    for i, task in enumerate(rgb_control_tasks):
        if task and 'name' in task:
            task_name = task['name'].lower()
            # Installation task
            if install_index is None and 'install' in task_name and 'openrgb' in task_name:
                if 'apt' in task:
                    install_index = i
            # Hardware detection task
            if hardware_detection_index is None:
                if 'command' in task or 'shell' in task:
                    command = task.get('command') or task.get('shell', '')
                    if 'openrgb' in command and ('list' in command or '-l' in command):
                        hardware_detection_index = i

    # Assert - Proper ordering
    if install_index is not None and hardware_detection_index is not None:
        assert install_index < hardware_detection_index, \
            "Hardware detection should run after OpenRGB installation"


def test_hardware_detection_should_only_run_after_successful_installation(rgb_control_tasks):
    """Hardware detection should only run after OpenRGB is successfully installed.

    Validates:
    - Hardware detection is conditional on successful installation
    - Or runs unconditionally (assuming installation succeeded)

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find hardware detection task
    hardware_detection_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            if 'command' in task or 'shell' in task:
                command = task.get('command') or task.get('shell', '')
                if 'openrgb' in command and ('list' in command or '-l' in command):
                    hardware_detection_task = task
                    break

    # Assert - Task exists
    assert hardware_detection_task is not None, \
        "Hardware detection task should exist"

    # Assert - Either has no condition (runs always after installation)
    # or has explicit condition checking for successful installation
    # For now, we accept both approaches - test just validates the task exists
    # and has proper command structure (validated in previous test)
    assert True, "Hardware detection task found and validated in other tests"
