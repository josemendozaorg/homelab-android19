"""Unit tests for bastion host DNS configuration."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="module")
def bastion_dir(project_root):
    """Return the android-16-bastion directory."""
    return project_root.parent / "android-16-bastion"


@pytest.fixture(scope="module")
def bastion_playbook(bastion_dir):
    """Load bastion playbook.yml."""
    playbook_file = bastion_dir / "playbook.yml"
    with open(playbook_file, 'r') as f:
        playbook_data = yaml.safe_load(f)
        # Handle both single playbook and list of plays
        return playbook_data if isinstance(playbook_data, list) else [playbook_data]


@pytest.fixture(scope="module")
def infrastructure_catalog(project_root):
    """Load infrastructure catalog."""
    catalog_file = project_root / "infrastructure-catalog.yml"
    with open(catalog_file, 'r') as f:
        return yaml.safe_load(f)


def test_bastion_playbook_exists(bastion_dir):
    """Bastion playbook file exists."""
    playbook_file = bastion_dir / "playbook.yml"
    assert playbook_file.exists(), \
        f"Bastion playbook not found: {playbook_file}"


def test_bastion_playbook_valid_yaml(bastion_playbook):
    """Bastion playbook is valid YAML."""
    assert bastion_playbook is not None, \
        "Playbook should be loadable as YAML"
    assert isinstance(bastion_playbook, list), \
        "Playbook should be a list of plays"


def test_bastion_playbook_targets_bastion_group(bastion_playbook):
    """Bastion playbook targets the bastion host group."""
    # Get first play
    first_play = bastion_playbook[0]
    assert 'hosts' in first_play, \
        "Playbook should specify hosts"
    assert first_play['hosts'] == 'bastion', \
        "Playbook should target 'bastion' host group"


def test_bastion_playbook_loads_catalog(bastion_dir):
    """Bastion playbook loads infrastructure catalog variables."""
    playbook_file = bastion_dir / "playbook.yml"
    content = playbook_file.read_text()

    # Check for vars_files or include_vars with infrastructure-catalog.yml
    assert ('vars_files' in content and 'infrastructure-catalog.yml' in content) or \
           ('include_vars' in content and 'infrastructure-catalog.yml' in content), \
        "Playbook should load infrastructure-catalog.yml variables"


def test_bastion_playbook_includes_dns_tasks(bastion_dir):
    """Bastion playbook includes DNS configuration tasks."""
    playbook_file = bastion_dir / "playbook.yml"
    content = playbook_file.read_text()

    # Check for include of dns-configure.yml
    assert 'dns-configure.yml' in content, \
        "Playbook should include dns-configure.yml tasks"


def test_bastion_dns_tasks_file_exists(bastion_dir):
    """DNS configuration tasks file exists."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    assert dns_tasks_file.exists(), \
        f"DNS tasks file not found: {dns_tasks_file}"


def test_bastion_dns_tasks_valid_yaml(bastion_dir):
    """DNS configuration tasks are valid YAML."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    with open(dns_tasks_file, 'r') as f:
        tasks = yaml.safe_load(f)

    assert tasks is not None, \
        "DNS tasks should be valid YAML"
    # Tasks can be a list or a single dict
    assert isinstance(tasks, (list, dict)), \
        "DNS tasks should be a list or dict"


def test_bastion_dns_tasks_reference_catalog(bastion_dir):
    """DNS tasks reference catalog.network.dns variable."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    assert 'catalog.network.dns' in content, \
        "DNS tasks should reference catalog.network.dns variable"


def test_bastion_dns_tasks_no_hardcoded_ips(bastion_dir):
    """DNS tasks do not contain hardcoded DNS IP addresses."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Skip comments and debug/msg statements
        if line.strip().startswith('#') or 'msg:' in line or 'debug:' in line:
            continue

        # Check for hardcoded DNS IP in nmcli commands
        if 'nmcli' in line and '192.168.0.25' in line and 'catalog' not in line:
            assert False, \
                f"Found hardcoded DNS IP at line {i}: {line.strip()}\n" \
                f"Should use {{ catalog.network.dns }} instead"


def test_bastion_dns_tasks_use_nmcli(bastion_dir):
    """DNS tasks use NetworkManager (nmcli) for configuration."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    assert 'nmcli' in content, \
        "DNS tasks should use nmcli (NetworkManager CLI)"


