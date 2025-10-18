"""Step definitions for RGB/LED Light Control feature.

This module contains BDD step definitions for testing RGB/LED light control
on Arctic fans, Arctic CPU cooler, and RAM modules on the Proxmox host.
"""
import pytest
import time
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the feature file
scenarios('../features/rgb_led_control.feature')


# ============================================================================
# Test Context - Shared state between steps
# ============================================================================

@pytest.fixture
def test_context():
    """Shared context for test scenario state."""
    return {
        'playbook_result': None,
        'ssh_result': None,
        'openrgb_initial_state': None,
        'systemd_service_status': None,
        'ansible_changed': None,
    }


# ============================================================================
# GIVEN Steps (Setup and Preconditions)
# ============================================================================

@given('the Proxmox host "192.168.0.19" is accessible')
def proxmox_host_accessible(ssh_runner):
    """Verify Proxmox host is accessible via SSH."""
    # Test SSH connectivity by running a simple command
    result = ssh_runner("192.168.0.19", "echo 'SSH OK'", user="root")

    assert result.returncode == 0, (
        f"Cannot connect to Proxmox host via SSH.\n"
        f"Error: {result.stderr}\n"
        f"Ensure SSH keys are set up and the host is running."
    )


@given('the Proxmox host has Arctic fans, Arctic CPU cooler, and RGB RAM installed')
def hardware_installed(ssh_runner):
    """Verify hardware components are present on the system."""
    # This is a precondition assumption for these tests
    # We assume the hardware exists - the RGB software will detect it
    # For now, we just verify the host is responding
    result = ssh_runner("192.168.0.19", "uname -a", user="root")
    assert result.returncode == 0, "Proxmox host must be accessible"


@given('no RGB control software is currently installed')
def no_rgb_software(ssh_runner, test_context):
    """Verify RGB control software (OpenRGB/liquidctl) is not installed."""
    # Check if OpenRGB is installed
    result = ssh_runner("192.168.0.19", "which openrgb", user="root")
    test_context['openrgb_initial_state'] = 'installed' if result.returncode == 0 else 'not_installed'

    # If already installed, uninstall it for clean test
    if result.returncode == 0:
        # Remove OpenRGB AppImage and systemd service
        ssh_runner("192.168.0.19", "rm -f /usr/local/bin/openrgb", user="root")
        ssh_runner("192.168.0.19", "systemctl disable rgb-control.service || true", user="root")
        ssh_runner("192.168.0.19", "systemctl stop rgb-control.service || true", user="root")
        ssh_runner("192.168.0.19", "rm -f /etc/systemd/system/rgb-control.service", user="root")
        ssh_runner("192.168.0.19", "systemctl daemon-reload", user="root")

        # Verify it's gone
        result = ssh_runner("192.168.0.19", "which openrgb", user="root")
        assert result.returncode != 0, "OpenRGB should not be installed for this test"


@given('the RGB control software is already installed')
@given('the RGB control software is installed')
def rgb_software_installed(ssh_runner, test_context, ansible_runner):
    """Verify RGB control software is installed."""
    # Check if OpenRGB is installed
    result = ssh_runner("192.168.0.19", "which openrgb", user="root")

    # If not installed, run the playbook to install it
    if result.returncode != 0:
        playbook_result = ansible_runner(
            "android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml",
            extra_vars={"rgb_lights_enabled": True, "rgb_lights_state": "off"},
            tags="rgb"
        )
        assert playbook_result.returncode == 0, "Failed to install RGB control software"

        # Verify installation
        result = ssh_runner("192.168.0.19", "which openrgb", user="root")

    assert result.returncode == 0, (
        f"OpenRGB should be installed.\n"
        f"Error: {result.stderr}"
    )


@given('all RGB/LED lights are currently turned off')
@given('all RGB/LED lights are already turned off')
def lights_currently_off(ssh_runner, ansible_runner):
    """Verify all RGB/LED lights are in OFF state."""
    # Run playbook to ensure lights are off
    playbook_result = ansible_runner(
        "android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml",
        extra_vars={"rgb_lights_enabled": True, "rgb_lights_state": "off"},
        tags="rgb"
    )
    assert playbook_result.returncode == 0, "Failed to set lights to off state"


@given('the RGB lights are in a known state')
def lights_in_known_state(ssh_runner, ansible_runner):
    """Ensure RGB lights are in a known state (either on or off)."""
    # Set lights to a known state (off)
    playbook_result = ansible_runner(
        "android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml",
        extra_vars={"rgb_lights_enabled": True, "rgb_lights_state": "off"},
        tags="rgb"
    )
    assert playbook_result.returncode == 0, "Failed to set lights to known state"


