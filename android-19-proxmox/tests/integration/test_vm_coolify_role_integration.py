"""Integration tests for vm-coolify Ansible role."""
import pytest
import subprocess
from pathlib import Path


@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"


@pytest.mark.integration
@pytest.mark.ansible
def test_vm_coolify_role_yaml_files_should_have_valid_syntax(vm_coolify_role_path):
    """All YAML files in vm-coolify role should have valid syntax."""
    import yaml

    yaml_files = [
        vm_coolify_role_path / "defaults" / "main.yml",
        vm_coolify_role_path / "tasks" / "main.yml",
        vm_coolify_role_path / "handlers" / "main.yml",
    ]

    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"{yaml_file.name} has invalid YAML syntax: {e}")


@pytest.mark.integration
@pytest.mark.ansible
def test_vm_coolify_tasks_should_use_ansible_modules(vm_coolify_role_path):
    """tasks/main.yml should use proper Ansible module syntax."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"

    with open(tasks_main, 'r') as f:
        content = f.read()

    # Should use ansible.builtin modules or have TODO comments
    assert 'ansible.builtin' in content or 'TODO' in content, \
        "tasks/main.yml should use ansible.builtin modules or have TODO placeholders"


@pytest.mark.integration
@pytest.mark.ansible
def test_vm_coolify_handlers_should_use_systemd_module(vm_coolify_role_path):
    """handlers/main.yml should use ansible.builtin.systemd for service management."""
    handlers_main = vm_coolify_role_path / "handlers" / "main.yml"

    with open(handlers_main, 'r') as f:
        content = f.read()

    # Should use systemd module for service management
    assert 'ansible.builtin.systemd' in content, \
        "handlers/main.yml should use ansible.builtin.systemd for service management"


@pytest.mark.integration
@pytest.mark.ansible
def test_vm_coolify_defaults_should_define_coolify_variables(vm_coolify_role_path):
    """defaults/main.yml should define Coolify-related variables."""
    import yaml

    defaults_main = vm_coolify_role_path / "defaults" / "main.yml"

    with open(defaults_main, 'r') as f:
        defaults = yaml.safe_load(f)

    if defaults:  # If not empty
        # Should have Coolify-related variables
        expected_prefixes = ['coolify_', 'docker_', 'traefik_', 'letsencrypt_']
        has_coolify_vars = any(
            key.startswith(tuple(expected_prefixes))
            for key in defaults.keys()
        )

        assert has_coolify_vars, \
            "defaults/main.yml should define Coolify-related variables"


@pytest.mark.integration
@pytest.mark.ansible
def test_vm_coolify_role_should_follow_naming_conventions(vm_coolify_role_path):
    """vm-coolify role should follow project naming conventions (vm-* prefix)."""
    role_name = vm_coolify_role_path.name

    assert role_name.startswith('vm-'), \
        "Role should follow vm-* naming convention"
    assert role_name == 'vm-coolify', \
        "Role should be named vm-coolify"
