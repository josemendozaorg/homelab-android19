"""Integration tests for RAM LED control Ansible tasks.

These tests validate actual Ansible execution context and playbook loading.
"""
import pytest
import subprocess
import yaml
from pathlib import Path


@pytest.fixture
def host_proxmox_role_path(project_root):
    """Return path to host-proxmox role directory."""
    return project_root / "configuration-by-ansible" / "host-proxmox"


@pytest.mark.integration
def test_ram_led_control_tasks_ansible_syntax_valid(host_proxmox_role_path):
    """RAM LED control tasks should have valid Ansible syntax.

    This is an integration test that validates the task file can be
    loaded by Ansible without syntax errors.

    Linked to BDD Scenario 1: Turn RAM LEDs Off Independently
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act - Try to load the file with PyYAML (Ansible uses this)
    with open(ram_led_control_task_file) as f:
        tasks = yaml.safe_load(f)

    # Assert - File is parseable and has expected structure
    assert tasks is not None, "Task file should be parseable"
    assert isinstance(tasks, list), "Task file should contain a list"
    assert len(tasks) > 0, "Task file should have at least one task"

    # Assert - Each task has required Ansible fields
    for task in tasks:
        if isinstance(task, dict):
            assert 'name' in task or 'debug' in task or 'command' in task, \
                "Each task should have a name or be a module invocation"


@pytest.mark.integration
def test_ram_led_control_tasks_can_be_included_in_playbook(host_proxmox_role_path, tmp_path):
    """RAM LED control tasks should be includable in an Ansible playbook.

    Creates a minimal playbook that includes ram-led-control.yml and validates
    it passes Ansible syntax checking.

    Linked to Task 1.1: Create Ansible tasks for RAM LED control off
    """
    # Check if ansible-playbook is available
    ansible_check = subprocess.run(
        ['which', 'ansible-playbook'],
        capture_output=True
    )
    if ansible_check.returncode != 0:
        pytest.skip("ansible-playbook not available (runs in Docker environment)")

    # Arrange - Create a minimal test playbook
    test_playbook_content = f"""---
- name: Test RAM LED Control Integration
  hosts: localhost
  gather_facts: false
  vars:
    ram_lights_state: "off"
    ram_lights_enabled: true
  tasks:
    - name: Include RAM LED control tasks
      include_tasks: {host_proxmox_role_path}/tasks/ram-led-control.yml
"""

    test_playbook_path = tmp_path / "test_ram_led_playbook.yml"
    with open(test_playbook_path, 'w') as f:
        f.write(test_playbook_content)

    # Act - Run ansible-playbook --syntax-check
    result = subprocess.run(
        ['ansible-playbook', '--syntax-check', str(test_playbook_path)],
        capture_output=True,
        text=True
    )

    # Assert - Syntax check should pass
    assert result.returncode == 0, \
        f"Ansible syntax check should pass. Error: {result.stderr}"


@pytest.mark.integration
def test_ram_led_control_tasks_have_proper_conditionals(host_proxmox_role_path):
    """RAM LED control tasks should have proper when conditionals.

    Validates that tasks properly check ram_lights_state variable.

    Linked to Task 1.1: Create Ansible tasks for RAM LED control off
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Find tasks with command module
    command_tasks = [t for t in tasks if isinstance(t, dict) and 'command' in t]
    assert len(command_tasks) >= 2, \
        "Should have at least 2 command tasks (on and off)"

    # Assert - Tasks have when conditionals
    for task in command_tasks:
        assert 'when' in task, \
            f"Command task '{task.get('name', 'unnamed')}' should have 'when' conditional"

        # When should be a list or string containing ram_lights_state check
        when_clause = task['when']
        when_str = ' '.join(when_clause) if isinstance(when_clause, list) else when_clause

        assert 'ram_lights_state' in when_str, \
            f"Task '{task.get('name', 'unnamed')}' should check ram_lights_state variable"