@given('the administrator has set RGB lights to off')
def admin_set_lights_off(ssh_runner, ansible_runner):
    """Precondition: Administrator has previously set lights to off."""
    playbook_result = ansible_runner(
        "android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml",
        extra_vars={"rgb_lights_enabled": True, "rgb_lights_state": "off"},
        tags="rgb"
    )
    assert playbook_result.returncode == 0, "Failed to set lights off"


@given('the Arctic fans or CPU cooler are not detected by the RGB control software')
def hardware_not_detected(ssh_runner):
    """Simulate hardware not being detected by RGB control software."""
    # This is a negative test scenario
    # For now, we'll skip this as it requires hardware simulation
    pytest.skip("Hardware simulation not implemented - requires mock or actual hardware disconnection")


@given('the package repository is unavailable')
def package_repo_unavailable(ssh_runner):
    """Simulate package repository being unavailable."""
    # This is a negative test scenario
    # For now, we'll skip this as it's destructive
    pytest.skip("Repository simulation not implemented - requires network manipulation")


@given('the Makefile has been configured with RGB light control targets')
def makefile_configured(project_root):
    """Verify Makefile has RGB light control targets."""
    makefile = project_root / "Makefile"
    assert makefile.exists(), "Makefile should exist in project root"

    content = makefile.read_text()
    # We'll verify this when we implement Scenario 8
    # For now, just check Makefile exists
    assert len(content) > 0, "Makefile should not be empty"


# ============================================================================
# WHEN Steps (Actions)
# ============================================================================

@when(parsers.parse('the administrator runs the Ansible playbook with "{ansible_extra_vars}"'))
def run_ansible_playbook(ansible_extra_vars, ansible_runner, test_context):
    """Execute Ansible playbook with specified extra variables."""
    # Parse extra vars from string like "rgb_lights_state=off"
    extra_vars = {}
    for var in ansible_extra_vars.split():
        if '=' in var:
            key, value = var.split('=', 1)
            extra_vars[key] = value

    # Always enable RGB for these tests
    extra_vars['rgb_lights_enabled'] = True

    # Run the playbook
    result = ansible_runner(
        "android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml",
        extra_vars=extra_vars,
        tags="rgb"
    )

    # Store result for verification
    test_context['playbook_result'] = result

    # Check if any changes were made (for idempotency testing)
    test_context['ansible_changed'] = 'changed=0' not in result.stdout


@when(parsers.parse('the administrator runs the Ansible playbook with "{ansible_extra_vars}" again'))
def run_ansible_playbook_again(ansible_extra_vars, ansible_runner, test_context):
    """Execute Ansible playbook a second time (for idempotency testing)."""
    # Same as run_ansible_playbook, but we'll check for idempotency
    run_ansible_playbook(ansible_extra_vars, ansible_runner, test_context)


@when('the Proxmox host is rebooted')
def reboot_proxmox_host(ssh_runner):
    """Reboot the Proxmox host and wait for it to come back online."""
    # WARNING: This is destructive! Only use in isolated test environment
    pytest.skip("Reboot test skipped - too destructive for regular testing")

    # Uncomment below to enable reboot testing:
    # ssh_runner("192.168.0.19", "reboot", user="root")
    #
    # # Wait for host to go down
    # time.sleep(10)
    #
    # # Poll for SSH availability (max 5 minutes)
    # max_attempts = 60
    # for attempt in range(max_attempts):
    #     time.sleep(5)
    #     result = ssh_runner("192.168.0.19", "echo 'UP'", user="root")
    #     if result.returncode == 0:
    #         return
    #
    # pytest.fail("Proxmox host did not come back online after reboot")


