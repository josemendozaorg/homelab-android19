"""
Tests for PCIe ASPM GRUB configuration tasks.

This test suite validates the host-proxmox role's PCIe ASPM configuration
tasks for disabling Active State Power Management to prevent network card
disconnections.
"""

import pytest
import yaml
import subprocess
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


def test_update_grub_error_handling(project_root):
    """Update GRUB task has proper error handling for update-grub failures."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm-update.yml"

    assert task_file.exists(), f"Update GRUB task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Task file should contain a list of tasks"

    # Find the update-grub task
    update_grub_task = None
    for task in tasks:
        # Check for various command module formats
        has_command = (
            "ansible.builtin.command" in task or
            "command" in task or
            "ansible.builtin.shell" in task or
            "shell" in task
        )
        if has_command:
            task_str = str(task)
            if "update-grub" in task_str.lower() or "grub-mkconfig" in task_str.lower():
                update_grub_task = task
                break

    assert update_grub_task is not None, "Could not find update-grub command task"

    # Check for error handling - should have either failed_when or check mode
    task_keys = update_grub_task.keys()
    has_error_handling = (
        "failed_when" in task_keys or
        "ignore_errors" in task_keys or
        "check_mode" in task_keys
    )

    assert has_error_handling, \
        "Update GRUB task should have error handling (failed_when, ignore_errors, or check_mode)"

    # Check for result registration to capture errors
    assert "register" in task_keys, \
        "Update GRUB task should register result for error handling"

    # Look for error message display task (assert or fail task)
    task_content = str(tasks)
    has_error_message = (
        "assert" in task_content.lower() or
        "fail" in task_content.lower() or
        "rc" in task_content.lower()  # Return code checking
    )

    assert has_error_message, \
        "Task file should include error message handling (assert, fail, or rc checking)"


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


def test_grub_pcie_aspm_orchestrator_exists(project_root):
    """PCIe ASPM orchestrator task file exists and includes subtasks in correct order."""
    task_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm.yml"

    assert task_file.exists(), f"Orchestrator task file not found: {task_file}"

    with open(task_file) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Orchestrator file should contain a list of tasks"
    assert len(tasks) >= 4, "Orchestrator should include at least 4 subtasks (check, backup, configure, update)"

    task_content = str(tasks)

    # Check that all required subtasks are included
    assert "grub-pcie-aspm-check.yml" in task_content, "Orchestrator should include check task"
    assert "grub-pcie-aspm-backup.yml" in task_content, "Orchestrator should include backup task"
    assert "grub-pcie-aspm-configure.yml" in task_content, "Orchestrator should include configure task"
    assert "grub-pcie-aspm-update.yml" in task_content, "Orchestrator should include update task"

    # Check for include_tasks usage
    assert "include_tasks" in task_content, "Orchestrator should use include_tasks"


def test_main_yml_includes_pcie_aspm_configuration(project_root):
    """host-proxmox main.yml includes PCIe ASPM GRUB configuration with correct tags."""
    main_yml = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "main.yml"

    assert main_yml.exists(), f"Main task file not found: {main_yml}"

    with open(main_yml) as f:
        tasks = yaml.safe_load(f)

    assert isinstance(tasks, list), "Main.yml should contain a list of tasks"

    # Find the PCIe ASPM configuration task
    pcie_aspm_task = None
    for task in tasks:
        if "include_tasks" in task and "grub-pcie-aspm.yml" in str(task.get("include_tasks", "")):
            pcie_aspm_task = task
            break

    assert pcie_aspm_task is not None, "Main.yml should include grub-pcie-aspm.yml"

    # Check tags
    tags = pcie_aspm_task.get("tags", [])
    assert "proxmox" in tags, "PCIe ASPM task should have 'proxmox' tag"
    assert "grub" in tags, "PCIe ASPM task should have 'grub' tag"
    assert "pcie-aspm" in tags, "PCIe ASPM task should have 'pcie-aspm' tag"

    # Check task name
    task_name = pcie_aspm_task.get("name", "")
    assert "pcie" in task_name.lower() or "aspm" in task_name.lower(), \
        "Task should have descriptive name mentioning PCIe or ASPM"


def test_pcie_aspm_role_integration_ansible_syntax(project_root):
    """Integration test: Validate host-proxmox role with PCIe ASPM can be loaded by Ansible."""
    # Create a minimal test playbook that uses the host-proxmox role
    test_playbook_content = """---
- name: Test host-proxmox role with PCIe ASPM integration
  hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - name: Include host-proxmox main tasks
      include_tasks: ../configuration-by-ansible/host-proxmox/tasks/main.yml
"""

    test_playbook_path = project_root / "test_pcie_aspm_integration.yml"

    # Write test playbook
    with open(test_playbook_path, 'w') as f:
        f.write(test_playbook_content)

    try:
        # Check if ansible-playbook is available
        result = subprocess.run(
            ["which", "ansible-playbook"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # ansible-playbook is available, run syntax check
            syntax_result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(test_playbook_path)],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )

            # Clean up test playbook
            test_playbook_path.unlink()

            assert syntax_result.returncode == 0, \
                f"Ansible syntax check failed:\nSTDOUT: {syntax_result.stdout}\nSTDERR: {syntax_result.stderr}"
        else:
            # ansible-playbook not available, skip with warning
            test_playbook_path.unlink()
            pytest.skip("ansible-playbook not installed, skipping Ansible syntax validation")

    except Exception as e:
        # Clean up on any error
        if test_playbook_path.exists():
            test_playbook_path.unlink()
        raise e


def test_pcie_aspm_include_tasks_are_resolvable(project_root):
    """Integration test: Verify all include_tasks references in orchestrator are resolvable."""
    orchestrator = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "grub-pcie-aspm.yml"
    tasks_dir = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks"

    assert orchestrator.exists(), "Orchestrator file must exist"

    with open(orchestrator) as f:
        tasks = yaml.safe_load(f)

    # Extract all include_tasks references
    for task in tasks:
        if "include_tasks" in task:
            included_file = task["include_tasks"]
            included_path = tasks_dir / included_file

            assert included_path.exists(), \
                f"Included task file not found: {included_file} (expected at {included_path})"

            # Verify the included file is valid YAML
            with open(included_path) as included_f:
                included_tasks = yaml.safe_load(included_f)
                assert included_tasks is not None, f"Included file {included_file} has invalid YAML"
                assert isinstance(included_tasks, list), f"Included file {included_file} should contain a list of tasks"
