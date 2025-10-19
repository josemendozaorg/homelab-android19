"""Unit tests for RAM LED control role structure within host-proxmox role.

These tests validate that the Ansible role provides proper structure for
independent RAM LED light control functionality.
"""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def host_proxmox_role_path(project_root):
    """Return path to host-proxmox role directory."""
    return project_root / "configuration-by-ansible" / "host-proxmox"


def test_should_provide_ram_led_control_task_structure_for_host_proxmox_role(host_proxmox_role_path):
    """RAM LED control task file should exist with valid structure for host-proxmox role.

    Validates:
    - tasks/ram-led-control.yml exists
    - File is valid YAML
    - File has basic structure (is a list)

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.1: Create Ansible tasks for RAM LED control off
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act & Assert - File exists
    assert ram_led_control_task_file.exists(), \
        f"RAM LED control task file should exist at {ram_led_control_task_file}"

    # Act & Assert - Valid YAML
    with open(ram_led_control_task_file) as f:
        content = yaml.safe_load(f)

    # Assert - Basic structure (should be a list for Ansible tasks)
    assert isinstance(content, list), \
        "RAM LED control task file should contain a list of tasks"


def test_ram_led_control_should_target_only_led4_channel(host_proxmox_role_path):
    """RAM LED control should target only led4 channel, not Arctic lights (led1-led3).

    Validates:
    - Commands target 'led4' only
    - No references to led1, led2, or led3
    - Uses liquidctl --match 'ASUS' pattern

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Ensures AC8: Turning RAM LEDs off does NOT affect Arctic lights
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Contains led4 references (RAM channel)
    assert 'led4' in content, \
        "RAM LED control should target led4 channel"

    # Assert - Does NOT contain Arctic light channel references
    # Check for led1, led2, led3 in command contexts (not in comments)
    task_commands = [task.get('command', '') for task in tasks if isinstance(task, dict)]
    all_commands = ' '.join(task_commands)

    assert 'led1' not in all_commands, \
        "RAM LED control should NOT target led1 (Arctic light channel)"
    assert 'led2' not in all_commands, \
        "RAM LED control should NOT target led2 (Arctic light channel)"
    assert 'led3' not in all_commands, \
        "RAM LED control should NOT target led3 (Arctic light channel)"

    # Assert - Uses liquidctl with ASUS matcher
    assert "liquidctl --match 'ASUS'" in content or 'liquidctl --match "ASUS"' in content, \
        "RAM LED control should use liquidctl with ASUS device matcher"


