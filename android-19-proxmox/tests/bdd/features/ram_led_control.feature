@acceptance @bdd @rgb @hardware @ram
Feature: RAM LED Control for Kingston HyperX Fury
  As a homelab administrator
  I want to control RGB lights on RAM modules independently
  So that I can customize lighting while keeping Arctic cooling components lit

  Background:
    Given the Proxmox host "192.168.0.19" is accessible
    And the Proxmox host has Kingston HyperX Fury RAM with LED capability

  @deployment @first_time_setup
  Scenario: Turn RAM LEDs Off Independently
    Given liquidctl is already installed
    And Arctic lights are currently ON
    When the administrator runs the Ansible playbook with "ram_lights_state=off"
    Then RAM LEDs are turned off
    And Arctic lights remain ON in rainbow mode
    And the system displays confirmation showing RAM LEDs OFF and Arctic lights UNCHANGED

  @deployment
  Scenario: Turn RAM LEDs On Independently
    Given liquidctl is already installed
    And RAM LEDs are currently turned off
    And Arctic lights are currently OFF
    When the administrator runs the Ansible playbook with "ram_lights_state=on"
    Then RAM LEDs are turned on with rainbow effect
    And Arctic lights remain OFF
    And the system displays confirmation showing RAM LEDs ON and Arctic lights UNCHANGED

  @persistence
  Scenario: RAM LED State Persists After Reboot
    Given liquidctl is installed
    And the administrator has set RAM LEDs to off
    And Arctic lights are set to on
    When the Proxmox host is rebooted
    Then RAM LEDs remain off after the system boots
    And Arctic lights remain on after the system boots
    And both RGB control service and RAM control service start automatically

  @idempotency
  Scenario: Idempotent Operation - RAM LEDs Already Off
    Given liquidctl is installed
    And RAM LEDs are already turned off
    When the administrator runs the Ansible playbook with "ram_lights_state=off" again
    Then the playbook completes successfully without errors
    And RAM LEDs remain off
    And Ansible reports no changes made for RAM operations

  @status_check
  Scenario: Check RAM LED Status
    Given liquidctl is installed
    And RAM LEDs are in a known state
    When the administrator runs the Ansible playbook with "ram_lights_action=status"
    Then the system displays the current state of RAM LEDs
    And no state changes occur to RAM or Arctic lights
    And the output clearly indicates whether RAM LEDs are on or off
    And the output shows Arctic lights status for comparison

  @makefile_integration
  Scenario: Using Makefile Convenience Targets
    Given the Makefile has been configured with RAM LED control targets
    When the administrator runs "make proxmox-ram-lights-off"
    Then the underlying Ansible playbook is executed with ram_lights_state=off
    And RAM LEDs are turned off
    And Arctic lights remain in their current state
    And the output is formatted clearly for command-line viewing

  @mixed_state
  Scenario: Mixed State - RAM Off, Arctic On
    Given liquidctl is installed
    And both RAM and Arctic lights are currently on
    When the administrator runs "make proxmox-ram-lights-off"
    And verifies Arctic lights are still on
    Then RAM LEDs are off
    And Arctic fans CPU cooler LEDs remain on in rainbow mode
    And the system can maintain this mixed state across reboots

  @error_handling
  Scenario: liquidctl Not Installed - Dependency Check
    Given liquidctl is NOT installed on the Proxmox host
    When the administrator runs the Ansible playbook with "ram_lights_state=off"
    Then the playbook displays a clear error message indicating liquidctl is required
    And the error message suggests running the RGB control feature first
    And the playbook fails gracefully without making changes
