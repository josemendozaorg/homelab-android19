# Specification: RAM LED Control for Kingston HyperX Fury

## Overview
### Purpose
This feature provides independent control of RAM LED lights (Kingston HyperX Fury modules) separate from the existing Arctic cooling RGB control. While the Arctic lights feature controls all RGB components together, this feature enables granular control to turn RAM LEDs on/off independently.

**Problems Solved:**
- RAM LEDs remain on even when Arctic lights are turned off (no independent control)
- Unable to create lighting configurations like "RAM off, Arctic fans on" or vice versa
- RAM light pollution may be more distracting than case fans in certain scenarios (desk-level visibility)
- Power efficiency: ability to disable RAM LEDs specifically while keeping cooling monitoring LEDs active
- Professional appearance: disable bright RAM LEDs during video calls while maintaining system status visibility

This feature complements the existing Arctic lights control by adding component-level granularity, giving the homelab administrator precise control over each RGB system independently.

### Stakeholders
- **Homelab Administrator**: Primary user who needs independent RAM LED control for different contexts
- **Proxmox Host (Android #19)**: Physical server with Kingston HyperX Fury RAM modules
- **Household Members**: Benefit from selective LED control (RAM can be more visible on desk)
- **Video Content Creators**: Ability to disable distracting RAM LEDs while keeping system monitoring LEDs active
- **Existing Arctic Lights Feature**: This feature extends but does not replace the existing RGB control

## Functional Requirements
### Core Functionality
- **FR1**: Turn RAM LEDs OFF independently (Kingston HyperX Fury modules only)
- **FR2**: Turn RAM LEDs ON independently (Kingston HyperX Fury modules only)
- **FR3**: Persist RAM LED state across system reboots (independent of Arctic lights state)
- **FR4**: Support checking current RAM LED status without changing the state
- **FR5**: Preserve existing Arctic lights control functionality (no interference or conflicts)
- **FR6**: Use existing liquidctl installation (reuse RGB control infrastructure)
- **FR7**: Target only led4 channel (RGB header for RAM) on ASUS Aura LED Controller
- **FR8**: Provide idempotent operation (running same configuration multiple times produces same result)
- **FR9**: Enable mixed lighting states (e.g., RAM off + Arctic on, or RAM on + Arctic off)

### User Interactions
**Ansible Playbook Execution:**
```bash
# Turn RAM LEDs off (independently)
ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml \
  -e "ram_lights_state=off"

# Turn RAM LEDs on (independently)
ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml \
  -e "ram_lights_state=on"

# Check RAM LED status
ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml \
  -e "ram_lights_action=status"
```

**Makefile Targets (convenience wrappers):**
```bash
make proxmox-ram-lights-off     # Turn RAM LEDs off (Arctic lights unchanged)
make proxmox-ram-lights-on      # Turn RAM LEDs on (Arctic lights unchanged)
make proxmox-ram-lights-status  # Check current RAM LED status
```

**Combined Operations (examples):**
```bash
# Scenario: Turn off all RGB
make proxmox-rgb-lights-off      # Turn off Arctic lights
make proxmox-ram-lights-off      # Turn off RAM LEDs

# Scenario: RAM off, Arctic on
make proxmox-ram-lights-off      # Turn off RAM LEDs
make proxmox-rgb-lights-on       # Turn on Arctic lights

# Scenario: RAM on, Arctic off
make proxmox-ram-lights-on       # Turn on RAM LEDs
make proxmox-rgb-lights-off      # Turn off Arctic lights
```

**Expected Output:**
- Clear confirmation messages showing RAM LED state changes
- Status of RAM hardware component (Kingston HyperX Fury)
- Explicit indication that Arctic lights are NOT affected by RAM operations
- Current state when checking status
- Warning if liquidctl is not installed (dependency on RGB control feature)

## Behavior-Driven Development Scenarios

### Scenario 1: Turn RAM LEDs Off Independently
**Given** the Proxmox host has Kingston HyperX Fury RAM with LED capability
**And** liquidctl is already installed (from RGB control feature)
**And** Arctic lights are currently ON (rainbow effect)
**When** the administrator runs the Ansible playbook with `ram_lights_state=off`
**Then** RAM LEDs (led4 channel) are turned off
**And** Arctic lights remain ON in rainbow mode (led1, led2, led3 unchanged)
**And** the system displays confirmation showing "RAM LEDs: OFF, Arctic lights: UNCHANGED"

### Scenario 2: Turn RAM LEDs On Independently
**Given** the Proxmox host has Kingston HyperX Fury RAM
**And** RAM LEDs are currently turned off
**And** Arctic lights are currently OFF
**When** the administrator runs the Ansible playbook with `ram_lights_state=on`
**Then** RAM LEDs (led4 channel) are turned on with rainbow effect
**And** Arctic lights remain OFF (led1, led2, led3 unchanged)
**And** the system displays confirmation showing "RAM LEDs: ON, Arctic lights: UNCHANGED"

### Scenario 3: RAM LED State Persists After Reboot
**Given** liquidctl is installed
**And** the administrator has set RAM LEDs to off
**And** Arctic lights are set to on
**When** the Proxmox host is rebooted
**Then** RAM LEDs remain off after the system boots
**And** Arctic lights remain on after the system boots
**And** both RGB control service and RAM control service start automatically

### Scenario 4: Idempotent Operation - RAM LEDs Already Off
**Given** liquidctl is installed
**And** RAM LEDs are already turned off
**When** the administrator runs the Ansible playbook with `ram_lights_state=off` again
**Then** the playbook completes successfully without errors
**And** RAM LEDs remain off
**And** Ansible reports no changes made (idempotent behavior)

### Scenario 5: Check RAM LED Status
**Given** liquidctl is installed
**And** RAM LEDs are in a known state (either on or off)
**When** the administrator runs the Ansible playbook with `ram_lights_action=status`
**Then** the system displays the current state of RAM LEDs
**And** no state changes occur to RAM or Arctic lights
**And** the output clearly indicates whether RAM LEDs are on or off
**And** the output shows Arctic lights status for comparison

### Scenario 6: Using Makefile Convenience Targets
**Given** the Makefile has been configured with RAM LED control targets
**When** the administrator runs `make proxmox-ram-lights-off`
**Then** the underlying Ansible playbook is executed with `ram_lights_state=off`
**And** RAM LEDs are turned off
**And** Arctic lights remain in their current state
**And** the output is formatted clearly for command-line viewing

### Scenario 7: Mixed State - RAM Off, Arctic On
**Given** liquidctl is installed
**And** both RAM and Arctic lights are currently on
**When** the administrator runs `make proxmox-ram-lights-off`
**And** verifies Arctic lights are still on
**Then** RAM LEDs are off
**And** Arctic fans, CPU cooler LEDs remain on in rainbow mode
**And** the system can maintain this mixed state across reboots

### Scenario 8: liquidctl Not Installed (Dependency Check)
**Given** liquidctl is NOT installed on the Proxmox host
**When** the administrator runs the Ansible playbook with `ram_lights_state=off`
**Then** the playbook displays a clear error message indicating liquidctl is required
**And** the error message suggests running the RGB control feature first
**And** the playbook fails gracefully without making changes

## Acceptance Criteria
- [ ] **AC1**: RAM LED control uses existing liquidctl installation (dependency on RGB control feature)
- [ ] **AC2**: RAM LEDs can be turned OFF via `ram_lights_state=off` parameter (independent of Arctic lights)
- [ ] **AC3**: RAM LEDs can be turned ON via `ram_lights_state=on` parameter (independent of Arctic lights)
- [ ] **AC4**: RAM LED state persists across system reboots (independent of Arctic lights state)
- [ ] **AC5**: Running the playbook multiple times with the same configuration produces no changes (idempotent)
- [ ] **AC6**: RAM LED status can be queried via `ram_lights_action=status` without changing state
- [ ] **AC7**: Status output clearly shows RAM LED state and compares with Arctic lights status
- [ ] **AC8**: Turning RAM LEDs off does NOT affect Arctic lights (led1, led2, led3 unchanged)
- [ ] **AC9**: Turning RAM LEDs on does NOT affect Arctic lights (led1, led2, led3 unchanged)
- [ ] **AC10**: Mixed lighting states are supported (e.g., RAM off + Arctic on)
- [ ] **AC11**: Makefile targets (`make proxmox-ram-lights-off/on/status`) correctly invoke Ansible playbook
- [ ] **AC12**: Ansible playbook completes successfully (exit code 0) when operations succeed
- [ ] **AC13**: RAM LED control service is enabled and starts automatically on boot
- [ ] **AC14**: Confirmation messages explicitly state "RAM LEDs changed, Arctic lights UNCHANGED"
- [ ] **AC15**: All BDD acceptance tests pass (8 scenarios in ram_led_control.feature)

## Non-Functional Requirements
### Performance
- Ansible playbook execution should complete in under 30 seconds for typical operations
- RAM LED state changes should take effect within 1 second
- Status checks should return results within 5 seconds
- No performance impact on Arctic lights control feature

### Security
- Reuse existing SSH key-based authentication (no new credentials)
- RGB control software runs with minimum necessary privileges
- No sensitive data stored in Ansible variables or logs
- Follows Proxmox security best practices for service configuration

### Usability
- Clear, actionable confirmation messages with explicit "Arctic lights UNCHANGED" indicators
- Human-readable status output (not just machine-parseable)
- Consistent output formatting with RGB control feature
- Makefile targets provide convenient shortcuts for common operations
- Error messages clearly indicate dependency on RGB control feature

## Constraints and Assumptions
### Technical Constraints
- **Dependency on RGB Control Feature**: Requires liquidctl to be installed by rgb-led-control feature
- **Hardware Limitation**: Can only control led4 channel (RGB header for RAM) on ASUS Aura LED Controller
- **Single LED Channel**: All RAM modules controlled together (cannot control individual DIMM slots)
- **Hardware Compatibility**: Assumes Kingston HyperX Fury RAM is connected to motherboard RGB header
- **Root Privileges**: Ansible tasks require sudo/root access on Proxmox host for hardware control
- **No Concurrent Modification**: Cannot run RGB control and RAM control operations simultaneously

### Assumptions
- **liquidctl Pre-installed**: RGB control feature has already installed and configured liquidctl
- **Hardware Connectivity**: Kingston HyperX Fury RAM is connected via standard RGB protocol to motherboard header
- **Hardware Detection**: RAM RGB hardware is detectable by liquidctl via ASUS Aura LED Controller
- **Network Connectivity**: Stable SSH connection to Proxmox host during playbook execution
- **No Conflicting Software**: No other RGB control software is managing the RAM LEDs
- **Homelab Environment**: This is for a homelab/development environment, not production infrastructure
- **Service Independence**: RAM control service can run independently alongside RGB control service

### Dependencies
- **RGB Control Feature**: MUST be deployed first to install liquidctl
- **SSH Access**: Working SSH connectivity to Proxmox host (192.168.0.19) with key-based authentication
- **Ansible**: Ansible 2.9+ installed in development environment
- **Python**: Python 3.x installed on Proxmox host
- **liquidctl**: Installed via pip3 (from RGB control feature)
- **Hardware Drivers**: Linux kernel drivers for RGB communication
- **Proxmox Host Role**: Depends on `host-proxmox` Ansible role structure
- **Makefile**: Project Makefile for convenience target integration
- **Systemd**: For persistence service management

## Open Questions
- [ ] **Q1**: Should RAM control be integrated into the existing RGB control tasks or kept completely separate?
- [ ] **Q2**: Should there be a combined command to set all lights (Arctic + RAM) to the same state?
- [ ] **Q3**: How should status output be formatted when showing both RAM and Arctic states?
- [ ] **Q4**: Should we support custom RAM LED effects (static colors, breathing) or keep it strictly on/off?
- [ ] **Q5**: Is there value in controlling individual RAM DIMM slots if hardware supports it?
- [ ] **Q6**: Should we create a unified "lighting control" feature that manages both granularly?

## Approval
- **Created by:** Claude Code
- **Date:** 2025-10-19
- **Status:** Draft - Ready for Implementation
- **Approved by:** Pending user review
- **Executable Tests**: Created and verified (RED phase - 8 BDD scenarios skipping as expected)
- **Test Location**: `android-19-proxmox/tests/bdd/features/ram_led_control.feature`
