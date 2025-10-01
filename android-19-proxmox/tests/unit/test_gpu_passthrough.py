"""
Tests for GPU passthrough configuration role.

This test suite validates the host-proxmox-gpu-passthrough role structure
and configuration for Nvidia GPU passthrough setup.
"""

import pytest
import yaml
from pathlib import Path


def test_gpu_passthrough_role_exists(project_root):
    """GPU passthrough role directory exists with required structure."""
    role_dir = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough"

    assert role_dir.exists(), f"Role directory not found: {role_dir}"

    # Check required directories
    assert (role_dir / "tasks").exists(), "Role missing tasks directory"
    assert (role_dir / "defaults").exists(), "Role missing defaults directory"

    # Check required task files
    assert (role_dir / "tasks" / "main.yml").exists(), "Role missing tasks/main.yml"
    assert (role_dir / "tasks" / "identify-gpu.yml").exists(), "Role missing tasks/identify-gpu.yml"


def test_gpu_defaults_configuration(project_root):
    """GPU passthrough defaults contain expected hardware configuration."""
    defaults_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "defaults" / "main.yml"

    assert defaults_file.exists(), f"Defaults file not found: {defaults_file}"

    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    # Verify GPU hardware configuration from README.md
    assert "gpu_model" in defaults, "Missing gpu_model in defaults"
    assert "RTX 5060Ti" in defaults["gpu_model"], "Expected RTX 5060Ti GPU model"

    assert "gpu_vendor_id" in defaults, "Missing gpu_vendor_id in defaults"
    assert defaults["gpu_vendor_id"] == "10de", "Expected NVIDIA vendor ID (10de)"


def test_identify_gpu_task_structure(project_root):
    """GPU identification task uses correct lspci command."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "identify-gpu.yml"

    assert task_file.exists(), f"GPU identification task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    # Check for lspci command usage
    task_content = str(tasks)
    assert "lspci" in task_content, "Task should use lspci command to detect GPU"
    assert "NVIDIA" in task_content or "nvidia" in task_content.lower(), "Task should filter for NVIDIA GPU"