def test_ram_led_control_should_support_off_state(host_proxmox_role_path):
    """RAM LED control should support turning LEDs off.

    Validates:
    - Has task with 'color off' command
    - Task is conditional on ram_lights_state == "off"
    - Task has changed_when: false for idempotency

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.1: Create Ansible tasks for RAM LED control off
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Has 'color off' command
    assert 'color off' in content, \
        "RAM LED control should have command to turn LEDs off"

    # Assert - Has ram_lights_state conditional
    assert 'ram_lights_state' in content, \
        "RAM LED control should use ram_lights_state variable"

    # Assert - Has changed_when: false for idempotency
    assert 'changed_when: false' in content or 'changed_when:false' in content, \
        "RAM LED control tasks should be marked as unchanged for idempotency"


def test_should_define_ram_led_control_default_variables_in_host_proxmox_role(host_proxmox_role_path):
    """RAM LED control default variables should be defined in host-proxmox role.

    Validates:
    - defaults/main.yml contains ram_lights_enabled variable
    - defaults/main.yml contains ram_lights_state variable
    - Variables have appropriate default values

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.2: Add variable handling for ram_lights_state in defaults
    """
    # Arrange
    defaults_file = host_proxmox_role_path / "defaults" / "main.yml"

    # Act
    assert defaults_file.exists(), "defaults/main.yml should exist"

    with open(defaults_file) as f:
        defaults = yaml.safe_load(f)

    # Assert - Required RAM LED variables are defined
    assert 'ram_lights_enabled' in defaults, \
        "ram_lights_enabled variable should be defined in defaults"

    assert 'ram_lights_state' in defaults, \
        "ram_lights_state variable should be defined in defaults"

    # Assert - Variables have sensible types/values
    assert isinstance(defaults['ram_lights_enabled'], bool), \
        "ram_lights_enabled should be a boolean"

    assert defaults['ram_lights_state'] in ['on', 'off'], \
        "ram_lights_state should be 'on' or 'off'"


def test_should_include_ram_led_control_tasks_in_host_proxmox_main_tasks(host_proxmox_role_path):
    """RAM LED control task file should be included in main task list.

    Validates:
    - tasks/main.yml includes ram-led-control.yml
    - Include is enabled (not commented out)
    - Include has proper conditional (ram_lights_enabled)

    This supports BDD Scenario 1: Turn RAM LEDs Off Independently
    Linked to Task 1.3: Include RAM LED control tasks in main playbook
    """
    # Arrange
    main_tasks_file = host_proxmox_role_path / "tasks" / "main.yml"

    # Act
    assert main_tasks_file.exists(), "tasks/main.yml should exist"

    with open(main_tasks_file) as f:
        content = f.read()

    # Assert - ram-led-control.yml is included
    assert 'ram-led-control.yml' in content, \
        "tasks/main.yml should include ram-led-control.yml task file"

    # Assert - Include is not commented out
    # Check that the line containing ram-led-control.yml doesn't start with #
    for line in content.split('\n'):
        if 'ram-led-control.yml' in line:
            stripped = line.strip()
            assert not stripped.startswith('#'), \
                "ram-led-control.yml include should not be commented out"
            break

    # Assert - Has proper conditional
    assert 'ram_lights_enabled' in content, \
        "RAM LED control include should check ram_lights_enabled variable"


def test_ram_led_control_should_support_on_state(host_proxmox_role_path):
    """RAM LED control should support turning LEDs on with rainbow effect.

    Validates:
    - Has task with 'color rainbow' command for led4
    - Task is conditional on ram_lights_state == "on"
    - Task has changed_when: false for idempotency

    This supports BDD Scenario 2: Turn RAM LEDs On Independently
    Linked to Task 2.1: Add Ansible task for RAM LED control on (rainbow)
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Has 'color rainbow' command for led4
    assert 'color rainbow' in content, \
        "RAM LED control should have command to turn LEDs on with rainbow effect"

    assert 'led4' in content, \
        "Rainbow command should target led4 channel (RAM)"

    # Assert - Has ram_lights_state == "on" conditional
    # Find the "on" task and verify it has proper conditional
    on_task_found = False
    for task in tasks:
        if isinstance(task, dict) and 'command' in task:
            cmd = task['command']
            if 'rainbow' in cmd and 'led4' in cmd:
                on_task_found = True
                assert 'when' in task, "Rainbow task should have conditional"
                when_clause = task['when']
                when_str = ' '.join(when_clause) if isinstance(when_clause, list) else when_clause
                assert 'ram_lights_state' in when_str and '"on"' in when_str, \
                    "Rainbow task should check ram_lights_state == 'on'"
                break

    assert on_task_found, "Should have task for turning RAM LEDs on with rainbow"


