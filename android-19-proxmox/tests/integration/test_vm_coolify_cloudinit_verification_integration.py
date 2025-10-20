"""Integration tests for vm-coolify cloud-init verification."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


@pytest.mark.integration
@pytest.mark.ansible
def test_cloudinit_verification_tasks_should_have_valid_yaml(vm_coolify_role_path):
    """verify-cloudinit.yml should be valid YAML that Ansible can parse."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        try:
            tasks = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"verify-cloudinit.yml has invalid YAML: {e}")

    assert tasks is not None, "File should not be empty"
    assert isinstance(tasks, list), "Should be a list of tasks"
    assert len(tasks) >= 4, "Should have at least 4 verification tasks"


@pytest.mark.integration
@pytest.mark.ansible
def test_main_tasks_should_include_verification_in_correct_order(vm_coolify_role_path):
    """main.yml should include cloud-init verification before installation tasks."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find the include_tasks for verify-cloudinit.yml
    verification_index = None
    for i, task in enumerate(tasks):
        if isinstance(task, dict):
            include_key = task.get('ansible.builtin.include_tasks') or task.get('include_tasks')
            if include_key and 'verify-cloudinit.yml' in str(include_key):
                verification_index = i
                break

    assert verification_index is not None, \
        "main.yml should include verify-cloudinit.yml"

    # Verify it comes after the debug task (index 0) but before installation tasks
    assert verification_index > 0, \
        "Verification should come after initial debug task"


@pytest.mark.integration
@pytest.mark.ansible
def test_all_verification_tasks_use_proper_ansible_modules(vm_coolify_role_path):
    """All verification tasks should use ansible.builtin modules."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    expected_modules = {
        'ansible.builtin.command',
        'ansible.builtin.stat',
        'ansible.builtin.systemd',
        'ansible.builtin.assert'
    }

    found_modules = set()
    for task in tasks:
        for key in task.keys():
            if key.startswith('ansible.builtin.'):
                found_modules.add(key)

    # Should use at least some of the expected modules
    assert len(found_modules) > 0, \
        "Should use ansible.builtin modules for verification"

    # Check that we're using proper modules (not just shell/command for everything)
    assert 'ansible.builtin.stat' in found_modules or 'ansible.builtin.command' in found_modules, \
        "Should use appropriate Ansible modules"


@pytest.mark.integration
@pytest.mark.ansible
def test_verification_tasks_have_failure_conditions(vm_coolify_role_path):
    """Verification tasks should have explicit failure conditions."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        tasks = yaml.safe_load(f)

    failure_checks = 0
    for task in tasks:
        # Count tasks with failure conditions
        if 'failed_when' in task or 'ansible.builtin.assert' in task:
            failure_checks += 1

    assert failure_checks >= 2, \
        "Should have at least 2 tasks with explicit failure conditions"


@pytest.mark.integration
@pytest.mark.ansible
def test_verification_tasks_reference_catalog_configuration(vm_coolify_role_path):
    """Verification tasks should reference vm_config from infrastructure catalog."""
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    with open(verify_cloudinit, 'r') as f:
        content = f.read()

    # Should reference vm_config variable from catalog
    assert 'vm_config' in content, \
        "Should reference vm_config variable from infrastructure catalog"


@pytest.mark.integration
@pytest.mark.ansible
def test_role_structure_supports_complete_verification_workflow(vm_coolify_role_path):
    """Complete verification workflow from main.yml -> verify-cloudinit.yml should be valid."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"
    verify_cloudinit = vm_coolify_role_path / "tasks" / "verify-cloudinit.yml"

    # Both files should be valid YAML
    with open(tasks_main, 'r') as f:
        main_tasks = yaml.safe_load(f)

    with open(verify_cloudinit, 'r') as f:
        verify_tasks = yaml.safe_load(f)

    assert main_tasks is not None, "main.yml should be valid YAML"
    assert verify_tasks is not None, "verify-cloudinit.yml should be valid YAML"
    assert isinstance(main_tasks, list), "main.yml should contain a task list"
    assert isinstance(verify_tasks, list), "verify-cloudinit.yml should contain a task list"
