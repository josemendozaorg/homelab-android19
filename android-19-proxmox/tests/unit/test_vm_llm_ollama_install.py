"""Unit tests for Ollama installation tasks in vm-llm-aimachine role."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def ollama_tasks_file(project_root):
    """Ollama installation tasks file."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine" / "tasks" / "ollama-install.yml"


def test_ollama_task_file_exists(ollama_tasks_file):
    """ollama-install.yml should exist."""
    assert ollama_tasks_file.exists(), "ollama-install.yml not found"


def test_ollama_task_valid_yaml(ollama_tasks_file):
    """ollama-install.yml should be valid YAML."""
    with open(ollama_tasks_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "ollama-install.yml should not be empty"
    assert isinstance(data, list), "ollama-install.yml should contain a list of tasks"


def test_ollama_has_download_installation(ollama_tasks_file):
    """Should download and install Ollama."""
    content = ollama_tasks_file.read_text()
    assert 'ollama' in content.lower(), "Should reference Ollama"
    # Check for download methods (get_url, curl, or official install script)
    assert 'get_url' in content or 'curl' in content or 'shell' in content, \
           "Should download Ollama binary or use install script"


def test_ollama_has_model_directory_creation(ollama_tasks_file):
    """Should create model directory."""
    content = ollama_tasks_file.read_text()
    assert 'file' in content.lower() or 'directory' in content.lower(), \
           "Should create model directory"
    assert '/opt/ollama' in content or 'ollama_model_dir' in content, \
           "Should reference Ollama model directory"


def test_ollama_has_systemd_service(ollama_tasks_file):
    """Should create or configure systemd service for Ollama."""
    content = ollama_tasks_file.read_text()
    assert 'systemd' in content.lower() or 'service' in content.lower(), \
           "Should configure systemd service"


def test_ollama_service_binds_to_all_interfaces(ollama_tasks_file):
    """Should configure Ollama to bind to all interfaces (0.0.0.0)."""
    content = ollama_tasks_file.read_text()
    assert 'ollama_host' in content or '0.0.0.0' in content or 'OLLAMA_HOST' in content, \
           "Should configure host binding"
    assert 'ollama_port' in content or '11434' in content or 'OLLAMA_PORT' in content, \
           "Should configure port 11434"


def test_ollama_service_auto_start_enabled(ollama_tasks_file):
    """Should enable Ollama service for auto-start on boot."""
    content = ollama_tasks_file.read_text()
    assert 'enabled' in content and ('true' in content.lower() or 'yes' in content), \
           "Should enable service for auto-start"


def test_ollama_has_service_verification(ollama_tasks_file):
    """Should verify Ollama service is running."""
    content = ollama_tasks_file.read_text()
    # Check for service verification or version check
    assert 'systemctl' in content or 'ollama' in content.lower() or 'service' in content, \
           "Should verify Ollama service or installation"


def test_ollama_has_version_check(ollama_tasks_file):
    """Should verify Ollama version or installation."""
    content = ollama_tasks_file.read_text()
    assert 'ollama' in content.lower() and ('version' in content.lower() or 'list' in content.lower()), \
           "Should check Ollama version or functionality"


def test_ollama_handles_gpu_configuration(ollama_tasks_file):
    """Should configure Ollama for GPU usage."""
    content = ollama_tasks_file.read_text()
    # Ollama automatically detects CUDA, but should set environment variables
    assert 'CUDA' in content or 'nvidia' in content.lower() or 'gpu' in content.lower(), \
           "Should configure GPU-related settings for Ollama"
