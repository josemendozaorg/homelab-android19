"""Unit tests for vm-llm-aimachine infrastructure catalog entry."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def catalog(project_root):
    """Load infrastructure catalog."""
    catalog_path = project_root / "infrastructure-catalog.yml"
    with open(catalog_path) as f:
        return yaml.safe_load(f)


def test_vm_llm_aimachine_exists_in_catalog(catalog):
    """VM ID 140 should exist in infrastructure catalog."""
    assert 140 in catalog['services'], "VM ID 140 (vm-llm-aimachine) not found in catalog"


def test_vm_llm_aimachine_has_correct_name(catalog):
    """VM should have correct name."""
    vm = catalog['services'][140]
    assert vm['name'] == 'vm-llm-aimachine', f"Expected name 'vm-llm-aimachine', got '{vm['name']}'"


def test_vm_llm_aimachine_is_vm_type(catalog):
    """VM should be type 'vm' not 'container'."""
    vm = catalog['services'][140]
    assert vm['type'] == 'vm', f"Expected type 'vm', got '{vm['type']}'"


def test_vm_llm_aimachine_has_correct_ip(catalog):
    """VM should have IP 192.168.0.140."""
    vm = catalog['services'][140]
    assert vm['ip'] == '192.168.0.140', f"Expected IP '192.168.0.140', got '{vm['ip']}'"


def test_vm_llm_aimachine_has_correct_resources(catalog):
    """VM should have 32 cores, 50GB RAM, 500GB disk."""
    vm = catalog['services'][140]
    resources = vm['resources']

    assert resources['cores'] == 32, f"Expected 32 cores, got {resources['cores']}"
    assert resources['memory'] == 51200, f"Expected 51200 MB RAM, got {resources['memory']}"
    assert resources['disk'] == 500, f"Expected 500 GB disk, got {resources['disk']}"


def test_vm_llm_aimachine_has_iso_specified(catalog):
    """VM should have Ubuntu Server ISO specified."""
    vm = catalog['services'][140]
    assert 'iso' in vm, "ISO not specified for VM"
    assert 'ubuntu' in vm['iso'].lower(), f"Expected Ubuntu ISO, got '{vm['iso']}'"
    assert 'server' in vm['iso'].lower() or '24.04' in vm['iso'], \
        f"Expected Ubuntu Server ISO, got '{vm['iso']}'"


def test_vm_llm_aimachine_has_gpu_passthrough_config(catalog):
    """VM should have GPU passthrough configuration."""
    vm = catalog['services'][140]
    assert 'gpu_passthrough' in vm, "GPU passthrough configuration not found"
    gpu_config = vm['gpu_passthrough']

    assert 'enabled' in gpu_config, "GPU passthrough 'enabled' field missing"
    assert gpu_config['enabled'] is True, "GPU passthrough should be enabled"
    assert 'device_id' in gpu_config or 'hostpci' in gpu_config, \
        "GPU device ID or hostpci configuration missing"


def test_vm_llm_aimachine_has_cloud_init_enabled(catalog):
    """VM should have cloud-init enabled for automation."""
    vm = catalog['services'][140]
    assert 'cloud_init' in vm, "cloud_init field missing"
    assert vm['cloud_init'] is True, "cloud_init should be enabled for automated setup"


def test_vm_llm_aimachine_has_qemu_agent_enabled(catalog):
    """VM should have QEMU guest agent enabled."""
    vm = catalog['services'][140]
    assert 'agent' in vm, "agent field missing"
    assert vm['agent'] is True, "QEMU guest agent should be enabled"


def test_vm_llm_aimachine_has_description(catalog):
    """VM should have descriptive description."""
    vm = catalog['services'][140]
    assert 'description' in vm, "description field missing"
    assert len(vm['description']) > 10, "description should be descriptive"
    assert 'gpu' in vm['description'].lower() or 'llm' in vm['description'].lower(), \
        "description should mention GPU or LLM"


def test_vm_llm_aimachine_id_not_conflicting(catalog):
    """VM ID 140 should be in valid range and not conflict."""
    # Check ID is in VM range (100-199)
    assert 100 <= 140 <= 199, "VM ID should be in range 100-199"

    # Check only one service has ID 140
    services_with_140 = [svc for svc_id, svc in catalog['services'].items() if svc_id == 140]
    assert len(services_with_140) == 1, f"Found {len(services_with_140)} services with ID 140, expected 1"
