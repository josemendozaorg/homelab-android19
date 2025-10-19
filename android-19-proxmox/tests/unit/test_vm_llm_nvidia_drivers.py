"""Unit tests for NVIDIA driver installation tasks in vm-llm-aimachine role."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def nvidia_tasks_file(project_root):
    """NVIDIA driver tasks file."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine" / "tasks" / "nvidia-drivers.yml"


def test_nvidia_drivers_task_file_exists(nvidia_tasks_file):
    """nvidia-drivers.yml should exist."""
    assert nvidia_tasks_file.exists(), "nvidia-drivers.yml not found"


def test_nvidia_drivers_task_valid_yaml(nvidia_tasks_file):
    """nvidia-drivers.yml should be valid YAML."""
    with open(nvidia_tasks_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "nvidia-drivers.yml should not be empty"
    assert isinstance(data, list), "nvidia-drivers.yml should contain a list of tasks"


def test_nvidia_drivers_has_detection_task(nvidia_tasks_file):
    """Should have task to detect available NVIDIA drivers."""
    content = nvidia_tasks_file.read_text()
    assert 'ubuntu-drivers devices' in content or 'ubuntu-drivers list' in content, \
           "Should use ubuntu-drivers to detect available drivers"


def test_nvidia_drivers_prefers_open_kernel(nvidia_tasks_file):
    """Should prefer open-kernel driver versions."""
    content = nvidia_tasks_file.read_text()
    # Check for open-kernel preference logic
    assert 'open' in content.lower(), \
           "Should have logic to prefer open-kernel driver versions"


def test_nvidia_drivers_has_installation_task(nvidia_tasks_file):
    """Should have task to install NVIDIA drivers."""
    content = nvidia_tasks_file.read_text()
    assert 'ubuntu-drivers' in content and ('install' in content or 'autoinstall' in content), \
           "Should use ubuntu-drivers to install drivers"


def test_nvidia_drivers_has_nvidia_smi_verification(nvidia_tasks_file):
    """Should verify installation with nvidia-smi."""
    content = nvidia_tasks_file.read_text()
    assert 'nvidia-smi' in content, \
           "Should verify driver installation with nvidia-smi"


def test_nvidia_drivers_has_dmesg_check(nvidia_tasks_file):
    """Should check dmesg for NVIDIA kernel module loading."""
    content = nvidia_tasks_file.read_text()
    assert 'dmesg' in content and 'nvidia' in content.lower(), \
           "Should check dmesg for NVIDIA kernel module loading"


def test_nvidia_drivers_has_cuda_verification(nvidia_tasks_file):
    """Should verify CUDA availability and version."""
    content = nvidia_tasks_file.read_text()
    # Check for CUDA verification (nvcc, nvidia-smi CUDA version, etc.)
    assert 'cuda' in content.lower() or 'nvcc' in content, \
           "Should verify CUDA availability"


def test_nvidia_drivers_has_idempotency_check(nvidia_tasks_file):
    """Installation should be idempotent (check if already installed)."""
    content = nvidia_tasks_file.read_text()
    # Look for when/changed_when clauses or stat checks
    assert 'when:' in content or 'stat:' in content or 'register:' in content, \
           "Should have idempotency checks (when/stat/register)"


def test_nvidia_drivers_has_reboot_handling(nvidia_tasks_file):
    """Should handle system reboot if kernel modules need loading."""
    content = nvidia_tasks_file.read_text()
    # Check for reboot task or handler
    assert 'reboot' in content.lower() or 'restart' in content.lower(), \
           "Should handle system reboot for driver loading"
