"""Integration tests for Terraform VM 160 (vm-coolify-platform) provisioning."""
import pytest
import subprocess
from pathlib import Path


@pytest.fixture
def terraform_dir(project_root):
    """Terraform provisioning directory."""
    return project_root / "provisioning-by-terraform"


@pytest.mark.integration
@pytest.mark.terraform
@pytest.mark.slow
def test_terraform_files_should_exist_for_vm_provisioning(terraform_dir):
    """Terraform configuration files should exist for VM provisioning."""
    assert (terraform_dir / "main.tf").exists(), "main.tf should exist"
    assert (terraform_dir / "variables.tf").exists(), "variables.tf should exist"
    assert (terraform_dir / "providers.tf").exists(), "providers.tf should exist"


@pytest.mark.integration
@pytest.mark.terraform
@pytest.mark.slow
def test_terraform_should_reference_infrastructure_catalog(terraform_dir, project_root):
    """Terraform should load VM configuration from infrastructure catalog."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Verify Terraform reads from infrastructure catalog
    assert "infrastructure-catalog.yml" in content, "Terraform should reference infrastructure-catalog.yml"
    assert "yamldecode" in content, "Terraform should parse YAML catalog"
    assert "local.catalog" in content, "Terraform should use local.catalog variable"

    # Verify catalog file exists
    catalog_path = project_root / "infrastructure-catalog.yml"
    assert catalog_path.exists(), "infrastructure-catalog.yml should exist"


@pytest.mark.integration
@pytest.mark.terraform
@pytest.mark.slow
def test_terraform_configuration_should_be_syntactically_valid(terraform_dir):
    """Terraform configuration should have valid HCL syntax."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Basic HCL syntax checks
    assert content.count("{") == content.count("}"), "Braces should be balanced"
    assert content.count("[") == content.count("]"), "Brackets should be balanced"
    assert 'resource "proxmox_virtual_environment_vm"' in content, "VM resource should be defined"


@pytest.mark.integration
@pytest.mark.terraform
@pytest.mark.slow
@pytest.mark.skip(reason="Requires terraform init with Proxmox credentials")
def test_terraform_validate_should_pass(terraform_dir):
    """Terraform configuration should pass validation (requires init)."""
    # This test requires terraform init with valid credentials
    # Skipped by default, can be run manually when credentials are available
    result = subprocess.run(
        ["terraform", "validate"],
        cwd=terraform_dir,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"terraform validate failed: {result.stderr}"
    assert "Success" in result.stdout or "valid" in result.stdout.lower()


@pytest.mark.integration
@pytest.mark.terraform
@pytest.mark.slow
def test_terraform_should_create_vm_resources_from_catalog(terraform_dir):
    """Terraform should define VM resources that read from catalog."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Verify for_each pattern for VMs
    assert 'for_each = local.terraform_vms' in content, \
           "Terraform should use for_each to iterate over VMs from catalog"

    # Verify VM ID comes from catalog key
    assert 'vm_id' in content and 'tonumber(each.key)' in content, \
           "VM ID should be read from catalog key"

    # Verify resources come from catalog
    assert 'each.value.resources' in content, "Resources should be read from catalog"
    assert 'each.value' in content, "VM properties should be read from each.value"


@pytest.mark.integration
@pytest.mark.terraform
@pytest.mark.slow
def test_terraform_should_support_cloud_init_for_vm_160(terraform_dir, catalog):
    """Terraform should support cloud-init for VM 160 provisioning."""
    main_tf = terraform_dir / "main.tf"
    content = main_tf.read_text()

    # Verify Terraform has cloud-init support
    assert 'initialization' in content.lower() or 'cloud' in content.lower(), \
           "Terraform should have cloud-init configuration"

    # Verify VM 160 is configured for cloud-init in catalog
    vm_160 = catalog['services'][160]
    assert vm_160['cloud_init'] is True, "VM 160 should have cloud-init enabled"
    assert vm_160['template_vm_id'] == 9000, "VM 160 should use cloud image template"
