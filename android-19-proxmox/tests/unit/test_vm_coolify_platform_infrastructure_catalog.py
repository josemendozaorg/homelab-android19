"""Unit tests for vm-coolify-platform infrastructure catalog entry."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def catalog(project_root):
    """Load infrastructure catalog."""
    catalog_path = project_root / "infrastructure-catalog.yml"
    with open(catalog_path) as f:
        return yaml.safe_load(f)


def test_vm_coolify_platform_exists_in_catalog(catalog):
    """VM ID 160 should exist in infrastructure catalog."""
    assert 160 in catalog['services'], "VM ID 160 (vm-coolify-platform) not found in catalog"


def test_vm_coolify_platform_has_correct_name(catalog):
    """VM should have correct name."""
    vm = catalog['services'][160]
    assert vm['name'] == 'vm-coolify-platform', f"Expected name 'vm-coolify-platform', got '{vm['name']}'"


def test_vm_coolify_platform_is_vm_type(catalog):
    """VM should be type 'vm' not 'container'."""
    vm = catalog['services'][160]
    assert vm['type'] == 'vm', f"Expected type 'vm', got '{vm['type']}'"


def test_vm_coolify_platform_has_correct_ip(catalog):
    """VM should have IP 192.168.0.160."""
    vm = catalog['services'][160]
    assert vm['ip'] == '192.168.0.160', f"Expected IP '192.168.0.160', got '{vm['ip']}'"


def test_vm_coolify_platform_has_correct_resources(catalog):
    """VM should have 8 cores, 16GB RAM, 200GB disk."""
    vm = catalog['services'][160]
    resources = vm['resources']

    assert resources['cores'] == 8, f"Expected 8 cores, got {resources['cores']}"
    assert resources['memory'] == 16384, f"Expected 16384 MB RAM (16GB), got {resources['memory']}"
    assert resources['disk'] == 200, f"Expected 200 GB disk, got {resources['disk']}"


def test_vm_coolify_platform_uses_cloud_init_template(catalog):
    """VM should use cloud image template (VM 9000)."""
    vm = catalog['services'][160]
    assert 'template_vm_id' in vm, "template_vm_id not specified for VM"
    assert vm['template_vm_id'] == 9000, f"Expected template_vm_id 9000, got '{vm['template_vm_id']}'"


def test_vm_coolify_platform_has_cloud_init_enabled(catalog):
    """VM should have cloud-init enabled for automation."""
    vm = catalog['services'][160]
    assert 'cloud_init' in vm, "cloud_init field missing"
    assert vm['cloud_init'] is True, "cloud_init should be enabled for automated setup"


def test_vm_coolify_platform_has_cloud_init_user(catalog):
    """VM should have cloud-init user configured."""
    vm = catalog['services'][160]
    assert 'cloud_init_user' in vm, "cloud_init_user field missing"
    assert vm['cloud_init_user'] == 'ubuntu', f"Expected cloud_init_user 'ubuntu', got '{vm['cloud_init_user']}'"


def test_vm_coolify_platform_has_qemu_agent_enabled(catalog):
    """VM should have QEMU guest agent enabled."""
    vm = catalog['services'][160]
    assert 'agent' in vm, "agent field missing"
    assert vm['agent'] is True, "QEMU guest agent should be enabled"


def test_vm_coolify_platform_has_onboot_enabled(catalog):
    """VM should auto-start on boot (platform service)."""
    vm = catalog['services'][160]
    assert 'onboot' in vm, "onboot field missing"
    assert vm['onboot'] is True, "onboot should be enabled for platform service"


def test_vm_coolify_platform_has_description(catalog):
    """VM should have descriptive description mentioning Coolify/PaaS."""
    vm = catalog['services'][160]
    assert 'description' in vm, "description field missing"
    assert len(vm['description']) > 10, "description should be descriptive"
    assert 'coolify' in vm['description'].lower() or 'paas' in vm['description'].lower(), \
        "description should mention Coolify or PaaS"


def test_vm_coolify_platform_has_storage_specified(catalog):
    """VM should use vm-storage storage pool."""
    vm = catalog['services'][160]
    assert 'storage' in vm, "storage field missing"
    assert vm['storage'] == 'vm-storage', f"Expected storage 'vm-storage', got '{vm['storage']}'"


def test_vm_coolify_platform_id_not_conflicting(catalog):
    """VM ID 160 should be in valid range and not conflict."""
    # Check ID is in VM range (100-199)
    assert 100 <= 160 <= 199, "VM ID should be in range 100-199"

    # Check only one service has ID 160
    services_with_160 = [svc for svc_id, svc in catalog['services'].items() if svc_id == 160]
    assert len(services_with_160) == 1, f"Found {len(services_with_160)} services with ID 160, expected 1"
