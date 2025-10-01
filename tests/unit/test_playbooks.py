"""Tests for Ansible playbook validation."""
import pytest
import subprocess
from pathlib import Path


@pytest.fixture(scope="module")
def playbook_dir(project_root):
    """Return the android-19-proxmox playbook directory."""
    return project_root / "android-19-proxmox"


def test_ubuntu_desktop_playbook_exists(playbook_dir):
    """Ubuntu Desktop playbook file exists."""
    playbook = playbook_dir / "ubuntu-desktop-dev-setup.yml"
    assert playbook.exists(), f"Playbook not found: {playbook}"


def test_ubuntu_desktop_playbook_syntax(playbook_dir):
    """Ubuntu Desktop playbook has valid Ansible syntax."""
    playbook = playbook_dir / "ubuntu-desktop-dev-setup.yml"

    # Run ansible-playbook --syntax-check
    result = subprocess.run(
        ["ansible-playbook", "--syntax-check", str(playbook)],
        capture_output=True,
        text=True,
        cwd=str(playbook_dir.parent)
    )

    assert result.returncode == 0, (
        f"Playbook syntax check failed:\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}"
    )


def test_ubuntu_desktop_playbook_references_catalog(playbook_dir):
    """Ubuntu Desktop playbook references infrastructure catalog."""
    playbook = playbook_dir / "ubuntu-desktop-dev-setup.yml"
    content = playbook.read_text()

    # Check that playbook loads catalog
    assert "infrastructure-catalog.yml" in content, \
        "Playbook should reference infrastructure-catalog.yml"
    assert "catalog.services[103]" in content, \
        "Playbook should reference VM 103 from catalog"


def test_ubuntu_desktop_role_exists(project_root):
    """Ubuntu Desktop role directory exists with required structure."""
    role_dir = project_root / "android-19-proxmox" / "configuration-by-ansible" / "vm-ubuntu-desktop-devmachine"

    assert role_dir.exists(), f"Role directory not found: {role_dir}"

    # Check required directories
    assert (role_dir / "tasks").exists(), "Role missing tasks directory"
    assert (role_dir / "defaults").exists(), "Role missing defaults directory"
    assert (role_dir / "templates").exists(), "Role missing templates directory"

    # Check required task files
    assert (role_dir / "tasks" / "main.yml").exists(), "Role missing tasks/main.yml"
    assert (role_dir / "tasks" / "iso-download.yml").exists(), "Role missing tasks/iso-download.yml"
    assert (role_dir / "tasks" / "post-install-setup.yml").exists(), "Role missing tasks/post-install-setup.yml"


def test_ubuntu_desktop_role_defaults(project_root):
    """Ubuntu Desktop role has defaults file."""
    defaults_file = (
        project_root / "android-19-proxmox" / "configuration-by-ansible" /
        "vm-ubuntu-desktop-devmachine" / "defaults" / "main.yml"
    )

    assert defaults_file.exists(), "Role missing defaults/main.yml"

    # Verify it's valid YAML
    import yaml
    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    assert defaults is not None, "Defaults file is empty"
    assert isinstance(defaults, dict), "Defaults should be a dictionary"
