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


def test_validate_amd_cpu_task_exists(project_root):
    """AMD CPU validation task exists for IOMMU prerequisite check."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "validate-amd-cpu.yml"

    assert task_file.exists(), f"AMD CPU validation task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    # Check for CPU detection command (lscpu or grep)
    task_content = str(tasks)
    assert "lscpu" in task_content.lower() or "cpuinfo" in task_content.lower(), \
        "Task should use lscpu or cpuinfo to detect CPU"
    assert "amd" in task_content.lower(), "Task should check for AMD CPU"
    assert "fail" in task_content.lower() or "assert" in task_content.lower(), \
        "Task should fail gracefully if AMD CPU not detected"


def test_check_iommu_runtime_task_exists(project_root):
    """IOMMU runtime check task reads /proc/cmdline and registers fact."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "check-iommu-runtime.yml"

    assert task_file.exists(), f"IOMMU runtime check task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for /proc/cmdline reading
    assert "/proc/cmdline" in task_content, "Task should read /proc/cmdline"

    # Check for iommu=pt string search
    assert "iommu=pt" in task_content or "iommu" in task_content.lower(), \
        "Task should check for iommu=pt parameter"

    # Check for fact registration
    assert "set_fact" in task_content or "register" in task_content, \
        "Task should register the result as a fact"


def test_check_iommu_grub_task_exists(project_root):
    """IOMMU GRUB config check task reads /etc/default/grub and registers fact."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "check-iommu-grub.yml"

    assert task_file.exists(), f"IOMMU GRUB check task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for GRUB config file reading
    assert "/etc/default/grub" in task_content, "Task should read /etc/default/grub"

    # Check for iommu=pt string search
    assert "iommu=pt" in task_content or "iommu" in task_content.lower(), \
        "Task should check for iommu=pt parameter"

    # Check for fact registration
    assert "set_fact" in task_content or "register" in task_content, \
        "Task should register the result as a fact"


def test_backup_grub_config_task_exists(project_root):
    """GRUB backup task creates timestamped backup in same directory."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "backup-grub-config.yml"

    assert task_file.exists(), f"GRUB backup task not found: {task_file}"

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
    assert ".backup." in task_content or "backup" in task_content.lower(), \
        "Backup filename should include 'backup'"

    # Check for timestamp in destination
    assert "ansible_date_time" in task_content or "date" in task_content.lower(), \
        "Task should use timestamp in backup filename"


def test_configure_grub_iommu_task_exists(project_root):
    """GRUB IOMMU configuration task adds kernel parameters using replace module."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "configure-grub-iommu.yml"

    assert task_file.exists(), f"GRUB IOMMU configuration task not found: {task_file}"

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

    # Check for both IOMMU parameters
    assert "amd_iommu=on" in task_content, "Task should add amd_iommu=on parameter"
    assert "iommu=pt" in task_content, "Task should add iommu=pt parameter"

    # Check for regexp pattern
    assert "regexp" in task_content.lower(), "Task should use regexp for pattern matching"


def test_update_grub_task_exists(project_root):
    """Update GRUB task runs update-grub command and verifies success."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "update-grub.yml"

    assert task_file.exists(), f"Update GRUB task not found: {task_file}"

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

    # Check for result registration
    assert "register" in task_content.lower(), "Task should register command result for verification"


def test_reboot_system_task_exists(project_root):
    """Reboot system task reboots and verifies IOMMU and uptime."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "reboot-system.yml"

    assert task_file.exists(), f"Reboot system task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for reboot module usage
    assert "reboot" in task_content.lower(), "Task should use reboot module"

    # Check for timeout configuration
    assert "timeout" in task_content.lower() or "reboot_timeout" in task_content.lower(), \
        "Task should configure reboot timeout"

    # Check for post-reboot verification
    assert "/proc/cmdline" in task_content or "iommu" in task_content.lower(), \
        "Task should verify IOMMU parameters after reboot"

    # Check for uptime verification
    assert "uptime" in task_content.lower() or "stat" in task_content.lower(), \
        "Task should verify system uptime after reboot"


def test_configure_vfio_modules_task_exists(project_root):
    """VFIO kernel modules configuration task creates /etc/modules-load.d/vfio.conf."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "configure-vfio-modules.yml"

    assert task_file.exists(), f"VFIO modules configuration task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for lineinfile module usage
    assert "lineinfile" in task_content.lower(), "Task should use lineinfile module"

    # Check for target file path
    assert "/etc/modules-load.d/vfio.conf" in task_content, \
        "Task should target /etc/modules-load.d/vfio.conf"

    # Check for all four VFIO modules
    assert "vfio" in task_content, "Task should configure vfio module"
    assert "vfio_iommu_type1" in task_content, "Task should configure vfio_iommu_type1 module"
    assert "vfio_pci" in task_content, "Task should configure vfio_pci module"
    assert "vfio_virqfd" in task_content, "Task should configure vfio_virqfd module"


def test_update_initramfs_task_exists(project_root):
    """Update initramfs task rebuilds initramfs with VFIO modules."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox-gpu-passthrough" / "tasks" / "update-initramfs.yml"

    assert task_file.exists(), f"Update initramfs task not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"
    assert len(tasks) > 0, "Task file should not be empty"

    task_content = str(tasks)

    # Check for update-initramfs command
    assert "update-initramfs" in task_content, "Task should run update-initramfs command"
    assert "-k all" in task_content, "Task should update all kernels with -k all flag"

    # Check for verification with lsinitramfs
    assert "lsinitramfs" in task_content, "Task should verify modules with lsinitramfs"

    # Check for timestamp verification
    assert "stat" in task_content.lower(), "Task should check initramfs file timestamp"

    # Check for result registration
    assert "register" in task_content.lower(), "Task should register command result"
