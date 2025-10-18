@acceptance @rgb @hardware
Feature: RGB/LED Light Control for Arctic Cooling and RAM
  As a homelab administrator
  I want to control RGB/LED lights on Arctic fans, CPU cooler, and RAM
  So that I can reduce light pollution and maintain professional appearance

  Background:
    Given the Proxmox host "192.168.0.19" is accessible
    And the Proxmox host has Arctic fans, Arctic CPU cooler, and RGB RAM installed

  @deployment @first_time_setup
  Scenario: First-time Setup and Turn Lights Off
    Given no RGB control software is currently installed
    When the administrator runs the Ansible playbook with "rgb_lights_state=off"
    Then the required RGB control software is automatically installed
    And all RGB/LED lights on Arctic fans are turned off
    And all RGB/LED lights on Arctic CPU cooler are turned off
    And all RGB/LED lights on RAM are turned off
    And the RGB light configuration persists across system reboots

  @happy_path
  Scenario: Turn Lights On After Being Off
    Given the RGB control software is already installed
    And all RGB/LED lights are currently turned off
    When the administrator runs the Ansible playbook with "rgb_lights_state=on"
    Then all RGB/LED lights on Arctic fans are turned on
    And all RGB/LED lights on Arctic CPU cooler are turned on
    And all RGB/LED lights on RAM are turned on
    And the system displays confirmation of the state change

  @idempotency
  Scenario: Idempotent Operation - Lights Already Off
    Given the RGB control software is installed
    And all RGB/LED lights are already turned off
    When the administrator runs the Ansible playbook with "rgb_lights_state=off" again
    Then the playbook completes successfully without errors
    And the lights remain off
    And Ansible reports no changes made

  @status_check
  Scenario: Check RGB Light Status
    Given the RGB control software is installed
    And the RGB lights are in a known state
    When the administrator runs the Ansible playbook with "rgb_lights_action=status"
    Then the system displays the current state of RGB/LED lights for each component
    And no state changes occur
    And the output clearly indicates whether lights are on or off

  @persistence @reboot
  Scenario: RGB Lights Persist After Reboot
    Given the RGB control software is installed
    And the administrator has set RGB lights to off
    When the Proxmox host is rebooted
    Then the RGB/LED lights remain off after the system boots
    And the RGB control software service starts automatically

  @error_handling @hardware_detection
  Scenario: Hardware Not Detected
    Given the RGB control software is installed
    And the Arctic fans or CPU cooler are not detected by the RGB control software
    When the administrator runs the Ansible playbook with "rgb_lights_state=off"
    Then the playbook displays a clear error message indicating which hardware is not detected
    And the playbook provides troubleshooting guidance
    And the Ansible task fails with a meaningful error code

  @error_handling @installation_failure
  Scenario: Software Installation Failure
    Given no RGB control software is installed
    And the package repository is unavailable
    When the administrator runs the Ansible playbook with "rgb_lights_state=off"
    Then the playbook displays a clear error message about the installation failure
    And the playbook fails gracefully without leaving the system in an inconsistent state
    And troubleshooting steps are provided in the error output

  @makefile @convenience
  Scenario: Using Makefile Convenience Targets
    Given the Makefile has been configured with RGB light control targets
    When the administrator runs "make proxmox-rgb-lights-off"
    Then the underlying Ansible playbook is executed with "rgb_lights_state=off"
    And all RGB/LED lights are turned off
    And the output is formatted clearly for command-line viewing
