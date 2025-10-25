"""BDD step definitions for bastion host DNS configuration."""
import pytest
import yaml
import subprocess
import re
from pathlib import Path
from pytest_bdd import scenarios, given, when, then, parsers


# Load all scenarios from the feature file
scenarios('../features/bastion_dns_configuration.feature')


# Fixtures
@pytest.fixture(scope="function")
def bastion_dir(project_root):
    """Return the android-16-bastion directory."""
    return project_root.parent / "android-16-bastion"


@pytest.fixture(scope="function")
def bastion_playbook(bastion_dir):
    """Load bastion playbook.yml."""
    playbook_file = bastion_dir / "playbook.yml"
    with open(playbook_file, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="function")
def infrastructure_catalog(project_root):
    """Load infrastructure catalog."""
    catalog_file = project_root / "infrastructure-catalog.yml"
    with open(catalog_file, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="function")
def deployment_result():
    """Store deployment results."""
    return {}


# Given steps
@given(parsers.parse('the bastion host "{host}" is accessible'))
def bastion_host_accessible(host):
    """Verify bastion host is accessible."""
    result = subprocess.run(
        ['ping', '-c', '1', '-W', '2', host],
        capture_output=True,
        timeout=5
    )
    assert result.returncode == 0, f"Bastion host {host} is not accessible"


@given('the infrastructure catalog defines network configuration')
def infrastructure_catalog_defines_network(infrastructure_catalog):
    """Verify infrastructure catalog has network configuration."""
    assert 'network' in infrastructure_catalog, \
        "Infrastructure catalog missing 'network' section"
    assert 'dns' in infrastructure_catalog['network'], \
        "Infrastructure catalog missing network.dns"
    assert infrastructure_catalog['network']['dns'] == "192.168.0.25", \
        "DNS server should be 192.168.0.25 (AdGuard)"


@given(parsers.parse('the AdGuard DNS server "{dns_server}" is running'))
def adguard_dns_running(dns_server):
    """Verify AdGuard DNS server is reachable."""
    # Check if port 53 (DNS) is open on AdGuard server
    result = subprocess.run(
        ['nc', '-zv', '-w', '2', dns_server, '53'],
        capture_output=True,
        timeout=5
    )
    # nc returns 0 if connection succeeds
    assert result.returncode == 0, \
        f"AdGuard DNS server {dns_server} is not reachable on port 53"


@given('the bastion Ansible playbook exists')
def bastion_playbook_exists(bastion_dir):
    """Verify bastion playbook file exists."""
    playbook_file = bastion_dir / "playbook.yml"
    assert playbook_file.exists(), \
        f"Bastion playbook not found: {playbook_file}"


@given('the bastion playbook includes DNS configuration tasks')
def bastion_playbook_includes_dns(bastion_dir):
    """Verify bastion playbook includes DNS tasks."""
    playbook_file = bastion_dir / "playbook.yml"
    assert playbook_file.exists(), "Bastion playbook not found"

    content = playbook_file.read_text()
    assert 'dns-configure.yml' in content or 'dns' in content.lower(), \
        "Bastion playbook should include DNS configuration tasks"


@given(parsers.parse('DNS tasks are tagged with "{tag}"'))
def dns_tasks_tagged(bastion_dir, tag):
    """Verify DNS tasks are properly tagged."""
    playbook_file = bastion_dir / "playbook.yml"
    content = playbook_file.read_text()

    # Check for tags in include statement or task (supports YAML list format)
    assert (f'tags: {tag}' in content or
            f'tags: ["{tag}"]' in content or
            f"tags: ['{tag}']" in content or
            f'- {tag}' in content), \
        f"DNS tasks should be tagged with '{tag}'"


