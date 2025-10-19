"""Unit tests for RAM LED control role structure within host-proxmox role.

These tests validate that the Ansible role provides proper structure for
independent RAM LED light control functionality.
"""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def host_proxmox_role_path(project_root):
    """Return path to host-proxmox role directory."""
    return project_root / "configuration-by-ansible" / "host-proxmox"


def test_should_provide_ram_led_control_task_structure_for_host_proxmox_role(host_proxmox_role_path):
    """RAM LED control task file should exist with valid structure for host-proxmox role.

    Validates:
    - tasks/ram-led-control.yml exists
    - File is valid YAML
    - File has basic structure (is a list)

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.1: Create Ansible tasks for RAM LED control off
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act & Assert - File exists
    assert ram_led_control_task_file.exists(), \
        f"RAM LED control task file should exist at {ram_led_control_task_file}"

    # Act & Assert - Valid YAML
    with open(ram_led_control_task_file) as f:
        content = yaml.safe_load(f)

    # Assert - Basic structure (should be a list for Ansible tasks)
    assert isinstance(content, list), \
        "RAM LED control task file should contain a list of tasks"


def test_ram_led_control_should_target_only_led4_channel(host_proxmox_role_path):
    """RAM LED control should target only led4 channel, not Arctic lights (led1-led3).

    Validates:
    - Commands target 'led4' only
    - No references to led1, led2, or led3
    - Uses liquidctl --match 'ASUS' pattern

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Ensures AC8: Turning RAM LEDs off does NOT affect Arctic lights
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Contains led4 references (RAM channel)
    assert 'led4' in content, \
        "RAM LED control should target led4 channel"

    # Assert - Does NOT contain Arctic light channel references
    # Check for led1, led2, led3 in command contexts (not in comments)
    task_commands = [task.get('command', '') for task in tasks if isinstance(task, dict)]
    all_commands = ' '.join(task_commands)

    assert 'led1' not in all_commands, \
        "RAM LED control should NOT target led1 (Arctic light channel)"
    assert 'led2' not in all_commands, \
        "RAM LED control should NOT target led2 (Arctic light channel)"
    assert 'led3' not in all_commands, \
        "RAM LED control should NOT target led3 (Arctic light channel)"

    # Assert - Uses liquidctl with ASUS matcher
    assert "liquidctl --match 'ASUS'" in content or 'liquidctl --match "ASUS"' in content, \
        "RAM LED control should use liquidctl with ASUS device matcher"


def test_ram_led_control_should_support_off_state(host_proxmox_role_path):
    """RAM LED control should support turning LEDs off.

    Validates:
    - Has task with 'color off' command
    - Task is conditional on ram_lights_state == "off"
    - Task has changed_when: false for idempotency

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.1: Create Ansible tasks for RAM LED control off
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Has 'color off' command
    assert 'color off' in content, \
        "RAM LED control should have command to turn LEDs off"

    # Assert - Has ram_lights_state conditional
    assert 'ram_lights_state' in content, \
        "RAM LED control should use ram_lights_state variable"

    # Assert - Has changed_when: false for idempotency
    assert 'changed_when: false' in content or 'changed_when:false' in content, \
        "RAM LED control tasks should be marked as unchanged for idempotency"
