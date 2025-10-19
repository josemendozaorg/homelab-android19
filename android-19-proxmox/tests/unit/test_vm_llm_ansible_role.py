"""Unit tests for vm-llm-aimachine Ansible role structure."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def role_dir(project_root):
    """vm-llm-aimachine role directory."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine"


def test_vm_llm_role_directory_exists(role_dir):
    """vm-llm-aimachine role directory should exist."""
    assert role_dir.exists(), "vm-llm-aimachine role directory not found"
    assert role_dir.is_dir(), "vm-llm-aimachine should be a directory"


def test_vm_llm_defaults_file_exists(role_dir):
    """Role should have defaults/main.yml file."""
    defaults_file = role_dir / "defaults" / "main.yml"
    assert defaults_file.exists(), "defaults/main.yml not found"


def test_vm_llm_defaults_valid_yaml(role_dir):
    """defaults/main.yml should be valid YAML."""
    defaults_file = role_dir / "defaults" / "main.yml"
    with open(defaults_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "defaults/main.yml should not be empty"


def test_vm_llm_tasks_main_exists(role_dir):
    """Role should have tasks/main.yml file."""
    tasks_file = role_dir / "tasks" / "main.yml"
    assert tasks_file.exists(), "tasks/main.yml not found"


def test_vm_llm_tasks_main_valid_yaml(role_dir):
    """tasks/main.yml should be valid YAML."""
    tasks_file = role_dir / "tasks" / "main.yml"
    with open(tasks_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "tasks/main.yml should not be empty"
    assert isinstance(data, list), "tasks/main.yml should contain a list of tasks"


def test_vm_llm_nvidia_drivers_task_file_exists(role_dir):
    """Role should have tasks/nvidia-drivers.yml for driver installation."""
    nvidia_task = role_dir / "tasks" / "nvidia-drivers.yml"
    assert nvidia_task.exists(), "tasks/nvidia-drivers.yml not found"


def test_vm_llm_vllm_install_task_file_exists(role_dir):
    """Role should have tasks/vllm-install.yml for vLLM installation."""
    vllm_task = role_dir / "tasks" / "vllm-install.yml"
    assert vllm_task.exists(), "tasks/vllm-install.yml not found"


def test_vm_llm_ollama_install_task_file_exists(role_dir):
    """Role should have tasks/ollama-install.yml for Ollama installation."""
    ollama_task = role_dir / "tasks" / "ollama-install.yml"
    assert ollama_task.exists(), "tasks/ollama-install.yml not found"


def test_vm_llm_defaults_references_catalog(role_dir):
    """defaults/main.yml should reference catalog as source of truth."""
    defaults_file = role_dir / "defaults" / "main.yml"
    content = defaults_file.read_text()
    assert "catalog" in content.lower() or "infrastructure-catalog.yml" in content, \
           "defaults/main.yml should reference catalog as source of truth"


def test_vm_llm_defaults_has_required_variables(role_dir):
    """defaults/main.yml should define required configuration variables."""
    defaults_file = role_dir / "defaults" / "main.yml"
    with open(defaults_file, 'r') as f:
        data = yaml.safe_load(f)

    # Should have configuration for NVIDIA drivers, vLLM, and Ollama
    # At minimum, should have some configuration structure
    assert data is not None, "defaults should have configuration"
    assert isinstance(data, dict), "defaults should be a dictionary"


def test_gpu_passthrough_task_file_exists(role_dir):
    """Role should have tasks/gpu-passthrough.yml for GPU configuration."""
    gpu_task = role_dir / "tasks" / "gpu-passthrough.yml"
    assert gpu_task.exists(), "tasks/gpu-passthrough.yml not found"


def test_gpu_passthrough_should_restart_vm_when_gpu_configured(role_dir):
    """GPU passthrough task should restart VM (stop/start) when GPU is newly configured."""
    gpu_task_file = role_dir / "tasks" / "gpu-passthrough.yml"
    with open(gpu_task_file, 'r') as f:
        tasks = yaml.safe_load(f)

    assert tasks is not None, "gpu-passthrough.yml should not be empty"
    assert isinstance(tasks, list), "gpu-passthrough.yml should contain a list of tasks"

    # Find stop VM task
    stop_task = None
    start_task = None
    for task in tasks:
        if isinstance(task, dict) and 'name' in task:
            if 'stop' in task['name'].lower() and 'vm' in task['name'].lower():
                stop_task = task
            if 'start' in task['name'].lower() and 'vm' in task['name'].lower():
                start_task = task

    assert stop_task is not None, "Should have task to stop VM after GPU configuration"
    assert start_task is not None, "Should have task to start VM after GPU configuration"

    # Verify stop task has correct condition (only when GPU was just configured)
    assert 'when' in stop_task, "Stop VM task should be conditional"
    when_condition = stop_task['when']
    # Check if condition includes gpu_config.changed
    if isinstance(when_condition, list):
        condition_str = ' '.join([str(c) for c in when_condition])
    else:
        condition_str = str(when_condition)

    assert 'gpu_config' in condition_str and 'changed' in condition_str, \
        "Stop VM task should only run when gpu_config.changed"

    # Verify start task has correct condition
    assert 'when' in start_task, "Start VM task should be conditional"

    # Verify tasks delegate to Proxmox host
    assert 'delegate_to' in stop_task, "Stop VM task should delegate to Proxmox host"
    assert 'delegate_to' in start_task, "Start VM task should delegate to Proxmox host"


def test_gpu_passthrough_should_wait_for_vm_after_restart(role_dir):
    """GPU passthrough should wait for VM to boot after restart."""
    gpu_task_file = role_dir / "tasks" / "gpu-passthrough.yml"
    with open(gpu_task_file, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find wait task (after start task)
    has_wait_task = False
    for task in tasks:
        if isinstance(task, dict) and 'name' in task:
            if 'wait' in task['name'].lower():
                has_wait_task = True
                # Should have timeout/delay for VM boot
                assert 'ansible.builtin.wait_for_connection' in str(task) or \
                       'ansible.builtin.wait_for' in str(task) or \
                       'ansible.builtin.pause' in str(task), \
                       "Wait task should use appropriate wait module"
                break

    assert has_wait_task, "Should wait for VM to boot after restart"