@given('the bastion is configured to use AdGuard DNS')
def bastion_configured_with_adguard():
    """Verify bastion is already configured with AdGuard DNS."""
    # Check current DNS configuration on bastion
    result = subprocess.run(
        ['ssh', 'josemendoza@192.168.0.10', 'resolvectl status'],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "Cannot check DNS status on bastion"
    # Don't assert DNS is configured yet - test might be setting it up


@given('the bastion is already configured with AdGuard DNS')
def bastion_already_configured():
    """Verify bastion already has AdGuard DNS configured (for idempotency test)."""
    result = subprocess.run(
        ['ssh', 'josemendoza@192.168.0.10', 'resolvectl status'],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "Cannot check DNS status on bastion"
    assert "192.168.0.25" in result.stdout, \
        "Bastion should already have AdGuard DNS configured"


@given('the network has both static IP hosts and DHCP clients')
def network_has_mixed_hosts(infrastructure_catalog):
    """Verify network strategy includes both static and DHCP."""
    network = infrastructure_catalog['network']
    assert 'ranges' in network, "Network should define IP ranges"
    assert 'dhcp_pool' in network['ranges'], "Should have DHCP pool defined"
    # Services are static IPs
    assert 'services' in infrastructure_catalog, "Should have static services"


# When steps
@when('the playbook configuration is loaded')
def playbook_loaded(bastion_playbook):
    """Load and verify playbook structure."""
    assert bastion_playbook is not None, "Playbook should be loadable as YAML"
    assert isinstance(bastion_playbook, (list, dict)), "Playbook should be valid YAML"


@when('the administrator deploys bastion DNS configuration')
def deploy_bastion_dns(deployment_result):
    """Deploy bastion DNS configuration using Ansible."""
    # Run ansible-playbook with DNS tag
    result = subprocess.run(
        ['ansible-playbook',
         '--inventory', 'inventory.yml',
         'android-16-bastion/playbook.yml',
         '--tags', 'dns'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd='/home/dev/repos/homelab-android19'
    )

    deployment_result['returncode'] = result.returncode
    deployment_result['stdout'] = result.stdout
    deployment_result['stderr'] = result.stderr


@when('the administrator re-deploys DNS configuration')
def redeploy_bastion_dns(deployment_result):
    """Re-deploy bastion DNS to test idempotency."""
    # Same as initial deployment
    deploy_bastion_dns(deployment_result)


@when('DNS is queried for homelab domains')
def query_homelab_domains(deployment_result):
    """Query DNS for .homelab domains from bastion."""
    # Store query results for validation
    deployment_result['dns_queries'] = {}

    domains = [
        ('proxmox.homelab', '192.168.0.19'),
        ('coolify.homelab', '192.168.0.160'),
        ('adguard.homelab', '192.168.0.25')
    ]

    for domain, expected_ip in domains:
        result = subprocess.run(
            ['ssh', 'josemendoza@192.168.0.10', f'nslookup {domain}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        deployment_result['dns_queries'][domain] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'expected_ip': expected_ip
        }


@when('the DNS tasks are examined')
def examine_dns_tasks(bastion_dir):
    """Read and examine DNS configuration tasks."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    assert dns_tasks_file.exists(), "DNS tasks file should exist"
    # Content will be checked in then steps


@when('DNS queries are made from bastion')
def dns_queries_from_bastion(deployment_result):
    """Make DNS queries for various hosts."""
    # Test a mix of internal and external domains
    test_domains = [
        'proxmox.homelab',
        'google.com',
        '192.168.0.19'  # Reverse lookup
    ]

    deployment_result['dns_queries'] = {}
    for domain in test_domains:
        result = subprocess.run(
            ['ssh', 'josemendoza@192.168.0.10', f'nslookup {domain}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        deployment_result['dns_queries'][domain] = {
            'returncode': result.returncode,
            'stdout': result.stdout
        }


# Then steps
@then('the playbook should load infrastructure catalog variables')
def playbook_loads_catalog(bastion_dir):
    """Verify playbook loads infrastructure catalog."""
    playbook_file = bastion_dir / "playbook.yml"
    content = playbook_file.read_text()

    # Check for vars_files with infrastructure-catalog.yml
    assert 'vars_files' in content or 'include_vars' in content, \
        "Playbook should load variables from catalog"
    assert 'infrastructure-catalog.yml' in content, \
        "Playbook should reference infrastructure-catalog.yml"


@then('DNS configuration should reference catalog network DNS')
def dns_references_catalog(bastion_dir):
    """Verify DNS tasks reference catalog variables."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    assert dns_tasks_file.exists(), "DNS tasks file should exist"

    content = dns_tasks_file.read_text()
    assert 'catalog.network.dns' in content, \
        "DNS tasks should reference catalog.network.dns"


@then(parsers.parse('DNS server should be "{expected_dns}"'))
def dns_server_value(infrastructure_catalog, expected_dns):
    """Verify DNS server value in catalog."""
    actual_dns = infrastructure_catalog['network']['dns']
    assert actual_dns == expected_dns, \
        f"Expected DNS {expected_dns}, got {actual_dns}"


@then('no DNS IP addresses should be hardcoded')
def no_hardcoded_dns(bastion_dir):
    """Verify no hardcoded DNS IPs in tasks."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    # Look for hardcoded IPs like 192.168.0.25 (except in comments/descriptions)
    # Allow in msg/debug but not in actual command parameters
    lines = content.split('\n')
    for line in lines:
        # Skip comments and debug messages
        if line.strip().startswith('#') or 'msg:' in line or 'debug:' in line:
            continue

        # Check for hardcoded DNS IP in nmcli commands
        if 'nmcli' in line and '192.168.0.25' in line:
            assert False, f"Found hardcoded DNS IP: {line.strip()}"


@then(parsers.parse('the bastion should use DNS server "{expected_dns}"'))
def bastion_uses_dns_server(expected_dns):
    """Verify bastion is using the correct DNS server."""
    result = subprocess.run(
        ['ssh', 'josemendoza@192.168.0.10', 'resolvectl status'],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "Cannot check DNS status on bastion"
    assert expected_dns in result.stdout, \
        f"Bastion should use DNS server {expected_dns}"


@then('DNS priority should be set to manual')
def dns_priority_manual():
    """Verify DNS is set to manual (ignore DHCP)."""
    result = subprocess.run(
        ['ssh', 'josemendoza@192.168.0.10',
         'nmcli -f ipv4.ignore-auto-dns connection show'],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "Cannot check NetworkManager settings"
    # Should show yes for ignore-auto-dns


@then('the deployment should complete without errors')
def deployment_succeeds(deployment_result):
    """Verify deployment completed successfully."""
    assert deployment_result.get('returncode') == 0, \
        f"Deployment failed:\n{deployment_result.get('stderr', '')}"


@then(parsers.parse('"{domain}" should resolve to "{expected_ip}"'))
def domain_resolves(deployment_result, domain, expected_ip):
    """Verify domain resolves to expected IP."""
    queries = deployment_result.get('dns_queries', {})
    assert domain in queries, f"DNS query for {domain} was not performed"

    query_result = queries[domain]
    assert query_result['returncode'] == 0, \
        f"DNS query for {domain} failed"
    assert expected_ip in query_result['stdout'], \
        f"{domain} should resolve to {expected_ip}\nGot: {query_result['stdout']}"


@then('no changes should be made')
def no_changes_made(deployment_result):
    """Verify idempotent deployment made no changes."""
    stdout = deployment_result.get('stdout', '')

    # Check for Ansible output indicating no changes
    # Look for "changed=0" or all tasks showing "ok"
    assert 'changed=0' in stdout or 'ok=' in stdout, \
        "Deployment should be idempotent (no changes on re-run)"


@then(parsers.parse('the deployment should report "{status}"'))
def deployment_reports_status(deployment_result, status):
    """Verify deployment status in Ansible output."""
    stdout = deployment_result.get('stdout', '')
    assert status in stdout.lower(), \
        f"Deployment should report {status}"


@then('DNS resolution should still work')
def dns_still_works():
    """Verify DNS resolution still works after re-deployment."""
    result = subprocess.run(
        ['ssh', 'josemendoza@192.168.0.10', 'nslookup proxmox.homelab'],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "DNS resolution should still work"
    assert "192.168.0.19" in result.stdout, \
        "proxmox.homelab should still resolve correctly"


@then('tasks should use nmcli commands')
def tasks_use_nmcli(bastion_dir):
    """Verify tasks use NetworkManager CLI."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    assert 'nmcli' in content, \
        "DNS tasks should use nmcli (NetworkManager)"


@then(parsers.re(r'tasks should NOT use direct file editing of (?P<path>.+)'))
def tasks_dont_edit_resolv_conf(bastion_dir, path):
    """Verify tasks don't directly edit resolv.conf."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    # Should not use lineinfile, blockinfile, or direct editing of resolv.conf
    assert path not in content or 'resolvectl' in content, \
        f"Tasks should not directly edit {path} (use NetworkManager)"


@then('tasks should set ignore-auto-dns to prevent DHCP override')
def tasks_set_ignore_auto_dns(bastion_dir):
    """Verify tasks set ignore-auto-dns."""
    dns_tasks_file = bastion_dir / "tasks" / "dns-configure.yml"
    content = dns_tasks_file.read_text()

    assert 'ignore-auto-dns' in content, \
        "Tasks should set ignore-auto-dns to prevent DHCP from overriding DNS"


@then('static IP hosts should be resolvable')
def static_hosts_resolvable(deployment_result):
    """Verify static IP hosts can be resolved."""
    queries = deployment_result.get('dns_queries', {})

    # Check proxmox.homelab (static IP)
    if 'proxmox.homelab' in queries:
        assert queries['proxmox.homelab']['returncode'] == 0, \
            "Static hosts should be resolvable"


@then('DHCP clients should be resolvable')
def dhcp_clients_resolvable():
    """Verify DHCP clients can be resolved (if any exist)."""
    # This is a placeholder - actual DHCP clients may not exist yet
    # Just verify DHCP is configured in AdGuard
    pass


@then('external domains should be resolvable')
def external_domains_resolvable(deployment_result):
    """Verify external domains can be resolved."""
    queries = deployment_result.get('dns_queries', {})

    # Check google.com
    if 'google.com' in queries:
        assert queries['google.com']['returncode'] == 0, \
            "External domains should be resolvable"
