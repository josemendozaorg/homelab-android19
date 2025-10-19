"""Unit tests for vm-coolify-platform Terraform configuration."""
import pytest
from pathlib import Path


@pytest.fixture
def terraform_dir(project_root):
    """Terraform provisioning directory."""
    return project_root / "provisioning-by-terraform"


def test_terraform_should_provision_vm_160_from_catalog(terraform_dir, catalog):
    """Terraform should provision VM 160 using for_each pattern from catalog."""
    main_tf = terraform_dir / "main.tf"
    assert main_tf.exists(), "main.tf not found"

    content = main_tf.read_text()

    # Verify Terraform uses for_each pattern for VMs
    assert 'resource "proxmox_virtual_environment_vm" "vms"' in content, \
           "VM resource with for_each pattern not found"
    assert 'for_each = local.terraform_vms' in content, \
           "for_each loop over terraform_vms not found"

    # Verify VM 160 exists in catalog with type="vm" (so it will be provisioned)
    assert 160 in catalog['services'], "VM 160 should be defined in catalog"
    assert catalog['services'][160]['type'] == 'vm', "VM 160 should have type 'vm' for Terraform provisioning"
    assert catalog['services'][160]['name'] == 'vm-coolify-platform', "VM 160 should be vm-coolify-platform"


def test_vm_160_should_have_correct_resources_for_terraform(catalog):
    """VM 160 should have 8 cores, 16GB RAM, and 200GB disk in catalog for Terraform."""
    vm_160 = catalog['services'][160]

    # Verify resource specifications match requirements
    assert vm_160['resources']['cores'] == 8, "VM 160 should have 8 CPU cores"
    assert vm_160['resources']['memory'] == 16384, "VM 160 should have 16384 MB (16GB) RAM"
    assert vm_160['resources']['disk'] == 200, "VM 160 should have 200 GB disk"


def test_vm_160_should_use_cloud_init_template_for_terraform(terraform_dir, catalog):
    """VM 160 should clone from Ubuntu cloud image template (VM 9000) with cloud-init enabled."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Verify Terraform supports cloning from template
    assert 'clone' in content.lower(), "Clone configuration should be present in Terraform"
    assert 'template_vm_id' in content or 'each.value, "template_vm_id"' in content, \
           "Template VM ID should be read from catalog"

    # Verify catalog has cloud-init template configuration for VM 160
    vm_160 = catalog['services'][160]
    assert 'template_vm_id' in vm_160, "VM 160 should specify template_vm_id for cloud-init"
    assert vm_160['template_vm_id'] == 9000, "VM 160 should use template VM ID 9000 (Ubuntu 24.04 cloud image)"
    assert vm_160['cloud_init'] is True, "VM 160 should have cloud-init enabled"


def test_vm_160_should_have_cloud_init_user_configuration(catalog):
    """VM 160 should have cloud-init user account configuration for Terraform."""
    vm_160 = catalog['services'][160]

    assert 'cloud_init_user' in vm_160, "VM 160 should have cloud_init_user defined"
    assert vm_160['cloud_init_user'] == 'ubuntu', "VM 160 should use 'ubuntu' as cloud-init user"


def test_vm_160_should_have_storage_configuration(catalog):
    """VM 160 should use vm-storage for disk storage."""
    vm_160 = catalog['services'][160]

    assert 'storage' in vm_160, "VM 160 should have storage defined"
    assert vm_160['storage'] == 'vm-storage', "VM 160 should use 'vm-storage' storage pool"


def test_vm_160_should_have_qemu_agent_enabled(terraform_dir, catalog):
    """VM 160 should have QEMU guest agent enabled for management."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Verify Terraform supports agent configuration
    assert 'agent' in content.lower(), "QEMU agent configuration should be in Terraform"

    # Verify catalog enables agent for VM 160
    vm_160 = catalog['services'][160]
    assert 'agent' in vm_160, "VM 160 should have agent field"
    assert vm_160['agent'] is True, "VM 160 should have QEMU agent enabled"


def test_vm_160_should_auto_start_on_boot(catalog):
    """VM 160 should be configured to auto-start on boot (platform service)."""
    vm_160 = catalog['services'][160]

    assert 'onboot' in vm_160, "VM 160 should have onboot configuration"
    assert vm_160['onboot'] is True, "VM 160 should auto-start on boot (platform service)"


def test_vm_160_should_have_static_ip_configuration(catalog):
    """VM 160 should have static IP 192.168.0.160 configured."""
    vm_160 = catalog['services'][160]

    assert 'ip' in vm_160, "VM 160 should have IP address defined"
    assert vm_160['ip'] == '192.168.0.160', "VM 160 should have IP 192.168.0.160"


def test_terraform_should_read_vm_resources_from_catalog(terraform_dir):
    """Terraform should use lookup pattern to read VM resources from catalog."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Verify Terraform reads resources dynamically from catalog
    assert 'lookup(each.value.resources, "cores"' in content, \
           "CPU cores should use lookup from catalog"
    assert 'lookup(each.value.resources, "memory"' in content, \
           "Memory should use lookup from catalog"
    assert 'lookup(each.value.resources, "disk"' in content, \
           "Disk should use lookup from catalog"


def test_vm_160_should_be_in_valid_vm_id_range(catalog):
    """VM 160 should be in valid VM ID range (100-199) per network strategy."""
    assert 160 in catalog['services'], "VM 160 should exist in catalog"
    assert 100 <= 160 <= 199, "VM ID 160 should be in VM range (100-199)"
