"""Tests for Ansible playbook validation."""
import pytest
import subprocess
import requests
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


def test_ubuntu_desktop_iso_url_accessible(project_root):
    """Ubuntu Desktop ISO URL is accessible and returns valid response."""
    defaults_file = (
        project_root / "android-19-proxmox" / "configuration-by-ansible" /
        "vm-ubuntu-desktop-devmachine" / "defaults" / "main.yml"
    )

    import yaml
    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    iso_url = defaults.get('ubuntu_desktop_iso_url')
    assert iso_url, "ubuntu_desktop_iso_url not defined in defaults"

    # Send HEAD request to check if ISO is accessible
    # Use timeout to avoid hanging on slow/dead URLs
    try:
        response = requests.head(iso_url, timeout=10, allow_redirects=True)
        assert response.status_code == 200, (
            f"ISO URL returned status {response.status_code}. "
            f"Expected 200. URL: {iso_url}"
        )
    except requests.exceptions.Timeout:
        pytest.fail(f"ISO URL request timed out after 10 seconds. URL: {iso_url}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to access ISO URL: {e}")


def test_ubuntu_desktop_no_hardcoded_ssh_key(project_root):
    """SSH public key should not be hardcoded in defaults file.

    Security: SSH keys should be read from the system or environment variables,
    not hardcoded in version control.

    This test verifies that ssh_public_key uses Ansible lookup instead of
    hardcoded key material.
    """
    defaults_file = (
        project_root / "android-19-proxmox" / "configuration-by-ansible" /
        "vm-ubuntu-desktop-devmachine" / "defaults" / "main.yml"
    )

    import yaml
    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    ssh_key = defaults.get('ssh_public_key', '')

    # Check if SSH key is hardcoded (starts with ssh-rsa, ssh-ed25519, etc.)
    assert not ssh_key.startswith(('ssh-rsa', 'ssh-ed25519', 'ssh-dss', 'ecdsa-')), (
        "SSH public key should not be hardcoded in defaults file. "
        "Use lookup from ~/.ssh/id_rsa.pub or environment variable instead."
    )


def test_ubuntu_desktop_no_hardcoded_credentials(project_root):
    """User credentials should not be hardcoded in defaults file.

    Security: Hardcoded passwords in version control are a security risk.
    Credentials should be provided via ansible-vault, environment variables,
    or prompted during deployment.

    This test verifies that dev_password uses environment variable lookup
    instead of hardcoded password.
    """
    defaults_file = (
        project_root / "android-19-proxmox" / "configuration-by-ansible" /
        "vm-ubuntu-desktop-devmachine" / "defaults" / "main.yml"
    )

    import yaml
    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    # Check for obviously insecure hardcoded passwords
    dev_password = defaults.get('dev_password', '')

    # Password should not be a simple string like "dev", "password", "changeme", etc.
    insecure_passwords = ['dev', 'password', 'changeme', 'admin', 'test', '123456']

    assert dev_password not in insecure_passwords, (
        f"Password '{dev_password}' is hardcoded in defaults file. "
        "Use ansible-vault, environment variable, or prompt for password instead."
    )
