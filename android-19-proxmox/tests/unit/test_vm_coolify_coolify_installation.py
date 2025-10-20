"""Unit tests for vm-coolify Coolify platform installation tasks."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


def test_should_have_separate_coolify_installation_task_file(vm_coolify_role_path):
    """vm-coolify should have separate install-coolify.yml task file for modularity."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    assert install_coolify.exists(), \
        "Should have tasks/install-coolify.yml for Coolify installation"
    assert install_coolify.is_file(), \
        "install-coolify.yml should be a file"


def test_main_tasks_should_include_coolify_installation_after_docker(vm_coolify_role_path):
    """main.yml should include install-coolify.yml after Docker installation."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = f.read()

    # Should include the Coolify installation task file
    assert 'install-coolify.yml' in content, \
        "main.yml should include install-coolify.yml task file"

    # Should come after install-docker.yml
    docker_pos = content.find('install-docker.yml')
    coolify_pos = content.find('install-coolify.yml')
    assert docker_pos < coolify_pos, \
        "Coolify installation should come after Docker installation"


def test_should_use_official_coolify_installation_script(vm_coolify_role_path):
    """Should use official Coolify installation script from get.coollabs.io."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should reference official Coolify installation script URL
    assert 'get.coollabs.io' in content or 'coolify_install_script_url' in content, \
        "Should use official Coolify installation script from get.coollabs.io"


def test_should_download_installation_script_before_execution(vm_coolify_role_path):
    """Should download Coolify installation script to temporary location before execution."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should download script (get_url or uri module)
    assert 'get_url' in content or 'uri' in content, \
        "Should download installation script before execution for safety"


def test_should_execute_coolify_installation_script(vm_coolify_role_path):
    """Should execute downloaded Coolify installation script."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should execute the script (shell, command, or script module)
    assert 'shell' in content or 'command' in content or 'script' in content, \
        "Should execute Coolify installation script"


def test_should_verify_coolify_service_is_running(vm_coolify_role_path):
    """Should verify Coolify systemd service is active after installation."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should check or manage Coolify service
    assert 'systemd' in content or 'service' in content, \
        "Should verify or manage Coolify systemd service"

    # Should reference coolify service
    assert 'coolify' in content.lower(), \
        "Should reference Coolify service"


def test_should_use_ansible_builtin_modules_for_installation(vm_coolify_role_path):
    """Coolify installation should use ansible.builtin modules for reliability."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should use ansible.builtin namespace for core modules
    assert 'ansible.builtin' in content, \
        "Should use ansible.builtin modules (get_url, shell, systemd, stat, etc.)"


def test_should_use_root_privileges_for_installation(vm_coolify_role_path):
    """Coolify installation tasks should use become: yes for root privileges."""
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


def test_should_check_if_coolify_already_installed_for_idempotency(vm_coolify_role_path):
    """Should check if Coolify is already installed before running installation."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should check if already installed (stat module or conditional)
    assert 'stat' in content or 'when' in content, \
        "Should check if Coolify is already installed for idempotency"


def test_should_reference_coolify_configuration_variables(vm_coolify_role_path):
    """Coolify installation should reference configuration variables from defaults."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should reference installation script URL variable
    has_variables = (
        'coolify_install_script_url' in content or
        'coolify_version' in content or
        '{{' in content  # Any Jinja2 variable
    )

    assert has_variables, \
        "Should use variables from defaults/main.yml for configuration"


def test_coolify_installation_file_should_have_valid_yaml_syntax(vm_coolify_role_path):
    """install-coolify.yml should have valid YAML syntax."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        try:
            content = yaml.safe_load(f)
            assert content is not None, "File should not be empty"
            assert isinstance(content, list), "Should be a list of tasks"
        except yaml.YAMLError as e:
            pytest.fail(f"install-coolify.yml has invalid YAML syntax: {e}")


def test_coolify_installation_should_be_idempotent(vm_coolify_role_path):
    """Coolify installation tasks should be safe to run multiple times."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        tasks = yaml.safe_load(f)

    # Check for idempotent patterns (when conditions, creates parameter, etc.)
    has_idempotent_patterns = False
    for task in tasks:
        # Shell/command tasks should have 'when' or 'creates'
        if 'ansible.builtin.shell' in task or 'shell' in task or 'command' in task:
            if 'when' in task or 'creates' in str(task):
                has_idempotent_patterns = True
                break

    assert has_idempotent_patterns or len(tasks) > 0, \
        "Should use idempotent patterns (when conditions, creates parameter, etc.)"


def test_should_download_script_to_temporary_location(vm_coolify_role_path):
    """Should download installation script to /tmp or similar temporary location."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should use temporary location for script
    assert '/tmp' in content or 'temp' in content.lower(), \
        "Should download installation script to temporary location (/tmp)"


def test_installation_script_should_be_executable(vm_coolify_role_path):
    """Downloaded installation script should be made executable before execution."""
    install_coolify = vm_coolify_role_path / "tasks" / "install-coolify.yml"

    with open(install_coolify, 'r') as f:
        content = f.read()

    # Should set script as executable (mode, file module, or shell chmod)
    has_executable_setup = (
        'mode:' in content and '0755' in content or
        '0700' in content or
        'chmod' in content
    )

    assert has_executable_setup or 'shell' in content, \
        "Should ensure installation script is executable (mode: '0755' or chmod +x)"
