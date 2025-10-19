"""Unit tests for RGB control persistence via systemd service.

These tests validate that the Ansible role creates a systemd service
to ensure RGB light configuration persists across system reboots.
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


def test_should_create_systemd_service_for_rgb_persistence(rgb_control_tasks):
    """Should create a systemd service to persist RGB configuration across reboots.

    Validates:
    - Task exists to create systemd service file
    - Uses template or copy module
    - Service file placed in /etc/systemd/system/
    - Uses privilege escalation (become: true)

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    - Addresses: "And the RGB light configuration persists across system reboots"
    """
    # Arrange
    assert rgb_control_tasks is not None, "RGB control tasks should be loaded"
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find systemd service creation task
    service_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            task_name = task['name'].lower()
            if ('systemd' in task_name or 'service' in task_name) and \
               ('create' in task_name or 'install' in task_name or 'rgb' in task_name):
                # Check if it's creating a service file
                if 'template' in task or 'copy' in task:
                    service_task = task
                    break

    # Assert - Service creation task exists
    assert service_task is not None, \
        "Should have a task that creates systemd service for RGB control"

    # Assert - Uses template or copy module
    assert 'template' in service_task or 'copy' in service_task, \
        "Should use 'template' or 'copy' module to create service file"

    # Assert - Destination is systemd directory
    if 'template' in service_task:
        dest = service_task['template'].get('dest', '')
    elif 'copy' in service_task:
        dest = service_task['copy'].get('dest', '')
    else:
        dest = ''

    assert '/etc/systemd/system/' in dest or '/lib/systemd/system/' in dest, \
        "Service file should be placed in systemd directory"
    assert 'rgb' in dest.lower() and '.service' in dest, \
        "Service file should have RGB-related name with .service extension"

    # Assert - Uses privilege escalation
    assert 'become' in service_task, \
        "Service file creation should use privilege escalation"
    assert service_task['become'] == True or service_task['become'] == 'yes', \
        "Should set become: true for systemd file creation"


def test_should_enable_systemd_service_for_autostart(rgb_control_tasks):
    """Should enable systemd service to start automatically on boot.

    Validates:
    - Task exists to enable systemd service
    - Uses systemd module
    - Service is enabled (not just started)
    - Uses privilege escalation

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    - Ensures service runs automatically on reboot
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find service enable task
    enable_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            task_name = task['name'].lower()
            if 'systemd' in task:
                systemd_config = task['systemd']
                if isinstance(systemd_config, dict):
                    # Check if it's enabling an RGB service
                    service_name = systemd_config.get('name', '')
                    if 'rgb' in service_name.lower():
                        enable_task = task
                        break

    # Assert - Enable task exists
    assert enable_task is not None, \
        "Should have a task that enables RGB systemd service"

    # Assert - Uses systemd module
    assert 'systemd' in enable_task, \
        "Should use 'systemd' module to manage service"

    # Assert - Service is enabled
    systemd_config = enable_task['systemd']
    assert isinstance(systemd_config, dict), "systemd config should be a dict"
    assert 'enabled' in systemd_config, \
        "Should specify 'enabled' parameter"
    assert systemd_config['enabled'] == True or \
           systemd_config['enabled'] == 'yes' or \
           systemd_config['enabled'] == 'true', \
        "Service should be enabled for autostart"

    # Assert - Service name is specified
    assert 'name' in systemd_config, \
        "Should specify service name"
    service_name = systemd_config['name']
    assert 'rgb' in service_name.lower(), \
        "Service name should be RGB-related"

    # Assert - Uses privilege escalation
    assert 'become' in enable_task, \
        "Service enable should use privilege escalation"
    assert enable_task['become'] == True or enable_task['become'] == 'yes', \
        "Should set become: true for service management"


def test_should_reload_systemd_daemon_after_service_creation(rgb_control_tasks):
    """Should reload systemd daemon after creating service file.

    Validates:
    - Task exists to reload systemd daemon
    - Uses systemd module with daemon_reload
    - Runs after service file creation

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find daemon reload task
    reload_task = None
    reload_index = None
    service_create_index = None

    for i, task in enumerate(rgb_control_tasks):
        if task and 'systemd' in task:
            systemd_config = task['systemd']
            if isinstance(systemd_config, dict):
                # Daemon reload task
                if 'daemon_reload' in systemd_config and \
                   systemd_config['daemon_reload'] in [True, 'yes', 'true']:
                    reload_task = task
                    reload_index = i

        # Service creation task
        if task and 'name' in task:
            if 'template' in task or 'copy' in task:
                if 'systemd' in task['name'].lower() or 'service' in task['name'].lower():
                    service_create_index = i

    # Assert - Reload task exists
    assert reload_task is not None, \
        "Should have a task that reloads systemd daemon"

    # Assert - Uses systemd module with daemon_reload
    assert 'systemd' in reload_task, \
        "Should use 'systemd' module for daemon reload"
    systemd_config = reload_task['systemd']
    assert systemd_config.get('daemon_reload') in [True, 'yes', 'true'], \
        "Should set daemon_reload: yes"

    # Assert - Proper ordering (reload after service creation)
    if service_create_index is not None and reload_index is not None:
        assert service_create_index < reload_index, \
            "Daemon reload should occur after service file creation"


def test_should_control_only_arctic_lights_channels_not_ram(project_root):
    """RGB service template should control only Arctic lights (led1-led3), not RAM (led4).

    Validates:
    - rgb-control.service.j2 template controls led1, led2, led3
    - Template does NOT control led4 (RAM channel)
    - This ensures service isolation between RGB and RAM control

    Supporting BDD Scenario 3: RAM LED State Persists After Reboot
    Linked to Task 3.3: Modify RGB service to only control led1-led3
    Ensures AC8: Turning RAM LEDs off does NOT affect Arctic lights
    Ensures AC9: Turning Arctic lights off does NOT affect RAM LEDs
    """
    # Arrange
    template_file = project_root / "configuration-by-ansible" / "host-proxmox" / "templates" / "rgb-control.service.j2"

    # Act
    assert template_file.exists(), \
        f"RGB control service template should exist at {template_file}"

    with open(template_file) as f:
        content = f.read()

    # Assert - Template controls Arctic light channels (led1, led2, led3)
    assert 'led1' in content, \
        "RGB service should control led1 channel (Arctic lights)"
    assert 'led2' in content, \
        "RGB service should control led2 channel (Arctic lights)"
    assert 'led3' in content, \
        "RGB service should control led3 channel (Arctic lights)"

    # Assert - Template does NOT control RAM channel (led4)
    assert 'led4' not in content, \
        "RGB service should NOT control led4 channel (RAM - managed by ram-led-control.service)"

    # Assert - Template targets exactly 3 channels
    # Check the for loop structure
    assert 'for led in led1 led2 led3' in content or 'led1 led2 led3' in content, \
        "RGB service should iterate over exactly led1, led2, led3 (Arctic channels only)"