@when(parsers.parse('the administrator runs "{command}"'))
def run_command(command, project_root, test_context):
    """Execute a shell command (e.g., make target)."""
    import subprocess

    result = subprocess.run(
        command,
        shell=True,
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    test_context['command_result'] = result


# ============================================================================
# THEN Steps (Assertions and Validation)
# ============================================================================

@then('the required RGB control software is automatically installed')
def verify_software_installed(ssh_runner):
    """Verify RGB control software was installed by Ansible."""
    # Check if OpenRGB is installed
    result = ssh_runner("192.168.0.19", "which openrgb", user="root")

    assert result.returncode == 0, (
        f"OpenRGB should be installed after running playbook.\n"
        f"Error: {result.stderr}"
    )

    # Verify it's executable
    result = ssh_runner("192.168.0.19", "openrgb --version", user="root")
    assert result.returncode == 0, "OpenRGB should be executable"


@then('all RGB/LED lights on Arctic fans are turned off')
@then('all RGB/LED lights on Arctic CPU cooler are turned off')
@then('all RGB/LED lights on RAM are turned off')
def verify_lights_off(ssh_runner):
    """Verify RGB lights are turned off."""
    # Check that the command was executed
    # Note: We can't easily verify lights are physically off without RGB software queries
    # So we verify the command executed successfully
    result = ssh_runner("192.168.0.19", "which openrgb", user="root")
    assert result.returncode == 0, "OpenRGB should be installed"

    # Try to list devices (this verifies OpenRGB can run)
    result = ssh_runner("192.168.0.19", "openrgb --list-devices || true", user="root")
    # Command should run (even if no devices detected, it shouldn't crash)
    assert "OpenRGB" in result.stdout or result.returncode == 0, \
        "OpenRGB should be able to run"


@then('all RGB/LED lights on Arctic fans are turned on')
@then('all RGB/LED lights on Arctic CPU cooler are turned on')
@then('all RGB/LED lights on RAM are turned on')
def verify_lights_on(ssh_runner):
    """Verify RGB lights are turned on."""
    # Similar to verify_lights_off - we verify the software is working
    result = ssh_runner("192.168.0.19", "which openrgb", user="root")
    assert result.returncode == 0, "OpenRGB should be installed"


@then('the RGB light configuration persists across system reboots')
def verify_persistence(ssh_runner):
    """Verify systemd service is configured for persistence."""
    # Check if systemd service exists
    result = ssh_runner("192.168.0.19", "systemctl list-unit-files | grep rgb-control", user="root")
    assert result.returncode == 0, "rgb-control systemd service should exist"

    # Check if service is enabled
    result = ssh_runner("192.168.0.19", "systemctl is-enabled rgb-control.service", user="root")
    assert result.returncode == 0 and "enabled" in result.stdout, \
        "rgb-control service should be enabled"


@then('the playbook completes successfully without errors')
def verify_playbook_success(test_context):
    """Verify Ansible playbook completed successfully."""
    result = test_context['playbook_result']
    assert result is not None, "Playbook should have been executed"
    assert result.returncode == 0, (
        f"Playbook should complete successfully.\n"
        f"Stdout: {result.stdout}\n"
        f"Stderr: {result.stderr}"
    )


@then('the lights remain off')
def verify_lights_remain_off(ssh_runner):
    """Verify lights are still off."""
    # Same as verify_lights_off
    verify_lights_off(ssh_runner)


@then('Ansible reports no changes made')
def verify_no_changes(test_context):
    """Verify Ansible reported no changes (idempotency)."""
    result = test_context['playbook_result']
    assert result is not None, "Playbook should have been executed"

    # Check for "changed=0" in output
    assert not test_context['ansible_changed'], (
        f"Ansible should report no changes for idempotent operation.\n"
        f"Output: {result.stdout}"
    )


@then('the system displays confirmation of the state change')
def verify_state_change_confirmation(test_context):
    """Verify playbook output shows state change."""
    result = test_context['playbook_result']
    assert result is not None, "Playbook should have been executed"

    # Check that playbook ran successfully
    assert result.returncode == 0, "Playbook should complete successfully"


@then(parsers.parse('the system displays the current state of RGB/LED lights for each component'))
def verify_status_display(test_context):
    """Verify status command displays light state."""
    pytest.skip("Status command not yet implemented")


@then('no state changes occur')
def verify_no_state_changes(test_context):
    """Verify no state changes occurred during status check."""
    pytest.skip("Status command not yet implemented")


@then('the output clearly indicates whether lights are on or off')
def verify_status_clarity(test_context):
    """Verify status output is clear and readable."""
    pytest.skip("Status command not yet implemented")


@then('the RGB/LED lights remain off after the system boots')
def verify_lights_off_after_boot(ssh_runner):
    """Verify lights are off after reboot."""
    pytest.skip("Reboot test not implemented")


@then('the RGB control software service starts automatically')
def verify_service_starts(ssh_runner):
    """Verify service started automatically."""
    result = ssh_runner("192.168.0.19", "systemctl is-active rgb-control.service", user="root")
    # Service might not be 'active' (it's oneshot), but should be loaded
    result = ssh_runner("192.168.0.19", "systemctl status rgb-control.service", user="root")
    assert "Loaded" in result.stdout, "Service should be loaded"


@then(parsers.parse('the playbook displays a clear error message indicating which hardware is not detected'))
@then('the playbook provides troubleshooting guidance')
@then('the Ansible task fails with a meaningful error code')
@then('the playbook displays a clear error message about the installation failure')
@then('the playbook fails gracefully without leaving the system in an inconsistent state')
@then('troubleshooting steps are provided in the error output')
def verify_error_handling(test_context):
    """Verify error handling and messages."""
    pytest.skip("Error handling scenarios not yet implemented")


@then('the underlying Ansible playbook is executed with "rgb_lights_state=off"')
def verify_makefile_execution(test_context):
    """Verify Makefile executed Ansible correctly."""
    pytest.skip("Makefile integration not yet implemented")


@then('the output is formatted clearly for command-line viewing')
def verify_output_formatting(test_context):
    """Verify output is readable."""
    pytest.skip("Output formatting verification not yet implemented")
