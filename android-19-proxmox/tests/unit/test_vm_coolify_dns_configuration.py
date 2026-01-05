"""Unit tests for vm-coolify DNS configuration tasks."""
import pytest
import yaml
from pathlib import Path

@pytest.fixture
def vm_coolify_role_path(project_root):
    """Path to vm-coolify Ansible role."""
    return project_root / "configuration-by-ansible" / "vm-coolify"

def test_vm_coolify_should_have_dns_configure_yml(vm_coolify_role_path):
    """vm-coolify should have dns-configure.yml for host DNS configuration."""
    dns_configure = vm_coolify_role_path / "tasks" / "dns-configure.yml"
    assert dns_configure.exists(), "Should have tasks/dns-configure.yml"
    assert dns_configure.is_file(), "dns-configure.yml should be a file"

def test_vm_coolify_should_have_configure_docker_dns_yml(vm_coolify_role_path):
    """vm-coolify should have configure-docker-dns.yml for container DNS configuration."""
    docker_dns = vm_coolify_role_path / "tasks" / "configure-docker-dns.yml"
    assert docker_dns.exists(), "Should have tasks/configure-docker-dns.yml"
    assert docker_dns.is_file(), "configure-docker-dns.yml should be a file"

def test_vm_coolify_should_have_dns_verify_yml(vm_coolify_role_path):
    """vm-coolify should have dns-verify.yml for resolution verification."""
    dns_verify = vm_coolify_role_path / "tasks" / "dns-verify.yml"
    assert dns_verify.exists(), "Should have tasks/dns-verify.yml"
    assert dns_verify.is_file(), "dns-verify.yml should be a file"

def test_vm_coolify_main_yml_should_include_dns_tasks(vm_coolify_role_path):
    """main.yml should include DNS configuration tasks in proper order."""
    tasks_main = vm_coolify_role_path / "tasks" / "main.yml"
    content = tasks_main.read_text()

    assert 'dns-configure.yml' in content, "main.yml should include dns-configure.yml"
    assert 'configure-docker-dns.yml' in content, "main.yml should include configure-docker-dns.yml"
    assert 'dns-verify.yml' in content, "main.yml should include dns-verify.yml"

    # Order verification
    cloudinit_pos = content.find('verify-cloudinit.yml')
    dns_configure_pos = content.find('dns-configure.yml')
    docker_install_pos = content.find('install-docker.yml')
    docker_dns_pos = content.find('configure-docker-dns.yml')
    dns_verify_pos = content.find('dns-verify.yml')
    coolify_install_pos = content.find('install-coolify.yml')

    assert cloudinit_pos < dns_configure_pos, "DNS configuration should come after cloud-init verification"
    assert dns_configure_pos < docker_install_pos, "Docker installation should come after host DNS configuration"
    assert docker_install_pos < docker_dns_pos, "Docker DNS configuration should come after Docker installation"
    assert docker_dns_pos < dns_verify_pos, "DNS verification should come after Docker DNS configuration"
    assert dns_verify_pos < coolify_install_pos, "Coolify installation should come after DNS verification"

def test_dns_configure_yml_valid_yaml(vm_coolify_role_path):
    """dns-configure.yml should have valid YAML syntax."""
    dns_configure = vm_coolify_role_path / "tasks" / "dns-configure.yml"
    with open(dns_configure, 'r') as f:
        tasks = yaml.safe_load(f)
    assert isinstance(tasks, list), "dns-configure.yml should contain a task list"

def test_configure_docker_dns_yml_valid_yaml(vm_coolify_role_path):
    """configure-docker-dns.yml should have valid YAML syntax."""
    docker_dns = vm_coolify_role_path / "tasks" / "configure-docker-dns.yml"
    with open(docker_dns, 'r') as f:
        tasks = yaml.safe_load(f)
    assert isinstance(tasks, list), "configure-docker-dns.yml should contain a task list"
