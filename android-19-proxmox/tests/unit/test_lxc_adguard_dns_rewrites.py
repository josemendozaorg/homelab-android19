"""Tests for AdGuard DNS rewrites configuration."""
import pytest
import yaml
from pathlib import Path


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


def test_adguard_defaults_file_exists(adguard_role_dir):
    """AdGuard defaults/main.yml file exists."""
    defaults_file = adguard_role_dir / "defaults" / "main.yml"
    assert defaults_file.exists(), f"Defaults file not found: {defaults_file}"


def test_adguard_dns_rewrites_list_exists(adguard_defaults):
    """DNS rewrites list exists in defaults."""
    assert "adguard_dns_rewrites" in adguard_defaults, \
        "adguard_dns_rewrites key not found in defaults"
    assert isinstance(adguard_defaults["adguard_dns_rewrites"], list), \
        "adguard_dns_rewrites should be a list"


def test_coolify_dns_rewrite_exists(adguard_defaults):
    """DNS rewrite for coolify.homelab exists."""
    rewrites = adguard_defaults["adguard_dns_rewrites"]
    coolify_rewrite = next(
        (r for r in rewrites if r.get("domain") == "coolify.homelab"),
        None
    )
    assert coolify_rewrite is not None, \
        "coolify.homelab DNS rewrite not found"
    assert "ip" in coolify_rewrite, \
        "coolify.homelab rewrite missing IP"


def test_ollama_dns_rewrite_exists(adguard_defaults):
    """DNS rewrite for ollama.homelab exists."""
    rewrites = adguard_defaults["adguard_dns_rewrites"]
    ollama_rewrite = next(
        (r for r in rewrites if r.get("domain") == "ollama.homelab"),
        None
    )
    assert ollama_rewrite is not None, \
        "ollama.homelab DNS rewrite not found"
    assert "ip" in ollama_rewrite, \
        "ollama.homelab rewrite missing IP"


def test_vllm_dns_rewrite_exists(adguard_defaults):
    """DNS rewrite for vllm.homelab exists."""
    rewrites = adguard_defaults["adguard_dns_rewrites"]
    vllm_rewrite = next(
        (r for r in rewrites if r.get("domain") == "vllm.homelab"),
        None
    )
    assert vllm_rewrite is not None, \
        "vllm.homelab DNS rewrite not found"
    assert "ip" in vllm_rewrite, \
        "vllm.homelab rewrite missing IP"


def test_dns_rewrites_use_catalog_references(adguard_role_dir):
    """DNS rewrites use catalog variable references, not hardcoded IPs."""
    defaults_file = adguard_role_dir / "defaults" / "main.yml"
    content = defaults_file.read_text()

    # Check for catalog references
    assert "catalog.services[160].ip" in content, \
        "coolify.homelab should reference catalog.services[160].ip"
    assert "catalog.services[140].ip" in content, \
        "AI Machine services should reference catalog.services[140].ip"

    # Ensure no hardcoded IPs for these services
    rewrites_section = content[content.find("adguard_dns_rewrites"):]
    coolify_section = rewrites_section[rewrites_section.find("coolify.homelab"):rewrites_section.find("coolify.homelab") + 200]
    assert "192.168.0.160" not in coolify_section, \
        "coolify.homelab should not have hardcoded IP"


def test_existing_dns_rewrites_preserved(adguard_defaults):
    """Existing DNS rewrites for proxmox, pve, adguard, dns remain unchanged."""
    rewrites = adguard_defaults["adguard_dns_rewrites"]
    domains = [r.get("domain") for r in rewrites]

    assert "proxmox.homelab" in domains, \
        "proxmox.homelab rewrite should be preserved"
    assert "pve.homelab" in domains, \
        "pve.homelab rewrite should be preserved"
    assert "adguard.homelab" in domains, \
        "adguard.homelab rewrite should be preserved"
    assert "dns.homelab" in domains, \
        "dns.homelab rewrite should be preserved"


def test_dns_rewrites_count(adguard_defaults):
    """DNS rewrites list has expected number of entries."""
    rewrites = adguard_defaults["adguard_dns_rewrites"]
    # Should have 4 existing + 3 new = 7 entries
    assert len(rewrites) >= 7, \
        f"Expected at least 7 DNS rewrites, found {len(rewrites)}"
