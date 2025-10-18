# Specification: RGB/LED Light Control for Arctic Cooling and RAM

## Overview
### Purpose
This feature provides the ability to turn RGB/LED lights on and off for the Arctic fans, Arctic CPU cooler, and RAM modules on the Proxmox host (Android #19).

**Problems Solved:**
- Distracting RGB lighting when recording videos or working in the server room
- Light pollution when the server is in a shared living/working space
- Inability to maintain a professional appearance during video calls or recordings
- Unnecessary power consumption from RGB lighting when not needed

This feature enables the homelab administrator to control the visual appearance of the server hardware without affecting system performance or functionality.

### Stakeholders
- **Homelab Administrator**: Primary user who needs to control RGB lighting based on context (recording, sleeping, professional settings)
- **Proxmox Host (Android #19)**: Physical server affected by the configuration changes
- **Household Members**: Benefit from reduced light pollution in shared spaces
- **Video Content Consumers**: Better video quality without distracting RGB effects in background

## Functional Requirements
### Core Functionality
- **FR1**: Turn all RGB/LED lights OFF (Arctic fans, Arctic CPU cooler, and RAM modules)
- **FR2**: Turn all RGB/LED lights ON (Arctic fans, Arctic CPU cooler, and RAM modules)
- **FR3**: Persist RGB light state across system reboots (lights maintain their on/off state after restart)
- **FR4**: Auto-detect and install required RGB control software (liquidctl)
- **FR5**: Validate that RGB control software can communicate with the hardware components
- **FR6**: Provide idempotent operation (running the same configuration multiple times produces the same result)
- **FR7**: Handle hardware compatibility issues gracefully with clear error messages
- **FR8**: Support checking current RGB light status without changing the state

### User Interactions
**Ansible Playbook Execution:**
```bash
# Turn lights off
ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml \
  -e "rgb_lights_state=off"

# Turn lights on
ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml \
  -e "rgb_lights_state=on"

# Check status
ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml \
  -e "rgb_lights_action=status"
```

**Makefile Targets (convenience wrappers):**
```bash
make proxmox-rgb-lights-off    # Turn all RGB lights off
make proxmox-rgb-lights-on     # Turn all RGB lights on
make proxmox-rgb-lights-status # Check current status
```

**Expected Output:**
- Clear confirmation messages showing which lights were affected
- Status of each hardware component (Arctic fans, CPU cooler, RAM)
- Error messages if hardware is not detected or compatible
- Current state when checking status

## Behavior-Driven Development Scenarios

### Scenario 1: First-time Setup and Turn Lights Off
**Given** the Proxmox host has Arctic fans, Arctic CPU cooler, and RGB RAM installed
**And** no RGB control software is currently installed
**When** the administrator runs the Ansible playbook with `rgb_lights_state=off`
**Then** liquidctl is automatically installed via pip3
**And** all RGB/LED lights on Arctic fans, CPU cooler, and RAM are turned off using liquidctl
**And** the configuration persists across system reboots

### Scenario 2: Turn Lights On After Being Off
**Given** the RGB control software is already installed
**And** all RGB/LED lights are currently turned off
**When** the administrator runs the Ansible playbook with `rgb_lights_state=on`
**Then** all RGB/LED lights on Arctic fans, CPU cooler, and RAM are turned on
**And** the system displays confirmation of the state change

### Scenario 3: Idempotent Operation - Lights Already Off
**Given** the RGB control software is installed
**And** all RGB/LED lights are already turned off
**When** the administrator runs the Ansible playbook with `rgb_lights_state=off` again
**Then** the playbook completes successfully without errors
**And** the lights remain off
**And** Ansible reports no changes made (idempotent behavior)

### Scenario 4: Check RGB Light Status
**Given** the RGB control software is installed
**And** the RGB lights are in a known state (either on or off)
**When** the administrator runs the Ansible playbook with `rgb_lights_action=status`
**Then** the system displays the current state of RGB/LED lights for each component
**And** no state changes occur
**And** the output clearly indicates whether lights are on or off

### Scenario 5: RGB Lights Persist After Reboot
**Given** the RGB control software is installed
**And** the administrator has set RGB lights to off
**When** the Proxmox host is rebooted
**Then** the RGB/LED lights remain off after the system boots
**And** the RGB control software service starts automatically

### Scenario 6: Hardware Not Detected
**Given** the RGB control software is installed
**And** the Arctic fans or CPU cooler are not detected by the RGB control software
**When** the administrator runs the Ansible playbook with `rgb_lights_state=off`
**Then** the playbook displays a clear error message indicating which hardware is not detected
**And** the playbook provides troubleshooting guidance
**And** the Ansible task fails with a meaningful error code

### Scenario 7: Software Installation Failure
**Given** no RGB control software is installed
**And** the package repository is unavailable or software cannot be installed
**When** the administrator runs the Ansible playbook with `rgb_lights_state=off`
**Then** the playbook displays a clear error message about the installation failure
**And** the playbook fails gracefully without leaving the system in an inconsistent state
**And** troubleshooting steps are provided in the error output

### Scenario 8: Using Makefile Convenience Targets
**Given** the Makefile has been configured with RGB light control targets
**When** the administrator runs `make proxmox-rgb-lights-off`
**Then** the underlying Ansible playbook is executed with `rgb_lights_state=off`
**And** all RGB/LED lights are turned off
**And** the output is formatted clearly for command-line viewing

## Acceptance Criteria
- [ ] **AC1**: liquidctl is automatically installed via pip3 on first run if not present
- [ ] **AC2**: All RGB/LED lights can be turned OFF via `rgb_lights_state=off` parameter
- [ ] **AC3**: All RGB/LED lights can be turned ON via `rgb_lights_state=on` parameter
- [ ] **AC4**: RGB light state persists across system reboots (lights maintain on/off state after restart)
- [ ] **AC5**: Running the playbook multiple times with the same configuration produces no changes (idempotent)
- [ ] **AC6**: RGB light status can be queried via `rgb_lights_action=status` without changing state
- [ ] **AC7**: Status output clearly shows ON/OFF state for Arctic fans, CPU cooler, and RAM
- [ ] **AC8**: When hardware is not detected, error message clearly identifies which component failed
- [ ] **AC9**: Error messages include troubleshooting guidance and actionable next steps
- [ ] **AC10**: Installation failures leave system in consistent state (no partial configurations)
- [ ] **AC11**: Makefile targets (`make proxmox-rgb-lights-off/on/status`) correctly invoke Ansible playbook
- [ ] **AC12**: Ansible playbook completes successfully (exit code 0) when operations succeed
- [ ] **AC13**: Ansible playbook fails with meaningful error code when operations fail
- [ ] **AC14**: RGB control software service is enabled and starts automatically on boot
- [ ] **AC15**: All BDD acceptance tests pass (8 scenarios in rgb_led_control.feature)

## Non-Functional Requirements
### Performance
- Ansible playbook execution should complete in under 2 minutes for typical operations
- Initial software installation may take 3-5 minutes (downloading packages)
- Status checks should return results within 5 seconds
- RGB state changes should take effect within 1 second

### Security
- SSH key-based authentication only (no passwords)
- RGB control software runs with minimum necessary privileges
- No sensitive data (credentials, keys) stored in Ansible variables or logs
- Follows Proxmox security best practices for service configuration

### Usability
- Clear, actionable error messages with troubleshooting guidance
- Human-readable status output (not just machine-parseable)
- Consistent output formatting across all operations
- Progress indicators for long-running operations
- Makefile targets provide convenient shortcuts for common operations

## Constraints and Assumptions
### Technical Constraints
- **Physical Access Required**: Initial SSH key setup requires physical or IPMI access to Proxmox host
- **Hardware Compatibility**: RGB control software (OpenRGB/liquidctl) must support the specific Arctic hardware models
- **Root Privileges**: Ansible tasks require sudo/root access on Proxmox host for hardware control
- **Linux Kernel Support**: Requires Linux kernel 5.x+ with RGB hardware driver support
- **Single Execution**: Cannot run multiple RGB control operations simultaneously (hardware limitations)

### Assumptions
- **Hardware Connectivity**: Arctic fans, CPU cooler, and RAM are connected via standard RGB protocols (USB HID, SMBus, or I2C)
- **Hardware Detection**: RGB hardware is detectable by Linux kernel and appears in `/sys/bus` or `/dev/`
- **Software Availability**: liquidctl is installable via pip3
- **Network Connectivity**: Stable SSH connection to Proxmox host during playbook execution
- **No Conflicting Software**: No other RGB control software is managing the same hardware
- **Homelab Environment**: This is for a homelab/development environment, not production infrastructure

### Dependencies
- **SSH Access**: Working SSH connectivity to Proxmox host (192.168.0.19) with key-based authentication
- **Ansible**: Ansible 2.9+ installed in development environment
- **Python**: Python 3.x installed on Proxmox host
- **Package Manager**: apt (Debian/Ubuntu) package manager on Proxmox
- **RGB Control Software**: liquidctl installed via pip3
- **Hardware Drivers**: Linux kernel drivers for USB/I2C/SMBus RGB communication
- **Proxmox Host Role**: Depends on `host-proxmox` Ansible role structure
- **Makefile**: Project Makefile for convenience target integration

## Open Questions
- [ ] **Q1**: Which specific Arctic fan model is installed? (Different models may require different RGB control approaches)
- [ ] **Q2**: Which specific Arctic CPU cooler model? (e.g., Liquid Freezer II, Freezer 36)
- [ ] **Q3**: Which RAM brand and model? (Corsair, G.Skill, Kingston, etc. - affects compatibility)
- [x] **Q4**: ~~Should we support BOTH OpenRGB and liquidctl, or choose one based on hardware detection?~~ **RESOLVED:** Using liquidctl only (OpenRGB failed to control lights)
- [ ] **Q5**: Should there be a "dry-run" or "test" mode that shows what would change without actually changing lights?
- [ ] **Q6**: Should we support custom colors/effects in the future, or keep it strictly on/off for simplicity?
- [ ] **Q7**: Is there a preference for how lights should look when "ON"? (Default RGB cycling, static color, etc.)
- [ ] **Q8**: Should the Ansible role be idempotent for the "on" state even if current color/effect differs?

## Approval
- **Created by:** Claude Code
- **Date:** 2025-10-18
- **Status:** Draft - Ready for Implementation
- **Approved by:** Pending user review
- **Executable Tests**: Created and verified (RED phase - 8 BDD scenarios failing as expected)
- **Test Location**: `android-19-proxmox/tests/bdd/features/rgb_led_control.feature`
