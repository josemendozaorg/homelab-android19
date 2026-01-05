"""Unit tests for vLLM installation tasks in vm-llm-aimachine role."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def vllm_tasks_file(project_root):
    """vLLM installation tasks file."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine" / "tasks" / "vllm-install.yml"


def test_vllm_task_file_exists(vllm_tasks_file):
    """vllm-install.yml should exist."""
    assert vllm_tasks_file.exists(), "vllm-install.yml not found"


def test_vllm_task_valid_yaml(vllm_tasks_file):
    """vllm-install.yml should be valid YAML."""
    with open(vllm_tasks_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "vllm-install.yml should not be empty"
    assert isinstance(data, list), "vllm-install.yml should contain a list of tasks"


def test_vllm_has_python_installation(vllm_tasks_file):
    """Should install Python 3.11+ and pip."""
    content = vllm_tasks_file.read_text()
    assert 'python' in content.lower() and 'pip' in content.lower(), \
           "Should install Python and pip"


def test_vllm_has_vllm_installation(vllm_tasks_file):
    """Should install vLLM via pip."""
    content = vllm_tasks_file.read_text()
    assert 'vllm' in content.lower() and 'pip' in content.lower(), \
           "Should install vLLM via pip"


def test_vllm_has_service_user_creation(vllm_tasks_file):
    """Should create vLLM service user."""
    content = vllm_tasks_file.read_text()
    assert 'user' in content.lower() and ('vllm' in content or 'ansible.builtin.user' in content), \
           "Should create vLLM service user"


def test_vllm_has_model_directory_creation(vllm_tasks_file):
    """Should create model directory."""
    content = vllm_tasks_file.read_text()
    assert 'file' in content.lower() or 'directory' in content.lower(), \
           "Should create model directory"
    assert '/opt/models' in content or 'vllm_model_dir' in content, \
           "Should reference model directory path"


def test_vllm_has_systemd_service(vllm_tasks_file):
    """Should create systemd service for vLLM."""
    content = vllm_tasks_file.read_text()
    assert 'systemd' in content.lower() or 'service' in content.lower(), \
           "Should create systemd service"


def test_vllm_service_binds_to_vm_ip(vllm_tasks_file):
    """Should configure vLLM to bind to VM IP address."""
    content = vllm_tasks_file.read_text()
    assert 'vllm_host' in content or '192.168.0.140' in content or 'vm_config.ip' in content, \
           "Should bind to VM IP address"
    assert 'vllm_port' in content or '8000' in content, \
           "Should configure port 8000"


def test_vllm_service_auto_start_enabled(vllm_tasks_file):
    """Should control vLLM service auto-start with vllm_service_enabled variable."""
    content = vllm_tasks_file.read_text()
    # Service state should be controlled by vllm_service_enabled variable
    assert 'enabled: "{{ vllm_service_enabled }}"' in content, \
           "Should use vllm_service_enabled variable for service state"
    assert 'state: "{{ \'started\' if vllm_service_enabled else \'stopped\' }}"' in content, \
           "Should conditionally start/stop service based on vllm_service_enabled"



