"""
Tests for PCIe ASPM GRUB configuration tasks.

This test suite validates the host-proxmox role's PCIe ASPM configuration
tasks for disabling Active State Power Management to prevent network card
disconnections.
"""

import pytest
import yaml
from pathlib import Path


def test_pcie_aspm_task_files_exist(project_root):
    """PCIe ASPM GRUB configuration task files exist in host-proxmox role."""
    role_dir = project_root / "configuration-by-ansible" / "host-proxmox"
    tasks_dir = role_dir / "tasks"

    assert tasks_dir.exists(), f"Tasks directory not found: {tasks_dir}"

    # Check required task files
    required_tasks = [
        "grub-pcie-aspm-check.yml",
        "grub-pcie-aspm-backup.yml",
        "grub-pcie-aspm-configure.yml",
        "grub-pcie-aspm-update.yml",
        "grub-pcie-aspm-verify.yml",
    ]

    for task_file in required_tasks:
        task_path = tasks_dir / task_file
        assert task_path.exists(), f"Required task file not found: {task_file}"


def test_check_pcie_aspm_grub_task_structure(project_root):
    """Check PCIe ASPM GRUB config task reads /etc/default/grub and registers fact."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm-check.yml"

    assert task_file.exists(), f"Check task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for GRUB config file reading
    assert "/etc/default/grub" in task_content, "Task should read /etc/default/grub"

    # Check for pcie_aspm=off string search
    assert "pcie_aspm=off" in task_content, "Task should check for pcie_aspm=off parameter"

    # Check for fact registration
    assert "set_fact" in task_content or "register" in task_content, \
        "Task should register the result as a fact"


def test_backup_grub_config_pcie_aspm_task(project_root):
    """GRUB backup task creates timestamped backup before PCIe ASPM modification."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm-backup.yml"

    assert task_file.exists(), f"Backup task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for copy module usage
    assert "copy" in task_content.lower(), "Task should use copy module for backup"
    assert "remote_src" in task_content, "Task should use remote_src for local copy"

    # Check for source and destination paths
    assert "/etc/default/grub" in task_content, "Task should backup /etc/default/grub"
    assert ".backup" in task_content or "backup" in task_content.lower(), \
        "Backup filename should include 'backup'"

    # Check for timestamp in destination
    assert "ansible_date_time" in task_content or "date" in task_content.lower(), \
        "Task should use timestamp in backup filename"


def test_configure_grub_pcie_aspm_task(project_root):
    """GRUB PCIe ASPM configuration task adds pcie_aspm=off parameter using replace module."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm-configure.yml"

    assert task_file.exists(), f"Configure task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for replace module usage
    assert "replace" in task_content.lower(), "Task should use replace module for GRUB modification"

    # Check for GRUB config file target
    assert "/etc/default/grub" in task_content, "Task should modify /etc/default/grub"

    # Check for GRUB_CMDLINE_LINUX_DEFAULT
    assert "GRUB_CMDLINE_LINUX_DEFAULT" in task_content, \
        "Task should target GRUB_CMDLINE_LINUX_DEFAULT"

    # Check for pcie_aspm=off parameter
    assert "pcie_aspm=off" in task_content, "Task should add pcie_aspm=off parameter"

    # Check for regexp pattern
    assert "regexp" in task_content.lower(), "Task should use regexp for pattern matching"


def test_update_grub_pcie_aspm_task(project_root):
    """Update GRUB task runs update-grub command after PCIe ASPM configuration."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm-update.yml"

    assert task_file.exists(), f"Update GRUB task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for command module usage
    assert "command" in task_content.lower() or "shell" in task_content.lower(), \
        "Task should use command or shell module to run update-grub"

    # Check for update-grub command
    assert "update-grub" in task_content.lower() or "grub-mkconfig" in task_content.lower(), \
        "Task should run update-grub or grub-mkconfig command"

    # Check for result registration or notification
    assert "register" in task_content.lower() or "debug" in task_content.lower(), \
        "Task should register result or display message"


def test_verify_pcie_aspm_task(project_root):
    """Verify PCIe ASPM task checks /proc/cmdline for pcie_aspm=off parameter."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm-verify.yml"

    assert task_file.exists(), f"Verify task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for /proc/cmdline reading
    assert "/proc/cmdline" in task_content, "Task should read /proc/cmdline"

    # Check for pcie_aspm=off parameter check
    assert "pcie_aspm=off" in task_content or "pcie_aspm" in task_content.lower(), \
        "Task should check for pcie_aspm=off parameter"

    # Check for fact registration or debug output
    assert "register" in task_content.lower() or "debug" in task_content.lower(), \
        "Task should register result or display verification message"
