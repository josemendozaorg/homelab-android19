"""Unit tests for Ollama model management tasks in vm-llm-aimachine role."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def ollama_models_file(project_root):
    """Ollama model management tasks file."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine" / "tasks" / "ollama-models.yml"


@pytest.fixture
def defaults_file(project_root):
    """vm-llm-aimachine defaults file."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine" / "defaults" / "main.yml"


@pytest.fixture
def main_tasks_file(project_root):
    """vm-llm-aimachine main tasks file."""
    return project_root / "configuration-by-ansible" / "vm-llm-aimachine" / "tasks" / "main.yml"


# ============================================================================
# Tests for ollama-models.yml task file
# ============================================================================

def test_ollama_models_task_file_exists(ollama_models_file):
    """ollama-models.yml should exist for model management."""
    assert ollama_models_file.exists(), "ollama-models.yml not found"


def test_ollama_models_valid_yaml(ollama_models_file):
    """ollama-models.yml should be valid YAML."""
    with open(ollama_models_file, 'r') as f:
        data = yaml.safe_load(f)
    assert data is not None, "ollama-models.yml should not be empty"
    assert isinstance(data, list), "ollama-models.yml should contain a list of tasks"


def test_ollama_models_has_service_wait(ollama_models_file):
    """Should wait for Ollama service to be ready before pulling models."""
    content = ollama_models_file.read_text()
    # Should have some form of wait or health check
    assert 'wait' in content.lower() or 'uri' in content.lower() or 'until' in content.lower(), \
           "Should wait for Ollama service before pulling models"


def test_ollama_models_has_model_check(ollama_models_file):
    """Should check if model already exists before pulling."""
    content = ollama_models_file.read_text()
    assert 'ollama list' in content or 'ollama_list' in content.lower(), \
           "Should check existing models with 'ollama list'"


def test_ollama_models_has_model_pull(ollama_models_file):
    """Should pull models using 'ollama pull' command."""
    content = ollama_models_file.read_text()
    assert 'ollama pull' in content or 'ollama_pull' in content.lower(), \
           "Should pull models with 'ollama pull'"


def test_ollama_models_pulls_deepseek_r1(ollama_models_file):
    """Should pull DeepSeek-R1:14B model by default."""
    content = ollama_models_file.read_text()
    # Should reference the model configuration variable or directly the model name
    assert 'ollama_models_to_pull' in content or 'deepseek' in content.lower(), \
           "Should reference DeepSeek-R1 model or models configuration"


def test_ollama_models_has_verification(ollama_models_file):
    """Should verify model was pulled successfully."""
    content = ollama_models_file.read_text()
    assert 'verify' in content.lower() or 'assert' in content.lower() or 'debug' in content.lower(), \
           "Should verify model pull was successful"


def test_ollama_models_uses_loop_for_multiple_models(ollama_models_file):
    """Should support pulling multiple models via loop."""
    content = ollama_models_file.read_text()
    assert 'loop' in content.lower() or 'with_items' in content.lower() or 'ollama_models_to_pull' in content, \
           "Should support multiple models configuration"


# ============================================================================
# Tests for defaults/main.yml model configuration
# ============================================================================

def test_defaults_has_models_to_pull_config(defaults_file):
    """defaults/main.yml should have ollama_models_to_pull configuration."""
    with open(defaults_file, 'r') as f:
        data = yaml.safe_load(f)
    assert 'ollama_models_to_pull' in data, \
           "Should have ollama_models_to_pull configuration"
    assert isinstance(data['ollama_models_to_pull'], list), \
           "ollama_models_to_pull should be a list"


def test_defaults_has_deepseek_r1_model(defaults_file):
    """defaults/main.yml should include DeepSeek-R1:14B in models list."""
    with open(defaults_file, 'r') as f:
        data = yaml.safe_load(f)
    models = data.get('ollama_models_to_pull', [])
    assert any('deepseek-r1' in str(m).lower() for m in models), \
           "Should include deepseek-r1:14b in models list"


def test_defaults_has_pull_on_deploy_flag(defaults_file):
    """defaults/main.yml should have ollama_pull_models_on_deploy flag."""
    with open(defaults_file, 'r') as f:
        data = yaml.safe_load(f)
    assert 'ollama_pull_models_on_deploy' in data, \
           "Should have ollama_pull_models_on_deploy flag"
    assert data['ollama_pull_models_on_deploy'] is True, \
           "ollama_pull_models_on_deploy should be True by default"


def test_defaults_has_model_pull_timeout(defaults_file):
    """defaults/main.yml should have ollama_model_pull_timeout for large downloads."""
    with open(defaults_file, 'r') as f:
        data = yaml.safe_load(f)
    assert 'ollama_model_pull_timeout' in data, \
           "Should have ollama_model_pull_timeout configuration"
    assert data['ollama_model_pull_timeout'] >= 1800, \
           "Model pull timeout should be at least 30 minutes (1800 seconds)"


# ============================================================================
# Tests for main.yml integration
# ============================================================================

def test_main_tasks_includes_ollama_models(main_tasks_file):
    """main.yml should include ollama-models.yml tasks."""
    content = main_tasks_file.read_text()
    assert 'ollama-models.yml' in content, \
           "main.yml should include ollama-models.yml"


def test_main_tasks_has_conditional_model_pull(main_tasks_file):
    """main.yml should conditionally include model pull based on flag."""
    content = main_tasks_file.read_text()
    assert 'ollama_pull_models_on_deploy' in content, \
           "Should check ollama_pull_models_on_deploy flag"


def test_main_tasks_has_models_tag(main_tasks_file):
    """main.yml should tag model tasks for selective execution."""
    content = main_tasks_file.read_text()
    # Check for tags near the ollama-models include
    assert 'models' in content.lower() and 'tags' in content.lower(), \
           "Should have 'models' tag for selective execution"
