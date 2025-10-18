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
    """Should install OpenRGB when detection shows it's not installed.

    Validates:
    - Task exists to download OpenRGB AppImage
    - Uses get_url module to download AppImage
    - Installs to /usr/local/bin/openrgb
    - Sets executable permissions
    - Conditional execution based on detection result (openrgb_installed.rc != 0)
    - Uses privilege escalation (become: true)

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    - Addresses: "Then the required RGB control software is automatically installed"
    - Ensures: Idempotent behavior (only install when needed)
    """
    # Arrange
    assert rgb_control_tasks is not None, "RGB control tasks should be loaded"
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find the OpenRGB download task
    download_task = None
    for task in rgb_control_tasks:
        if task and 'name' in task:
            task_name = task['name'].lower()
            if 'download' in task_name and 'openrgb' in task_name and 'appimage' in task_name:
                download_task = task
                break

    # Assert - Download task exists
    assert download_task is not None, \
        "Should have a task that downloads OpenRGB AppImage"

    # Assert - Uses get_url module
    assert 'get_url' in download_task, \
        "Download task should use 'get_url' module"

    # Assert - Downloads to correct location
    get_url_config = download_task['get_url']
    assert isinstance(get_url_config, dict), "get_url config should be a dict"
    assert 'dest' in get_url_config, "Should specify destination"
    assert get_url_config['dest'] == '/usr/local/bin/openrgb', \
        "Should install to /usr/local/bin/openrgb"

    # Assert - Sets executable permission
    assert 'mode' in get_url_config, "Should set file permissions"
    assert '755' in str(get_url_config['mode']), "Should be executable (755)"

    # Assert - Conditional on detection result
    assert 'when' in download_task, \
        "Installation should be conditional on detection result"
    when_condition = str(download_task['when'])
    assert 'openrgb_installed' in when_condition, \
        "Condition should reference openrgb_installed detection result"
    assert 'rc' in when_condition and '!=0' in when_condition.replace(' ', ''), \
        "Should only install when detection failed (rc != 0)"

    # Assert - Uses privilege escalation
    assert 'become' in download_task, \
        "Installation should use privilege escalation"
    assert download_task['become'] == True or download_task['become'] == 'yes', \
        "Should set become: true for root privileges"


def test_should_create_installation_directory_before_download(rgb_control_tasks):
    """Should create installation directory before downloading AppImage.

    Validates:
    - Task exists to create /usr/local/bin directory
    - Uses file module
    - Conditional execution based on detection result
    - Uses privilege escalation
    - Appears before download task

    Supporting BDD Scenario: First-time Setup and Turn Lights Off
    """
    # Arrange
    assert isinstance(rgb_control_tasks, list), "Tasks should be a list"

    # Act - Find directory creation and download tasks
    dir_task = None
    dir_index = None
    download_index = None

    for i, task in enumerate(rgb_control_tasks):
        if task and 'name' in task:
            task_name = task['name'].lower()
            # Directory creation task
            if dir_task is None and 'create' in task_name and 'directory' in task_name and 'openrgb' in task_name:
                dir_task = task
                dir_index = i
            # Download task
            if download_index is None and 'download' in task_name and 'openrgb' in task_name and 'appimage' in task_name:
                download_index = i

    # Assert - Directory creation task exists
    assert dir_task is not None, \
        "Should have a task that creates OpenRGB installation directory"

    # Assert - Uses file module
    assert 'file' in dir_task, \
        "Directory creation task should use 'file' module"

    # Assert - Creates /usr/local/bin directory
    file_config = dir_task['file']
    if isinstance(file_config, dict):
        assert 'path' in file_config, "file task should specify path"
        assert file_config['path'] == '/usr/local/bin', \
            "Should create /usr/local/bin directory"
        assert 'state' in file_config, "file task should specify state"
        assert file_config['state'] == 'directory', \
            "Should set state to directory"

    # Assert - Conditional on detection result
    assert 'when' in dir_task, \
        "Directory creation should be conditional on detection result"
    when_condition = str(dir_task['when'])
    assert 'openrgb_installed' in when_condition, \
        "Condition should reference openrgb_installed detection result"

    # Assert - Uses privilege escalation
    assert 'become' in dir_task, \
        "Directory creation should use privilege escalation"
    assert dir_task['become'] == True or dir_task['become'] == 'yes', \
        "Should set become: true for root privileges"

    # Assert - Directory creation occurs before download
    if dir_index is not None and download_index is not None:
        assert dir_index < download_index, \
            "Directory creation should occur before AppImage download"


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
