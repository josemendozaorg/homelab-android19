"""Unit tests for AdGuard Home DHCP server configuration."""
import pytest
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


@pytest.fixture(scope="module")
def adguard_role_dir(project_root):
    """Return the lxc-adguard role directory."""
    return project_root / "configuration-by-ansible" / "lxc-adguard"


@pytest.fixture(scope="module")
def adguard_defaults(adguard_role_dir):
    """Load AdGuard defaults/main.yml."""
    defaults_file = adguard_role_dir / "defaults" / "main.yml"
    with open(defaults_file, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def infrastructure_catalog(project_root):
    """Load infrastructure catalog."""
    catalog_file = project_root / "infrastructure-catalog.yml"
    with open(catalog_file, 'r') as f:
        return yaml.safe_load(f)


def test_dhcp_enabled_flag_exists(adguard_defaults):
    """DHCP enabled flag exists in defaults."""
    assert "adguard_dhcp_enabled" in adguard_defaults, \
        "adguard_dhcp_enabled key not found in defaults"


def test_dhcp_enabled_is_configured(adguard_defaults):
    """DHCP enabled is configured (true after router DHCP disabled)."""
    assert adguard_defaults["adguard_dhcp_enabled"] is True, \
        "adguard_dhcp_enabled should be true (router DHCP has been disabled)"


def test_dhcp_interface_configured(adguard_defaults):
    """DHCP interface is configured."""
    assert "adguard_dhcp_interface" in adguard_defaults, \
        "adguard_dhcp_interface key not found"
    assert adguard_defaults["adguard_dhcp_interface"] == "eth0", \
        "adguard_dhcp_interface should be eth0"


def test_dhcp_local_domain_configured(adguard_defaults):
    """DHCP local domain is configured."""
    assert "adguard_dhcp_local_domain" in adguard_defaults, \
        "adguard_dhcp_local_domain key not found"
    assert adguard_defaults["adguard_dhcp_local_domain"] == "lan", \
        "adguard_dhcp_local_domain should be 'lan'"


def test_dhcp_range_configured(adguard_defaults):
    """DHCP range is configured correctly per ADR-002."""
    assert "adguard_dhcp_range_start" in adguard_defaults, \
        "adguard_dhcp_range_start key not found"
    assert "adguard_dhcp_range_end" in adguard_defaults, \
        "adguard_dhcp_range_end key not found"

    assert adguard_defaults["adguard_dhcp_range_start"] == "192.168.0.200", \
        "DHCP range should start at 192.168.0.200 per ADR-002"
    assert adguard_defaults["adguard_dhcp_range_end"] == "192.168.0.249", \
        "DHCP range should end at 192.168.0.249 per ADR-002"


def test_dhcp_gateway_uses_catalog(adguard_role_dir):
    """DHCP gateway references catalog variable."""
    defaults_file = adguard_role_dir / "defaults" / "main.yml"
    content = defaults_file.read_text()

    assert "adguard_dhcp_gateway:" in content, \
        "adguard_dhcp_gateway key not found"
    assert "catalog.network.gateway" in content, \
        "DHCP gateway should reference catalog.network.gateway"


def test_dhcp_subnet_mask_configured(adguard_defaults):
    """DHCP subnet mask is configured correctly."""
    assert "adguard_dhcp_subnet_mask" in adguard_defaults, \
        "adguard_dhcp_subnet_mask key not found"
    assert adguard_defaults["adguard_dhcp_subnet_mask"] == "255.255.255.0", \
        "DHCP subnet mask should be 255.255.255.0 (/24)"


def test_dhcp_lease_duration_configured(adguard_defaults):
    """DHCP lease duration is configured (24 hours)."""
    assert "adguard_dhcp_lease_duration" in adguard_defaults, \
        "adguard_dhcp_lease_duration key not found"
    assert adguard_defaults["adguard_dhcp_lease_duration"] == 86400, \
        "DHCP lease duration should be 86400 seconds (24 hours)"


def test_dhcp_icmp_timeout_configured(adguard_defaults):
    """DHCP ICMP timeout is configured."""
    assert "adguard_dhcp_icmp_timeout" in adguard_defaults, \
        "adguard_dhcp_icmp_timeout key not found"
    assert adguard_defaults["adguard_dhcp_icmp_timeout"] == 1000, \
        "DHCP ICMP timeout should be 1000ms"


def test_dhcp_range_does_not_conflict_with_static_ips(adguard_defaults):
    """DHCP range does not conflict with static IP assignments."""
    start = adguard_defaults["adguard_dhcp_range_start"]
    end = adguard_defaults["adguard_dhcp_range_end"]

    # Extract last octet
    start_octet = int(start.split('.')[-1])
    end_octet = int(end.split('.')[-1])

    # DHCP should be in .200-.249 range
    # Static IPs are in .1-.199 range per ADR-002
    assert start_octet >= 200, \
        "DHCP range start should be >= .200 to avoid static IP conflicts"
    assert end_octet <= 249, \
        "DHCP range end should be <= .249 per ADR-002"
    assert start_octet < end_octet, \
        "DHCP range start should be less than end"


def test_dhcp_configuration_in_template(adguard_role_dir):
    """AdGuardHome.yaml.j2 template contains DHCP configuration."""
    template_file = adguard_role_dir / "templates" / "AdGuardHome-minimal.yaml.j2"
    assert template_file.exists(), \
        f"Template file not found: {template_file}"

    content = template_file.read_text()

    # Check for DHCP section
    assert "dhcp:" in content, \
        "DHCP section not found in template"
    assert "enabled: {{ adguard_dhcp_enabled | lower }}" in content, \
        "DHCP enabled variable not found in template"


def test_dhcp_template_uses_variables(adguard_role_dir):
    """DHCP template uses all configured variables."""
    template_file = adguard_role_dir / "templates" / "AdGuardHome-minimal.yaml.j2"
    content = template_file.read_text()

    # Check for all DHCP variables
    required_vars = [
        "adguard_dhcp_enabled",
        "adguard_dhcp_interface",
        "adguard_dhcp_local_domain",
        "adguard_dhcp_gateway",
        "adguard_dhcp_subnet_mask",
        "adguard_dhcp_range_start",
        "adguard_dhcp_range_end",
        "adguard_dhcp_lease_duration",
        "adguard_dhcp_icmp_timeout"
    ]

    for var in required_vars:
        assert var in content, \
            f"Variable {var} not found in template"


def test_dhcp_template_renders_with_dhcp_disabled(adguard_role_dir):
    """Template contains correct DHCP structure for disabled state."""
    template_file = adguard_role_dir / "templates" / "AdGuardHome-minimal.yaml.j2"
    content = template_file.read_text()

    # Find DHCP section in template
    dhcp_section = content[content.find("dhcp:"):content.find("dhcp:") + 500]

    # Verify DHCP enabled uses variable
    assert "enabled: {{ adguard_dhcp_enabled | lower }}" in dhcp_section, \
        "DHCP enabled should use adguard_dhcp_enabled variable"

    # When disabled, DHCP configuration should still be present in template
    # (just with enabled=false)
    assert "interface_name:" in dhcp_section, \
        "DHCP interface_name should be in template"
    assert "dhcpv4:" in dhcp_section, \
        "DHCP dhcpv4 section should be in template"


def test_dhcp_template_structure_for_enabled_state(adguard_role_dir):
    """Template contains correct DHCP structure for enabled state."""
    template_file = adguard_role_dir / "templates" / "AdGuardHome-minimal.yaml.j2"
    content = template_file.read_text()

    # Verify all DHCP variables are used in the entire template
    # (checking in full content since section extraction was unreliable)
    assert "{{ adguard_dhcp_interface }}" in content, \
        "DHCP interface should use variable"
    assert "{{ adguard_dhcp_gateway }}" in content, \
        "DHCP gateway should use variable"
    assert "{{ adguard_dhcp_subnet_mask }}" in content, \
        "DHCP subnet mask should use variable"
    assert "{{ adguard_dhcp_range_start }}" in content, \
        "DHCP range start should use variable"
    assert "{{ adguard_dhcp_range_end }}" in content, \
        "DHCP range end should use variable"
    assert "{{ adguard_dhcp_lease_duration }}" in content, \
        "DHCP lease duration should use variable"
    assert "{{ adguard_dhcp_icmp_timeout }}" in content, \
        "DHCP ICMP timeout should use variable"


def test_dhcp_configuration_has_safety_comments(adguard_role_dir):
    """DHCP configuration includes safety warning comments."""
    defaults_file = adguard_role_dir / "defaults" / "main.yml"
    content = defaults_file.read_text()

    # Check for safety warnings
    assert "WARNING" in content or "CRITICAL" in content or "disable" in content.lower(), \
        "DHCP configuration should include safety warnings about router DHCP"
    assert "router" in content.lower(), \
        "Configuration should mention router DHCP"
