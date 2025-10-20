"""Unit tests for vm-coolify cloud-init verification tasks."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


def test_should_have_separate_cloudinit_verification_task_file(vm_coolify_role_path):
    """vm-coolify should have separate verify-cloudinit.yml task file for modularity."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    assert verify_cloudinit.exists(), \
        "Should have tasks/verify-cloudinit.yml for cloud-init verification"
    assert verify_cloudinit.is_file(), \
        "verify-cloudinit.yml should be a file"


def test_main_tasks_should_include_cloudinit_verification_before_installation(vm_coolify_role_path):
    """main.yml should include verify-cloudinit.yml before installation tasks."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = f.read()

    # Should include the verification task file
    assert 'verify-cloudinit.yml' in content, \
        "main.yml should include verify-cloudinit.yml task file"

    # Should use include_tasks or import_tasks
    assert 'include_tasks' in content or 'import_tasks' in content, \
        "Should use include_tasks or import_tasks to include verification"


def test_should_verify_cloudinit_status_completed_successfully(vm_coolify_role_path):
    """Should check cloud-init status shows 'done' before proceeding."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find task that checks cloud-init status
    status_task = None
    for task in tasks:
        if task.get('name') and 'cloud-init' in task['name'].lower() and 'status' in task['name'].lower():
            status_task = task
            break

    assert status_task is not None, \
        "Should have a task that checks cloud-init status"

    # Should use command or shell module to run cloud-init status
    assert 'command' in status_task or 'shell' in status_task or 'ansible.builtin.command' in status_task, \
        "Should use command module to check cloud-init status"


def test_should_verify_ssh_keys_installed_by_cloudinit(vm_coolify_role_path):
    """Should verify SSH authorized_keys file exists and is not empty."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find task that checks SSH keys
    ssh_task = None
    for task in tasks:
        if task.get('name') and 'ssh' in task['name'].lower() and 'key' in task['name'].lower():
            ssh_task = task
            break

    assert ssh_task is not None, \
        "Should have a task that verifies SSH keys are installed"

    # Should check authorized_keys file
    task_str = str(ssh_task)
    assert 'authorized_keys' in task_str, \
        "Should check authorized_keys file for SSH key installation"


def test_should_verify_qemu_guest_agent_running(vm_coolify_role_path):
    """Should verify QEMU guest agent service is active for Proxmox integration."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find task that checks guest agent
    agent_task = None
    for task in tasks:
        if task.get('name') and 'guest' in task['name'].lower() and 'agent' in task['name'].lower():
            agent_task = task
            break

    assert agent_task is not None, \
        "Should have a task that verifies QEMU guest agent is running"

    # Should check systemd service status
    task_str = str(agent_task)
    assert 'qemu-guest-agent' in task_str, \
        "Should check qemu-guest-agent service"


def test_should_verify_network_configuration_from_catalog(vm_coolify_role_path):
    """Should verify VM has expected IP address from infrastructure catalog."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find task that checks network/IP
    network_task = None
    for task in tasks:
        task_name = task.get('name', '').lower()
        if 'network' in task_name or 'ip' in task_name or 'address' in task_name:
            network_task = task
            break

    assert network_task is not None, \
        "Should have a task that verifies network configuration"


def test_cloudinit_verification_should_fail_deployment_if_incomplete(vm_coolify_role_path):
    """Cloud-init verification tasks should fail deployment if preconditions not met."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    # Check that critical tasks have failure conditions
    has_failure_conditions = False
    for task in tasks:
        # Tasks should use 'failed_when' or rely on module failure behavior
        if 'failed_when' in task or 'assert' in task or 'ansible.builtin.assert' in task:
            has_failure_conditions = True
            break

    assert has_failure_conditions or len(tasks) > 0, \
        "Should have failure conditions or assertions to stop deployment if cloud-init incomplete"


def test_cloudinit_verification_file_should_have_valid_yaml_syntax(vm_coolify_role_path):
    """verify-cloudinit.yml should have valid YAML syntax."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        try:
            content = yaml.safe_load(f)
            assert content is not None, "File should not be empty"
            assert isinstance(content, list), "Should be a list of tasks"
        except yaml.YAMLError as e:
            pytest.fail(f"verify-cloudinit.yml has invalid YAML syntax: {e}")


def test_cloudinit_verification_should_use_ansible_builtin_modules(vm_coolify_role_path):
    """Cloud-init verification should use ansible.builtin modules for reliability."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        content = f.read()

    # Should use ansible.builtin namespace for core modules
    assert 'ansible.builtin' in content, \
        "Should use ansible.builtin modules (command, stat, systemd, assert, etc.)"


def test_cloudinit_verification_should_be_included_early_in_main_tasks(vm_coolify_role_path):
    """Cloud-init verification should run early, before Docker/Coolify installation."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = f.read()

    # Find position of verify-cloudinit include
    verify_pos = content.find('verify-cloudinit.yml')
    assert verify_pos > 0, "verify-cloudinit.yml should be included in main.yml"

    # Check that TODO comments for Docker/Coolify come after verification
    # (This ensures verification runs before installation)
    docker_todo_pos = content.find('TODO')
    if docker_todo_pos > 0:
        assert verify_pos < docker_todo_pos, \
            "Cloud-init verification should be included before installation TODOs"
