"""Unit tests for OpenRGB installation in RGB control role.

These tests validate that the Ansible role automatically installs OpenRGB
when it is not already present (idempotent installation behavior).
"""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def rgb_control_tasks(project_root):
    """Load RGB control task file."""
    tasks_file = project_root / "configuration-by-ansible" / "host-proxmox" / "tasks" / "rgb-control.yml"
    with open(tasks_file) as f:
        return yaml.safe_load(f)


def test_should_install_openrgb_automatically_when_not_already_present(rgb_control_tasks):
    """Should install OpenRGB package when detection shows it's not installed.

    Validates:
    - Task exists to install openrgb package
    - Uses apt module for package installation
    - Conditional execution based on detection result (openrgb_installed.rc != 0)
    - Updates apt cache before installation
    - Uses privilege escalation (become: true)

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    - Addresses: "Then the required RGB control software is automatically installed"
    - Ensures: Idempotent behavior (only install when needed)
    """
    # Arrange
    assert rgb_control_tasks is not None, "RGB control tasks should be loaded"
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find the OpenRGB installation task
    install_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            task_name = task['name'].lower()
            if 'install' in task_name and 'openrgb' in task_name and 'detect' not in task_name:
                install_task = task
                break

    # Assert - Installation task exists
    assert install_task is not None, \
        "Should have a task that installs OpenRGB package"

    # Assert - Uses apt module
    assert 'apt' in install_task, \
        "Installation task should use 'apt' module for package management"

    # Assert - Installs openrgb package
    apt_config = install_task['apt']
    if isinstance(apt_config, dict):
        assert 'name' in apt_config, "apt task should specify package name"
        assert apt_config['name'] == 'openrgb', \
            "Should install 'openrgb' package"
    elif isinstance(apt_config, str):
        assert 'openrgb' in apt_config, "Should install openrgb package"

    # Assert - Conditional on detection result
    assert 'when' in install_task, \
        "Installation should be conditional on detection result"
    when_condition = str(install_task['when'])
    assert 'openrgb_installed' in when_condition, \
        "Condition should reference openrgb_installed detection result"
    assert 'rc' in when_condition and '!=0' in when_condition.replace(' ', ''), \
        "Should only install when detection failed (rc != 0)"

    # Assert - Uses privilege escalation
    assert 'become' in install_task, \
        "Installation should use privilege escalation"
    assert install_task['become'] == True or install_task['become'] == 'yes', \
        "Should set become: true for root privileges"

    # Assert - Updates cache
    if isinstance(apt_config, dict):
        assert 'update_cache' in apt_config, \
            "Should update apt cache before installation"
        assert apt_config['update_cache'] == True or apt_config['update_cache'] == 'yes', \
            "Should set update_cache: yes"


def test_should_add_openrgb_ppa_before_installation(rgb_control_tasks):
    """Should add OpenRGB PPA repository before installing package.

    Validates:
    - Task exists to add OpenRGB PPA
    - Uses apt_repository module
    - Conditional execution based on detection result
    - Uses privilege escalation
    - Appears before installation task

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find PPA and installation tasks
    ppa_task = None
    ppa_index = None
    install_index = None

    for i, task in enumerate(rgb_control_tasks):
        if task and 'name' in task:
            task_name = task['name'].lower()
            # PPA task
            if ppa_task is None and 'ppa' in task_name and 'openrgb' in task_name:
                ppa_task = task
                ppa_index = i
            # Installation task
            if install_index is None and 'install' in task_name and 'openrgb' in task_name and 'detect' not in task_name:
                install_index = i

    # Assert - PPA task exists
    assert ppa_task is not None, \
        "Should have a task that adds OpenRGB PPA repository"

    # Assert - Uses apt_repository module
    assert 'apt_repository' in ppa_task, \
        "PPA task should use 'apt_repository' module"

    # Assert - Specifies PPA repository
    apt_repo_config = ppa_task['apt_repository']
    if isinstance(apt_repo_config, dict):
        assert 'repo' in apt_repo_config, "apt_repository should specify repo"
        repo = apt_repo_config['repo']
        assert 'ppa:' in repo.lower() and 'openrgb' in repo.lower(), \
            "Should add OpenRGB PPA repository"

    # Assert - Conditional on detection result
    assert 'when' in ppa_task, \
        "PPA addition should be conditional on detection result"
    when_condition = str(ppa_task['when'])
    assert 'openrgb_installed' in when_condition, \
        "Condition should reference openrgb_installed detection result"

    # Assert - Uses privilege escalation
    assert 'become' in ppa_task, \
        "PPA addition should use privilege escalation"
    assert ppa_task['become'] == True or ppa_task['become'] == 'yes', \
        "Should set become: true for root privileges"

    # Assert - PPA task appears before installation
    if ppa_index is not None and install_index is not None:
        assert ppa_index < install_index, \
            "PPA addition should occur before package installation"


def test_installation_tasks_should_run_after_detection(rgb_control_tasks):
    """Installation tasks should run after detection task.

    Validates:
    - Detection task runs first
    - PPA addition runs after detection
    - Package installation runs after PPA addition
    - Proper task ordering ensures dependencies are met

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find task positions
    detection_index = None
    ppa_index = None
    install_index = None

    for i, task in enumerate(rgb_control_tasks):
        if task and 'name' in task:
            task_name = task['name'].lower()
            if detection_index is None and 'detect' in task_name and 'openrgb' in task_name:
                if 'command' in task or 'shell' in task:
                    detection_index = i
            if ppa_index is None and 'ppa' in task_name and 'openrgb' in task_name:
                ppa_index = i
            if install_index is None and 'install' in task_name and 'openrgb' in task_name and 'detect' not in task_name:
                install_index = i

    # Assert - Proper ordering
    assert detection_index is not None, "Detection task should exist"

    if ppa_index is not None:
        assert detection_index < ppa_index, \
            "Detection should run before PPA addition"

    if install_index is not None:
        assert detection_index < install_index, \
            "Detection should run before installation"

        if ppa_index is not None:
            assert ppa_index < install_index, \
                "PPA addition should run before installation"