def test_should_provide_ram_led_systemd_service_template_for_led4_only(host_proxmox_role_path):
    """RAM LED systemd service template should exist and target led4 only.

    Validates:
    - templates/ram-led-control.service.j2 exists
    - Template targets led4 channel only
    - Template does NOT target led1, led2, or led3 (Arctic channels)
    - Template uses ram_lights_state variable
    - Template has valid systemd structure ([Unit], [Service], [Install])

    This supports BDD Scenario 3: RAM LED State Persists After Reboot
    Linked to Task 3.1: Create systemd service template for RAM LED control
    Ensures AC4: RAM LED state persists across system reboots
    """
    # Arrange
    service_template_file = host_proxmox_role_path / "templates" / "ram-led-control.service.j2"

    # Act & Assert - File exists
    assert service_template_file.exists(), \
        f"RAM LED systemd service template should exist at {service_template_file}"

    # Act - Read template content
    with open(service_template_file) as f:
        content = f.read()

    # Assert - Contains led4 references (RAM channel)
    assert 'led4' in content, \
        "RAM LED systemd service should target led4 channel"

    # Assert - Does NOT contain Arctic light channel references
    assert 'led1' not in content, \
        "RAM LED systemd service should NOT target led1 (Arctic light channel)"
    assert 'led2' not in content, \
        "RAM LED systemd service should NOT target led2 (Arctic light channel)"
    assert 'led3' not in content, \
        "RAM LED systemd service should NOT target led3 (Arctic light channel)"

    # Assert - Uses ram_lights_state variable
    assert 'ram_lights_state' in content, \
        "RAM LED systemd service should use ram_lights_state variable"

    # Assert - Valid systemd unit file structure
    assert '[Unit]' in content, \
        "Systemd service template should have [Unit] section"
    assert '[Service]' in content, \
        "Systemd service template should have [Service] section"
    assert '[Install]' in content, \
        "Systemd service template should have [Install] section"

    # Assert - Uses liquidctl with ASUS matcher
    assert "liquidctl --match 'ASUS'" in content or 'liquidctl --match "ASUS"' in content, \
        "RAM LED systemd service should use liquidctl with ASUS device matcher"

    # Assert - Systemd service type and persistence
    assert 'Type=oneshot' in content, \
        "RAM LED systemd service should be Type=oneshot for boot-time execution"
    assert 'RemainAfterExit=yes' in content, \
        "RAM LED systemd service should have RemainAfterExit=yes for state persistence"


def test_should_deploy_ram_led_systemd_service_via_ansible_tasks(host_proxmox_role_path):
    """RAM LED control tasks should deploy and enable systemd service.

    Validates:
    - Task deploys ram-led-control.service.j2 template to /etc/systemd/system/
    - Task reloads systemd daemon after template deployment
    - Task enables service for autostart on boot
    - Tasks follow RGB control pattern (no state: started for oneshot service)
    - Tasks have proper conditionals to skip during status checks

    This supports BDD Scenario 3: RAM LED State Persists After Reboot
    Linked to Task 3.2: Deploy RAM LED control systemd service
    Ensures AC4: RAM LED state persists across system reboots
    Ensures AC13: Both RGB and RAM services start automatically after reboot
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Template deployment task exists
    template_task = None
    for task in tasks:
        if isinstance(task, dict) and 'template' in task:
            if 'ram-led-control.service.j2' in str(task.get('template', {})):
                template_task = task
                break

    assert template_task is not None, \
        "Should have task to deploy ram-led-control.service.j2 template"

    assert template_task['template']['dest'] == '/etc/systemd/system/ram-led-control.service', \
        "Template should be deployed to /etc/systemd/system/ram-led-control.service"

    assert template_task['template']['mode'] == '0644', \
        "Template should have mode 0644"

    # Assert - Systemd daemon reload task exists
    daemon_reload_task = None
    for task in tasks:
        if isinstance(task, dict) and 'systemd' in task:
            if task.get('systemd', {}).get('daemon_reload'):
                daemon_reload_task = task
                break

    assert daemon_reload_task is not None, \
        "Should have task to reload systemd daemon"

    # Assert - Service enable task exists
    service_enable_task = None
    for task in tasks:
        if isinstance(task, dict) and 'systemd' in task:
            systemd_config = task.get('systemd', {})
            if (systemd_config.get('name') == 'ram-led-control.service' and
                systemd_config.get('enabled')):
                service_enable_task = task
                break

    assert service_enable_task is not None, \
        "Should have task to enable ram-led-control.service for autostart"

    assert service_enable_task['systemd']['enabled'] is True or service_enable_task['systemd']['enabled'] == 'yes', \
        "Service should be enabled for autostart"

    # Assert - Service should NOT have state: started (following RGB pattern)
    # Oneshot services don't need to be started - liquidctl commands already applied state
    assert 'state' not in service_enable_task['systemd'], \
        "Service enable task should NOT have 'state: started' (oneshot service for boot persistence only)"


def test_should_support_ram_led_status_checking(host_proxmox_role_path):
    """RAM LED control should support status checking mode.

    Validates:
    - Tasks exist to check RAM LED systemd service status
    - Tasks are conditional on ram_lights_action == 'status'
    - Tasks check service file existence, service status, and configuration
    - Status tasks follow RGB control pattern

    This supports BDD Scenario 5: Check RAM LED Status
    Linked to Task 5.1: Add status checking tasks for RAM LED
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - File contains ram_lights_action variable references
    assert 'ram_lights_action' in content, \
        "RAM LED control should support ram_lights_action variable"

    # Assert - Has status checking conditional
    assert "ram_lights_action == 'status'" in content, \
        "RAM LED control should have tasks conditional on ram_lights_action == 'status'"

    # Assert - Check for service status tasks
    status_tasks_found = []
    for task in tasks:
        if isinstance(task, dict) and 'when' in task:
            when_clause = task['when']
            when_str = ' '.join(when_clause) if isinstance(when_clause, list) else str(when_clause)
            if 'ram_lights_action' in when_str and 'status' in when_str:
                status_tasks_found.append(task)

    assert len(status_tasks_found) >= 3, \
        f"Should have at least 3 status checking tasks (found {len(status_tasks_found)}): " \
        f"check service file, get service status, read service config"

    # Assert - Tasks use appropriate modules for status checking
    status_task_modules = []
    for task in status_tasks_found:
        # Collect module names used in status tasks
        for module in ['stat', 'systemd', 'slurp', 'debug']:
            if module in task:
                status_task_modules.append(module)

    assert 'stat' in status_task_modules or 'systemd' in status_task_modules, \
        "Status tasks should use 'stat' or 'systemd' module to check service"


