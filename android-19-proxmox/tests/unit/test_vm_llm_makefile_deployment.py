"""Unit tests for vm-llm-aimachine Makefile deployment target and playbook."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def makefile(project_root):
    """Makefile path."""
    return project_root.parent / "Makefile"


@pytest.fixture
def playbook_file(project_root):
    """vm-llm-aimachine playbook path."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine-setup.yml"


def test_makefile_has_vm_llm_deployment_target(makefile):
    """Makefile should have deploy-vm-llm-aimachine target."""
    content = makefile.read_text()
    assert 'deploy-vm-llm-aimachine' in content, \
           "Makefile should have deploy-vm-llm-aimachine target"


def test_makefile_target_follows_naming_convention(makefile):
    """Deployment target should follow deploy-vm-{name}-{capability} pattern."""
    content = makefile.read_text()
    # Should match pattern: deploy-vm-llm-aimachine
    assert 'deploy-vm-llm-aimachine:' in content, \
           "Target should follow naming convention"


def test_makefile_target_has_terraform_dependency(makefile):
    """Target should depend on proxmox-tf-init."""
    content = makefile.read_text()
    # Look for line with target and dependency
    assert 'deploy-vm-llm-aimachine: proxmox-tf-init' in content or \
           'deploy-vm-llm-aimachine:' in content and 'proxmox-tf-init' in content, \
           "Target should depend on proxmox-tf-init"


def test_makefile_target_runs_ansible_playbook(makefile):
    """Target should run Ansible playbook."""
    content = makefile.read_text()
    # Check for ansible-playbook command within the target
    lines = content.split('\n')
    in_target = False
    found_ansible = False
    for line in lines:
        if 'deploy-vm-llm-aimachine:' in line:
            in_target = True
        elif in_target and line.strip().startswith(('deploy-', '.PHONY', '#')):
            break
        elif in_target and 'ansible-playbook' in line:
            found_ansible = True
            break

    assert found_ansible, "Target should execute ansible-playbook"


def test_makefile_target_runs_terraform_apply(makefile):
    """Target should run Terraform apply for VM 140."""
    content = makefile.read_text()
    # Check for terraform apply targeting VM 140
    assert 'terraform apply' in content and '140' in content, \
           "Target should run terraform apply for VM 140"


def test_playbook_file_exists(playbook_file):
    """vm-llm-aimachine-setup.yml playbook should exist."""
    assert playbook_file.exists(), "vm-llm-aimachine-setup.yml playbook not found"


def test_playbook_is_valid_yaml(playbook_file):
    """Playbook should be valid YAML."""
    with open(playbook_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "Playbook should not be empty"
    assert isinstance(data, list), "Playbook should be a list of plays"


def test_playbook_targets_proxmox_host(playbook_file):
    """Playbook should target proxmox host."""
    with open(playbook_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data[0]['hosts'] == 'proxmox', \
           "Playbook should target proxmox host"


def test_playbook_loads_catalog(playbook_file):
    """Playbook should load infrastructure catalog."""
    content = playbook_file.read_text()
    assert 'infrastructure-catalog.yml' in content, \
           "Playbook should load infrastructure catalog"
    assert 'catalog' in content and ('from_yaml' in content or 'yamldecode' in content), \
           "Playbook should parse catalog YAML"


def test_playbook_references_vm_140(playbook_file):
    """Playbook should reference VM ID 140 from catalog."""
    content = playbook_file.read_text()
    assert '140' in content, \
           "Playbook should reference VM ID 140"


def test_playbook_includes_vm_llm_role(playbook_file):
    """Playbook should include vm-llm-aimachine role."""
    content = playbook_file.read_text()
    assert 'vm-llm-aimachine' in content, \
           "Playbook should reference vm-llm-aimachine role"


def test_playbook_has_deployment_documentation(playbook_file):
    """Playbook should have helpful deployment documentation."""
    content = playbook_file.read_text()
    # Check for comments or debug messages explaining deployment
    assert 'GPU' in content or 'LLM' in content or 'AI' in content, \
           "Playbook should document GPU/LLM/AI purpose"
