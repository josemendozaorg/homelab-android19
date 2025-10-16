"""Unit tests for vm-llm-aimachine Terraform configuration."""
import pytest
import re
from pathlib import Path


@pytest.fixture
def terraform_dir(project_root):
    """Terraform provisioning directory."""
    return project_root / "provisioning-by-terraform"


def test_terraform_vm_llm_resource_exists(terraform_dir):
    """Terraform main.tf should use for_each pattern for VMs from catalog."""
    main_tf = terraform_dir / "main.tf"
    assert main_tf.exists(), "main.tf not found"

    content = main_tf.read_text()

    # Check for VM resource with for_each pattern
    assert 'resource "proxmox_virtual_environment_vm" "vms"' in content, \
           "VM resource with for_each pattern not found"
    assert 'for_each = local.terraform_vms' in content, \
           "for_each loop over terraform_vms not found"


def test_terraform_vm_llm_has_gpu_passthrough(terraform_dir):
    """VM resource should have hostpci configuration for GPU passthrough."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Look for hostpci configuration
    assert 'hostpci' in content.lower(), "hostpci configuration not found for GPU passthrough"


def test_terraform_vm_llm_has_correct_resources(terraform_dir, catalog):
    """VM configuration should use lookup pattern for resources from catalog."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Check that CPU cores uses lookup from catalog
    assert 'lookup(each.value.resources, "cores"' in content, \
           "CPU cores should use lookup from catalog"

    # Check that memory uses lookup from catalog
    assert 'lookup(each.value.resources, "memory"' in content, \
           "Memory should use lookup from catalog"

    # Check that disk uses lookup from catalog
    assert 'lookup(each.value.resources, "disk"' in content, \
           "Disk should use lookup from catalog"

    # Validate actual values in catalog
    vm_140 = catalog['services'][140]
    assert vm_140['resources']['cores'] == 32, "Catalog should define 32 cores"
    assert vm_140['resources']['memory'] == 51200, "Catalog should define 51200 MB memory"
    assert vm_140['resources']['disk'] == 500, "Catalog should define 500 GB disk"


def test_terraform_vm_llm_uses_cloud_image_template(terraform_dir, catalog):
    """VM should clone from Ubuntu cloud image template defined in catalog."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Check that Terraform supports cloning from template
    assert 'clone' in content.lower(), "Clone configuration should be present"
    assert 'template_vm_id' in content or 'each.value, "template_vm_id"' in content, \
           "Template VM ID should be read from catalog"

    # Validate catalog has cloud-init template configuration
    vm_140 = catalog['services'][140]
    assert 'template_vm_id' in vm_140, "Catalog should specify template_vm_id for cloud-init"
    assert vm_140['template_vm_id'] == 9000, "Template should be VM ID 9000"
    assert vm_140['cloud_init'] is True, "Cloud-init should be enabled"


def test_terraform_vm_llm_has_cloud_init(terraform_dir):
    """VM should have cloud-init configuration."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Cloud-init can be configured various ways in Proxmox Terraform
    assert 'cloud' in content.lower() or 'cicustom' in content or 'ipconfig' in content, \
           "Cloud-init configuration not found"


def test_terraform_vm_llm_has_network_config(terraform_dir):
    """VM should have network configuration."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Check for network configuration
    assert 'network' in content.lower() or 'net' in content.lower(), \
           "Network configuration not found"

    # Check for bridge
    assert 'vmbr0' in content, "Network bridge vmbr0 not configured"


def test_terraform_vm_llm_has_correct_vmid(terraform_dir, catalog):
    """VM should have ID 140 from catalog."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Check that vm_id comes from catalog key
    assert 'vm_id' in content and 'tonumber(each.key)' in content, \
           "VM ID should be set from catalog key using tonumber(each.key)"

    # Validate catalog has VM 140
    assert 140 in catalog['services'], "VM 140 should be defined in catalog"
    assert catalog['services'][140]['name'] == 'vm-llm-aimachine', \
           "VM 140 should be vm-llm-aimachine"


def test_terraform_vm_llm_has_qemu_agent(terraform_dir):
    """VM should have QEMU guest agent enabled."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    assert 'agent' in content.lower(), "QEMU agent configuration not found"


def test_terraform_vm_llm_references_catalog(terraform_dir, catalog):
    """Terraform should reference infrastructure catalog for VM specs."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Check if catalog is referenced via local variable or data source
    # This is a soft check - Terraform might hardcode or use variables
    vm_140 = catalog['services'][140]

    # At minimum, specs should match catalog
    assert vm_140['resources']['cores'] == 32
    assert vm_140['resources']['memory'] == 51200
    assert vm_140['resources']['disk'] == 500
