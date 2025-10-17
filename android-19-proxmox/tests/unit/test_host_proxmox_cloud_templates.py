"""Unit tests for host-proxmox cloud image template automation."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def host_proxmox_role_dir(project_root):
    """host-proxmox role directory."""
    return project_root / "configuration-by-ansible" / "host-proxmox"


def test_cloud_image_templates_task_file_exists(host_proxmox_role_dir):
    """host-proxmox role should have cloud-image-templates.yml task file."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    assert task_file.exists(), "tasks/cloud-image-templates.yml not found"


def test_cloud_image_templates_valid_yaml(host_proxmox_role_dir):
    """cloud-image-templates.yml should be valid YAML."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    with open(task_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "cloud-image-templates.yml should not be empty"
    assert isinstance(data, list), "cloud-image-templates.yml should contain a list of tasks"


def test_cloud_image_should_download_directly_on_proxmox(host_proxmox_role_dir):
    """Cloud image should be downloaded directly on Proxmox host (no scp)."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    with open(task_file, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find download task
    download_task = None
    for task in tasks:
        if isinstance(task, dict) and 'name' in task:
            if 'download' in task['name'].lower() and 'cloud' in task['name'].lower():
                download_task = task
                break

    assert download_task is not None, "Should have task to download cloud image"

    # Should use get_url module (downloads directly on target host)
    assert 'ansible.builtin.get_url' in str(download_task), \
        "Should use get_url module to download directly on Proxmox (no scp)"


def test_cloud_image_download_should_be_idempotent(host_proxmox_role_dir):
    """Cloud image download should check if file exists (idempotent)."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    with open(task_file, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find check task before download
    has_check_task = False
    for task in tasks:
        if isinstance(task, dict) and 'name' in task:
            task_name = task['name'].lower()
            if ('check' in task_name or 'stat' in task_name) and 'image' in task_name:
                has_check_task = True
                break

    assert has_check_task, "Should check if cloud image exists before downloading"


def test_template_vm_creation_should_be_idempotent(host_proxmox_role_dir):
    """Template VM creation should check if template already exists."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    with open(task_file, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find check task for template VM
    has_template_check = False
    for task in tasks:
        if isinstance(task, dict) and 'name' in task:
            task_name = task['name'].lower()
            if 'check' in task_name and ('template' in task_name or 'vm' in task_name):
                has_template_check = True
                break

    assert has_template_check, "Should check if template VM already exists"


def test_template_creation_should_use_qm_commands(host_proxmox_role_dir):
    """Template creation should use qm commands for Proxmox VM management."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    with open(task_file, 'r') as f:
        content = f.read()

    # Should have qm create, qm importdisk, qm set, qm template commands
    assert 'qm create' in content, "Should use 'qm create' to create VM"
    assert 'qm importdisk' in content or 'qm set' in content, \
        "Should use 'qm importdisk' or 'qm set' to attach disk"
    assert 'qm template' in content, "Should use 'qm template' to convert VM to template"


def test_template_should_configure_cloud_init_drive(host_proxmox_role_dir):
    """Template should have cloud-init drive configured."""
    task_file = host_proxmox_role_dir / "tasks" / "cloud-image-templates.yml"
    with open(task_file, 'r') as f:
        content = f.read()

    # Should configure cloud-init drive (typically on ide2)
    assert 'cloudinit' in content.lower() or 'cloud-init' in content.lower(), \
        "Should configure cloud-init drive"
    assert 'ide2' in content or 'ide' in content, \
        "Cloud-init drive typically uses IDE interface"
