"""Unit tests for vm-coolify Ansible role structure."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


def test_vm_coolify_role_should_exist(vm_coolify_role_path):
    """vm-coolify role directory should exist following vm-* naming convention."""
    assert vm_coolify_role_path.exists(), \
        "vm-coolify role directory should exist at configuration-by-ansible/vm-coolify"
    assert vm_coolify_role_path.is_dir(), \
        "vm-coolify should be a directory"


def test_vm_coolify_should_have_required_subdirectories(vm_coolify_role_path):
    """vm-coolify role should have required Ansible subdirectories."""
    required_dirs = ['defaults', 'tasks', 'handlers']

    for dir_name in required_dirs:
        dir_path = vm_coolify_role_path / dir_name
        assert dir_path.exists(), \
            f"vm-coolify role should have {dir_name}/ subdirectory"
        assert dir_path.is_dir(), \
            f"{dir_name} should be a directory"


def test_vm_coolify_should_have_defaults_main_yml(vm_coolify_role_path):
    """vm-coolify role should have defaults/main.yml for variables."""
    defaults_main = vm_coolify_role_path / "defaults" / "main.yml"

    assert defaults_main.exists(), \
        "vm-coolify role should have defaults/main.yml"
    assert defaults_main.is_file(), \
        "defaults/main.yml should be a file"


def test_vm_coolify_should_have_tasks_main_yml(vm_coolify_role_path):
    """vm-coolify role should have tasks/main.yml for task orchestration."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    assert tasks_main.exists(), \
        "vm-coolify role should have tasks/main.yml"
    assert tasks_main.is_file(), \
        "tasks/main.yml should be a file"


def test_vm_coolify_should_have_handlers_main_yml(vm_coolify_role_path):
    """vm-coolify role should have handlers/main.yml for service management."""
    handlers_main = vm_coolify_role_path / "handlers" / "main.yml"

    assert handlers_main.exists(), \
        "vm-coolify role should have handlers/main.yml"
    assert handlers_main.is_file(), \
        "handlers/main.yml should be a file"


def test_vm_coolify_defaults_main_yml_should_be_valid_yaml(vm_coolify_role_path):
    """defaults/main.yml should have valid YAML syntax."""
    defaults_main = vm_coolify_role_path / "defaults" / "main.yml"

    with open(defaults_main, 'r') as f:
        content = yaml.safe_load(f)

    # Should be None (empty) or dict (with defaults)
    assert content is None or isinstance(content, dict), \
        "defaults/main.yml should contain valid YAML (empty or dict)"


def test_vm_coolify_tasks_main_yml_should_be_valid_yaml(vm_coolify_role_path):
    """tasks/main.yml should have valid YAML syntax."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = yaml.safe_load(f)

    # Should be None (empty), list (tasks), or dict
    assert content is None or isinstance(content, (list, dict)), \
        "tasks/main.yml should contain valid YAML"


def test_vm_coolify_handlers_main_yml_should_be_valid_yaml(vm_coolify_role_path):
    """handlers/main.yml should have valid YAML syntax."""
    handlers_main = vm_coolify_role_path / "handlers" / "main.yml"

    with open(handlers_main, 'r') as f:
        content = yaml.safe_load(f)

    # Should be None (empty), list (handlers), or dict
    assert content is None or isinstance(content, (list, dict)), \
        "handlers/main.yml should contain valid YAML"


def test_vm_coolify_defaults_should_have_role_description_comment(vm_coolify_role_path):
    """defaults/main.yml should have role description comment following project conventions."""
    defaults_main = vm_coolify_role_path / "defaults" / "main.yml"

    with open(defaults_main, 'r') as f:
        content = f.read()

    # Check for YAML document separator and role description comment
    assert content.startswith('---'), \
        "defaults/main.yml should start with YAML document separator (---)"
    assert 'vm-coolify' in content.lower(), \
        "defaults/main.yml should mention vm-coolify in comments"


def test_vm_coolify_tasks_should_have_role_description_comment(vm_coolify_role_path):
    """tasks/main.yml should have role description comment following project conventions."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = f.read()

    # Check for YAML document separator and role description
    assert content.startswith('---'), \
        "tasks/main.yml should start with YAML document separator (---)"
    assert 'vm-coolify' in content.lower(), \
        "tasks/main.yml should mention vm-coolify in comments"


def test_vm_coolify_handlers_should_have_role_description_comment(vm_coolify_role_path):
    """handlers/main.yml should have role description comment following project conventions."""
    handlers_main = vm_coolify_role_path / "handlers" / "main.yml"

    with open(handlers_main, 'r') as f:
        content = f.read()

    # Check for YAML document separator
    assert content.startswith('---'), \
        "handlers/main.yml should start with YAML document separator (---)"
    assert 'vm-coolify' in content.lower(), \
        "handlers/main.yml should mention vm-coolify in comments"
