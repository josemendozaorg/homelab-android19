"""Tests for infrastructure catalog validation."""
import pytest


def test_catalog_loaded(catalog):
    """Catalog YAML can be parsed and loaded."""
    assert catalog is not None
    assert isinstance(catalog, dict)


def test_catalog_has_services(catalog_services):
    """Catalog contains services section."""
    assert catalog_services is not None
    assert isinstance(catalog_services, dict)


@pytest.mark.parametrize("vm_id", [101, 103])
def test_vm_exists_in_catalog(catalog_services, vm_id):
    """VM exists in catalog services."""
    assert vm_id in catalog_services, f"VM {vm_id} not found in catalog"


@pytest.mark.parametrize("vm_id,expected_name,expected_ip", [
    (101, "omarchy", "192.168.0.101"),
    (103, "ubuntu-desktop-dev", "192.168.0.103"),
])
def test_vm_basic_properties(catalog_services, vm_id, expected_name, expected_ip):
    """VM has correct basic properties."""
    vm = catalog_services[vm_id]
    assert vm['name'] == expected_name, f"VM {vm_id} name mismatch"
    assert vm['ip'] == expected_ip, f"VM {vm_id} IP mismatch"
    assert vm['type'] == 'vm', f"VM {vm_id} type should be 'vm'"


@pytest.mark.parametrize("vm_id", [101, 103])
def test_vm_has_required_fields(catalog_services, vm_id):
    """VM entry has all required fields."""
    vm = catalog_services[vm_id]

    required_fields = [
        'name', 'type', 'ip', 'description',
        'iso', 'resources', 'storage'
    ]

    for field in required_fields:
        assert field in vm, f"VM {vm_id} missing required field: {field}"


@pytest.mark.parametrize("vm_id", [101, 103])
def test_vm_resources_complete(catalog_services, vm_id):
    """VM resources section has all required fields."""
    vm = catalog_services[vm_id]
    resources = vm.get('resources', {})

    assert 'cores' in resources, f"VM {vm_id} missing cores in resources"
    assert 'memory' in resources, f"VM {vm_id} missing memory in resources"
    assert 'disk' in resources, f"VM {vm_id} missing disk in resources"

    # Validate types and reasonable values
    assert isinstance(resources['cores'], int), "cores should be integer"
    assert resources['cores'] > 0, "cores should be positive"
    assert isinstance(resources['memory'], int), "memory should be integer"
    assert resources['memory'] > 0, "memory should be positive"
    assert isinstance(resources['disk'], int), "disk should be integer"
    assert resources['disk'] > 0, "disk should be positive"


def test_vm_103_ubuntu_desktop_specific(catalog_services):
    """VM 103 has correct Ubuntu Desktop configuration."""
    vm = catalog_services[103]

    assert vm['name'] == 'ubuntu-desktop-dev'
    assert vm['ip'] == '192.168.0.103'
    assert vm['description'] == 'Ubuntu Desktop development workstation (Ubuntu 24.04 + Omakub)'
    assert vm['iso'] == 'ubuntu-24.04.1-desktop-amd64.iso'
    assert vm['storage'] == 'vm-storage'

    # Verify resources match defaults
    assert vm['resources']['cores'] == 32
    assert vm['resources']['memory'] == 38912
    assert vm['resources']['disk'] == 150
