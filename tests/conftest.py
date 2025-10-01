"""Shared pytest fixtures for infrastructure testing."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def catalog(project_root):
    """Load infrastructure catalog once for all tests."""
    catalog_path = project_root / "android-19-proxmox" / "infrastructure-catalog.yml"
    with open(catalog_path) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def catalog_services(catalog):
    """Return services from the catalog."""
    return catalog.get('services', {})


@pytest.fixture(scope="session")
def catalog_network(catalog):
    """Return network configuration from the catalog."""
    return catalog.get('network', {})
