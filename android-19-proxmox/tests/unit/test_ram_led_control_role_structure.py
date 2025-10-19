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


def test_should_define_ram_led_control_default_variables_in_host_proxmox_role(host_proxmox_role_path):
    """RAM LED control default variables should be defined in host-proxmox role.

    Validates:
    - defaults/main.yml contains ram_lights_enabled variable
    - defaults/main.yml contains ram_lights_state variable
    - Variables have appropriate default values

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.2: Add variable handling for ram_lights_state in defaults
    """
    # Arrange
    defaults_file = host_proxmox_role_path / "defaults" / "main.yml"

    # Act
    assert defaults_file.exists(), "defaults/main.yml should exist"

    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    # Assert - Required RAM LED variables are defined
    assert 'ram_lights_enabled' in defaults, \
        "ram_lights_enabled variable should be defined in defaults"

    assert 'ram_lights_state' in defaults, \
        "ram_lights_state variable should be defined in defaults"

    # Assert - Variables have sensible types/values
    assert isinstance(defaults['ram_lights_enabled'], bool), \
        "ram_lights_enabled should be a boolean"

    assert defaults['ram_lights_state'] in ['on', 'off'], \
        "ram_lights_state should be 'on' or 'off'"


def test_should_include_ram_led_control_tasks_in_host_proxmox_main_tasks(host_proxmox_role_path):
    """RAM LED control task file should be included in main task list.

    Validates:
    - tasks/main.yml includes ram-led-control.yml
    - Include is enabled (not commented out)
    - Include has proper conditional (ram_lights_enabled)

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.3: Include RAM LED control tasks in main playbook
    """
    # Arrange
    main_tasks_file = host_proxmox_role_path / "tasks" / "main.yml"

    # Act
    assert main_tasks_file.exists(), "tasks/main.yml should exist"

    with open(main_tasks_file) as f:
        content = f.read()

    # Assert - ram-led-control.yml is included
    assert 'ram-led-control.yml' in content, \
        "tasks/main.yml should include ram-led-control.yml task file"

    # Assert - Include is not commented out
    # Check that the line containing ram-led-control.yml doesn't start with #
    for line in content.split('\n'):
        if 'ram-led-control.yml' in line:
            stripped = line.strip()
            assert not stripped.startswith('#'), \
                "ram-led-control.yml include should not be commented out"
            break

    # Assert - Has proper conditional
    assert 'ram_lights_enabled' in content, \
        "RAM LED control include should check ram_lights_enabled variable"


def test_ram_led_control_should_support_on_state(host_proxmox_role_path):
    """RAM LED control should support turning LEDs on with rainbow effect.

    Validates:
    - Has task with 'color rainbow' command for led4
    - Task is conditional on ram_lights_state == "on"
    - Task has changed_when: false for idempotency

    This supports BDD Scenario 2: Turn RAM LEDs On Independently
    Linked to Task 2.1: Add Ansible task for RAM LED control on (rainbow)
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Has 'color rainbow' command for led4
    assert 'color rainbow' in content, \
        "RAM LED control should have command to turn LEDs on with rainbow effect"

    assert 'led4' in content, \
        "Rainbow command should target led4 channel (RAM)"

    # Assert - Has ram_lights_state == "on" conditional
    # Find the "on" task and verify it has proper conditional
    on_task_found = False
    for task in tasks:
        if isinstance(task, dict) and 'command' in task:
            cmd = task['command']
            if 'rainbow' in cmd and 'led4' in cmd:
                on_task_found = True
                assert 'when' in task, "Rainbow task should have conditional"
                when_clause = task['when']
                when_str = ' '.join(when_clause) if isinstance(when_clause, list) else when_clause
                assert 'ram_lights_state' in when_str and '"on"' in when_str, \
                    "Rainbow task should check ram_lights_state == 'on'"
                break

    assert on_task_found, "Should have task for turning RAM LEDs on with rainbow"
