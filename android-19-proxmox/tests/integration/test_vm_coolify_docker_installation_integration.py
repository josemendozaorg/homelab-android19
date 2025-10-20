"""Integration tests for vm-coolify Docker installation."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


@pytest.mark.integration
@pytest.mark.ansible
def test_docker_installation_tasks_should_have_valid_yaml(vm_coolify_role_path):
    """install-docker.yml should be valid YAML that Ansible can parse."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        try:
            tasks = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"install-docker.yml has invalid YAML: {e}")

    assert tasks is not None, "File should not be empty"
    assert isinstance(tasks, list), "Should be a list of tasks"
    assert len(tasks) >= 7, "Should have at least 7 installation tasks"


@pytest.mark.integration
@pytest.mark.ansible
def test_main_tasks_should_include_docker_in_correct_order(vm_coolify_role_path):
    """main.yml should include Docker installation after cloud-init verification."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find the include_tasks for install-docker.yml
    docker_index = None
    cloudinit_index = None
    for i, task in enumerate(tasks):
        if isinstance(task, dict):
            include_key = task.get('ansible.builtin.include_tasks') or task.get('include_tasks')
            if include_key:
                if 'verify-cloudinit.yml' in str(include_key):
                    cloudinit_index = i
                elif 'install-docker.yml' in str(include_key):
                    docker_index = i

    assert docker_index is not None, \
        "main.yml should include install-docker.yml"
    assert cloudinit_index is not None, \
        "main.yml should include verify-cloudinit.yml"
    assert cloudinit_index < docker_index, \
        "Docker installation should come after cloud-init verification"


@pytest.mark.integration
@pytest.mark.ansible
def test_all_docker_tasks_use_proper_ansible_modules(vm_coolify_role_path):
    """All Docker installation tasks should use ansible.builtin modules."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        tasks = yaml.safe_load(f)

    expected_modules = {
        'ansible.builtin.apt',
        'ansible.builtin.apt_key',
        'ansible.builtin.apt_repository',
        'ansible.builtin.systemd',
        'ansible.builtin.user',
        'ansible.builtin.file'
    }

    found_modules = set()
    for task in tasks:
        for key in task.keys():
            if key.startswith('ansible.builtin.'):
                found_modules.add(key)

    # Should use multiple expected modules
    assert len(found_modules) >= 4, \
        "Should use at least 4 different ansible.builtin modules"


@pytest.mark.integration
@pytest.mark.ansible
def test_docker_tasks_have_privilege_escalation(vm_coolify_role_path):
    """Docker installation tasks should use become: yes for privilege escalation."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        tasks = yaml.safe_load(f)

    # Count tasks with become: yes
    privileged_tasks = 0
    for task in tasks:
        if task.get('become') is True or task.get('become') == 'yes':
            privileged_tasks += 1

    assert privileged_tasks >= 5, \
        "Should have at least 5 tasks with become: yes (most Docker tasks require root)"


@pytest.mark.integration
@pytest.mark.ansible
def test_docker_installation_references_catalog_variables(vm_coolify_role_path):
    """Docker installation should reference vm_config from infrastructure catalog."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    # Should reference vm_config.cloud_init_user for docker group
    assert 'vm_config' in content or 'cloud_init_user' in content, \
        "Should reference vm_config or cloud_init_user variable from catalog"


@pytest.mark.integration
@pytest.mark.ansible
def test_docker_packages_installation_is_idempotent(vm_coolify_role_path):
    """Docker package installation should use state=present for idempotency."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find apt package installation tasks
    package_tasks = [t for t in tasks if 'ansible.builtin.apt' in t or 'apt' in t]

    assert len(package_tasks) >= 2, \
        "Should have multiple apt package installation tasks"

    # Check that they use state=present or state=latest
    for task in package_tasks:
        apt_config = task.get('ansible.builtin.apt') or task.get('apt')
        if apt_config and isinstance(apt_config, dict):
            assert 'state' in apt_config, \
                "Apt tasks should explicitly set state for idempotency"


@pytest.mark.integration
@pytest.mark.ansible
def test_role_structure_supports_complete_docker_workflow(vm_coolify_role_path):
    """Complete Docker installation workflow from main.yml -> install-docker.yml should be valid."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    # Both files should be valid YAML
    with open(tasks_main, 'r') as f:
        main_tasks = yaml.safe_load(f)

    with open(install_docker, 'r') as f:
        docker_tasks = yaml.safe_load(f)

    assert main_tasks is not None, "main.yml should be valid YAML"
    assert docker_tasks is not None, "install-docker.yml should be valid YAML"
    assert isinstance(main_tasks, list), "main.yml should contain a task list"
    assert isinstance(docker_tasks, list), "install-docker.yml should contain a task list"
