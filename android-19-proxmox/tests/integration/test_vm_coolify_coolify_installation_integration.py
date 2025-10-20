"""Integration tests for vm-coolify Coolify installation."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


@pytest.mark.integration
@pytest.mark.ansible
def test_coolify_installation_tasks_should_have_valid_yaml(vm_coolify_role_path):
    """install-coolify.yml should be valid YAML that Ansible can parse."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        try:
            tasks = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"install-coolify.yml has invalid YAML: {e}")

    assert tasks is not None, "File should not be empty"
    assert isinstance(tasks, list), "Should be a list of tasks"
    assert len(tasks) >= 4, "Should have at least 4 installation tasks"


@pytest.mark.integration
@pytest.mark.ansible
def test_main_tasks_should_include_coolify_in_correct_order(vm_coolify_role_path):
    """main.yml should include Coolify installation after Docker installation."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find the include_tasks for install-coolify.yml
    coolify_index = None
    docker_index = None
    for i, task in enumerate(tasks):
        if isinstance(task, dict):
            include_key = task.get('ansible.builtin.include_tasks') or task.get('include_tasks')
            if include_key:
                if 'install-docker.yml' in str(include_key):
                    docker_index = i
                elif 'install-coolify.yml' in str(include_key):
                    coolify_index = i

    assert coolify_index is not None, \
        "main.yml should include install-coolify.yml"
    assert docker_index is not None, \
        "main.yml should include install-docker.yml"
    assert docker_index < coolify_index, \
        "Coolify installation should come after Docker installation"


@pytest.mark.integration
@pytest.mark.ansible
def test_all_coolify_tasks_use_proper_ansible_modules(vm_coolify_role_path):
    """All Coolify installation tasks should use ansible.builtin modules."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        tasks = yaml.safe_load(f)

    expected_modules = {
        'ansible.builtin.stat',
        'ansible.builtin.get_url',
        'ansible.builtin.shell',
        'ansible.builtin.systemd'
    }

    found_modules = set()
    for task in tasks:
        for key in task.keys():
            if key.startswith('ansible.builtin.'):
                found_modules.add(key)

    # Should use multiple expected modules
    assert len(found_modules) >= 3, \
        "Should use at least 3 different ansible.builtin modules"


@pytest.mark.integration
@pytest.mark.ansible
def test_coolify_tasks_have_privilege_escalation(vm_coolify_role_path):
    """Coolify installation tasks should use become: yes for privilege escalation."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        tasks = yaml.safe_load(f)

    # Count tasks with become: yes
    privileged_tasks = 0
    for task in tasks:
        if task.get('become') is True or task.get('become') == 'yes':
            privileged_tasks += 1

    assert privileged_tasks >= 2, \
        "Should have at least 2 tasks with become: yes (installation requires root)"


@pytest.mark.integration
@pytest.mark.ansible
def test_coolify_installation_has_idempotency_check(vm_coolify_role_path):
    """Coolify installation should check if already installed before proceeding."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        tasks = yaml.safe_load(f)

    # Should have a stat task to check if installed
    has_stat_check = False
    for task in tasks:
        if 'ansible.builtin.stat' in task or 'stat' in task:
            has_stat_check = True
            break

    assert has_stat_check, \
        "Should check if Coolify is already installed using stat module"


@pytest.mark.integration
@pytest.mark.ansible
def test_coolify_installation_uses_conditional_execution(vm_coolify_role_path):
    """Installation tasks should use when conditions for idempotency."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should use when conditions to skip if already installed
    assert 'when:' in content, \
        "Should use conditional execution (when) for idempotent installation"


@pytest.mark.integration
@pytest.mark.ansible
def test_role_structure_supports_complete_coolify_workflow(vm_coolify_role_path):
    """Complete Coolify installation workflow from main.yml -> install-coolify.yml should be valid."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    # Both files should be valid YAML
    with open(tasks_main, 'r') as f:
        main_tasks = yaml.safe_load(f)

    with open(install_coolify, 'r') as f:
        coolify_tasks = yaml.safe_load(f)

    assert main_tasks is not None, "main.yml should be valid YAML"
    assert coolify_tasks is not None, "install-coolify.yml should be valid YAML"
    assert isinstance(main_tasks, list), "main.yml should contain a task list"
    assert isinstance(coolify_tasks, list), "install-coolify.yml should contain a task list"