def test_should_display_formatted_ram_led_status_output(host_proxmox_role_path):
    """RAM LED status output should be formatted clearly with Arctic lights comparison.

    Validates:
    - Status output task exists with debug module
    - Output includes RAM LED state information
    - Output mentions Arctic lights for comparison
    - Output is formatted with visual separators
    - Task is conditional on ram_lights_action == 'status'

    This supports BDD Scenario 5: Check RAM LED Status
    Linked to Task 5.2: Add formatted output for RAM LED status display
    """
    # Arrange
    ram_led_control_task_file = host_proxmox_role_path / "tasks" / "ram-led-control.yml"

    # Act
    with open(ram_led_control_task_file) as f:
        content = f.read()
        tasks = yaml.safe_load(content)

    # Assert - Has status display task (must check for == 'status', not != 'status')
    status_display_task = None
    for task in tasks:
        if isinstance(task, dict) and 'debug' in task and 'when' in task:
            when_clause = task['when']
            when_str = ' '.join(when_clause) if isinstance(when_clause, list) else str(when_clause)
            # Must be checking FOR status mode (not excluding it)
            if 'ram_lights_action' in when_str and "== 'status'" in when_str:
                status_display_task = task
                break

    assert status_display_task is not None, \
        "Should have a debug task to display RAM LED status (conditional on ram_lights_action == 'status')"

    # Assert - Output includes key information
    debug_msg = str(status_display_task.get('debug', {}))
    assert 'RAM LED' in debug_msg or 'RAM' in debug_msg, \
        "Status output should mention RAM LEDs"

    # Assert - Output mentions Arctic lights for comparison
    assert 'Arctic' in debug_msg or 'RGB' in debug_msg, \
        "Status output should show Arctic lights status for comparison"

    # Assert - Has visual formatting
    # Check for common formatting patterns (borders, headers, sections)
    formatted = '═' in content or '─' in content or 'STATUS' in content.upper()
    assert formatted, \
        "Status output should have visual formatting (borders/headers/sections)"
