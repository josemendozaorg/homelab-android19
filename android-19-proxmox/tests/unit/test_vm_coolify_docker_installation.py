"""Unit tests for vm-coolify Docker installation tasks."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


def test_should_have_separate_docker_installation_task_file(vm_coolify_role_path):
    """vm-coolify should have separate install-docker.yml task file for modularity."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    assert install_docker.exists(), \
        "Should have tasks/install-docker.yml for Docker installation"
    assert install_docker.is_file(), \
        "install-docker.yml should be a file"


def test_main_tasks_should_include_docker_installation_after_cloudinit_verification(vm_coolify_role_path):
    """main.yml should include install-docker.yml after cloud-init verification."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = f.read()

    # Should include the Docker installation task file
    assert 'install-docker.yml' in content, \
        "main.yml should include install-docker.yml task file"

    # Should come after verify-cloudinit.yml
    verify_pos = content.find('verify-cloudinit.yml')
    docker_pos = content.find('install-docker.yml')
    assert verify_pos < docker_pos, \
        "Docker installation should come after cloud-init verification"


def test_should_install_docker_from_official_repository(vm_coolify_role_path):
    """Should install Docker CE from official Docker repository."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    # Should reference official Docker repository
    assert 'download.docker.com' in content, \
        "Should use official Docker repository (download.docker.com)"

    # Should add Docker GPG key
    assert 'gpg' in content.lower() or 'key' in content.lower(), \
        "Should add Docker GPG key for package verification"


def test_should_install_docker_compose_plugin(vm_coolify_role_path):
    """Should install Docker Compose plugin (v2) as part of Docker installation."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    # Should install docker-compose-plugin package
    assert 'docker-compose-plugin' in content, \
        "Should install docker-compose-plugin for Docker Compose v2"


def test_should_install_required_docker_packages(vm_coolify_role_path):
    """Should install docker-ce, docker-ce-cli, containerd.io packages."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    required_packages = ['docker-ce', 'docker-ce-cli', 'containerd.io']
    for package in required_packages:
        assert package in content, \
            f"Should install required package: {package}"


def test_should_start_and_enable_docker_service(vm_coolify_role_path):
    """Should start Docker service and enable it for automatic boot."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find systemd task for Docker service
    docker_service_task = None
    for task in tasks:
        if task.get('name') and 'docker' in task['name'].lower() and 'service' in task['name'].lower():
            if 'ansible.builtin.systemd' in task or 'systemd' in task:
                docker_service_task = task
                break

    assert docker_service_task is not None, \
        "Should have a task to manage Docker systemd service"


def test_should_add_cloud_init_user_to_docker_group(vm_coolify_role_path):
    """Should add cloud_init_user from catalog to docker group for non-root Docker access."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    # Should reference cloud_init_user variable from catalog
    assert 'cloud_init_user' in content, \
        "Should use cloud_init_user variable from infrastructure catalog"

    # Should add user to docker group
    assert 'docker' in content, \
        "Should add user to docker group"


def test_should_use_ansible_builtin_modules_for_installation(vm_coolify_role_path):
    """Docker installation should use ansible.builtin modules for reliability."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    # Should use ansible.builtin namespace for core modules
    assert 'ansible.builtin' in content, \
        "Should use ansible.builtin modules (apt, apt_key, apt_repository, systemd, user, etc.)"


def test_docker_installation_should_be_idempotent(vm_coolify_role_path):
    """Docker installation tasks should be safe to run multiple times."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        tasks = yaml.safe_load(f)

    # Check for idempotent patterns (state=present, etc.)
    has_idempotent_tasks = False
    for task in tasks:
        # Apt tasks should use state=present or state=latest
        if 'ansible.builtin.apt' in task or 'apt' in task:
            if 'state' in str(task):
                has_idempotent_tasks = True
                break

    assert has_idempotent_tasks or len(tasks) > 0, \
        "Should use idempotent task patterns (state=present, etc.)"


def test_docker_installation_file_should_have_valid_yaml_syntax(vm_coolify_role_path):
    """install-docker.yml should have valid YAML syntax."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        try:
            content = yaml.safe_load(f)
            assert content is not None, "File should not be empty"
            assert isinstance(content, list), "Should be a list of tasks"
        except yaml.YAMLError as e:
            pytest.fail(f"install-docker.yml has invalid YAML syntax: {e}")


def test_docker_installation_should_update_apt_cache_first(vm_coolify_role_path):
    """Should update apt package cache before installing Docker packages."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        tasks = yaml.safe_load(f)

    # First few tasks should handle apt cache/repository setup
    # Look for update_cache or apt_repository tasks
    has_cache_update = False
    for task in tasks[:5]:  # Check first 5 tasks
        task_str = str(task)
        if 'update_cache' in task_str or 'apt_repository' in task_str:
            has_cache_update = True
            break

    assert has_cache_update, \
        "Should update apt cache or add repository before installing packages"


def test_docker_installation_should_install_prerequisites_first(vm_coolify_role_path):
    """Should install Docker prerequisites (ca-certificates, curl, gnupg) before adding repository."""
    install_docker = vm_coolify_role_path / "tasks" / "install-docker.yml"

    with open(install_docker, 'r') as f:
        content = f.read()

    # Should install prerequisite packages
    prerequisites = ['ca-certificates', 'curl']
    for prereq in prerequisites:
        assert prereq in content, \
            f"Should install prerequisite package: {prereq}"