def test_bastion_dns_tasks_dont_edit_resolv_conf(bastion_dir):
    """DNS tasks do not directly edit /etc/resolv.conf."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    # Should not use file editing modules on /etc/resolv.conf
    # It's OK to read it with resolvectl, but not edit directly
    lines = content.split('\n')
    for line in lines:
        if '/etc/resolv.conf' in line:
            # Allow in debug messages or read-only commands
            assert any(keyword in line for keyword in ['msg:', 'debug:', 'resolvectl', 'cat', '#']), \
                "Tasks should not directly edit /etc/resolv.conf - use NetworkManager instead"


def test_bastion_dns_tasks_set_ignore_auto_dns(bastion_dir):
    """DNS tasks set ignore-auto-dns to prevent DHCP override."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    assert 'ignore-auto-dns' in content or 'ipv4.ignore-auto-dns' in content, \
        "DNS tasks should set ignore-auto-dns to prevent DHCP from overriding manual DNS"


def test_bastion_dns_tasks_are_tagged(bastion_dir):
    """DNS tasks are tagged for selective deployment."""
    playbook_file = bastion_dir / "playbook.yml"
    content = playbook_file.read_text()

    # Check for tags: dns in the include or task
    assert 'tags:' in content and 'dns' in content, \
        "DNS tasks should be tagged with 'dns' for selective deployment"


def test_catalog_defines_adguard_dns(infrastructure_catalog):
    """Infrastructure catalog defines AdGuard as DNS server."""
    assert 'network' in infrastructure_catalog, \
        "Catalog should have network section"
    assert 'dns' in infrastructure_catalog['network'], \
        "Catalog should define network.dns"
    assert infrastructure_catalog['network']['dns'] == "192.168.0.25", \
        "DNS should be AdGuard at 192.168.0.25"


def test_bastion_dns_tasks_verify_configuration(bastion_dir):
    """DNS tasks include verification steps."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    # Should verify DNS configuration (resolvectl or similar)
    assert 'resolvectl' in content or 'nslookup' in content or 'verify' in content.lower(), \
        "DNS tasks should include verification steps"


def test_bastion_dns_tasks_have_descriptions(bastion_dir):
    """DNS tasks have descriptive names."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    with open(dns_tasks_file, 'r') as f:
        tasks = yaml.safe_load(f)

    # Tasks should be a list
    if isinstance(tasks, list):
        for task in tasks:
            if isinstance(task, dict):
                assert 'name' in task or 'ansible.builtin.debug' in str(task), \
                    "Each task should have a descriptive name"


def test_bastion_inventory_defines_bastion(project_root):
    """Ansible inventory defines bastion host."""
    inventory_file = project_root.parent / "inventory.yml"
    with open(inventory_file, 'r') as f:
        inventory = yaml.safe_load(f)

    assert 'all' in inventory, "Inventory should have 'all' group"
    assert 'children' in inventory['all'], "Inventory should have children"
    assert 'bastion' in inventory['all']['children'], \
        "Inventory should define 'bastion' host group"


def test_bastion_inventory_has_correct_ip(project_root):
    """Bastion host in inventory has correct IP address."""
    inventory_file = project_root.parent / "inventory.yml"
    with open(inventory_file, 'r') as f:
        inventory = yaml.safe_load(f)

    bastion_group = inventory['all']['children']['bastion']
    assert 'hosts' in bastion_group, "Bastion group should have hosts"

    # Get first host in bastion group
    bastion_hosts = bastion_group['hosts']
    first_host = list(bastion_hosts.values())[0]

    assert 'ansible_host' in first_host, \
        "Bastion host should have ansible_host defined"
    assert first_host['ansible_host'] == "192.168.0.10", \
        "Bastion should be at 192.168.0.10"
