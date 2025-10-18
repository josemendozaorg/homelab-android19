# Specification: PCIe ASPM Kernel Parameter Configuration for Network Stability

## Overview
### Purpose
This feature implements an automated configuration to disable PCIe Active State Power Management (ASPM) on the Proxmox host (Android #19) to resolve critical network stability issues.

**Problem:** The Proxmox server's Intel network card (igc enp11s0) randomly disconnects from the motherboard's PCIe bus after several days of operation, causing complete loss of network connectivity (both SSH port 22 and web UI port 8006). Kernel logs show `PCIe link lost, device now detached` errors, indicating hardware-level disconnection caused by aggressive power management features on the ASUS ProArt motherboard's chipset.

**Solution:** Permanently disable PCIe ASPM at the kernel level by adding the `pcie_aspm=off` boot parameter to GRUB configuration. This prevents the kernel from putting PCIe devices into deep sleep states that the network card cannot reliably wake from.

**Impact:** This is a critical stability fix for production infrastructure. Without this fix, the Proxmox server requires physical console access to recover from network disconnections, making remote homelab management impossible.

### Stakeholders
- **Homelab Administrator**: Primary user requiring stable remote access to Proxmox infrastructure
- **Android #19 (Proxmox Host)**: Main virtualization server affected by network disconnections
- **Android #16 (Bastion Host)**: Requires reliable connectivity to Proxmox for management operations
- **Virtual Machines and LXC Containers**: All services running on Proxmox depend on host network stability
- **Ansible Automation System**: Requires consistent SSH connectivity to manage Proxmox configuration

## Functional Requirements
### Core Functionality
1. **GRUB Configuration Modification**: Ansible must modify `/etc/default/grub` on the Proxmox host to add `pcie_aspm=off` to the `GRUB_CMDLINE_LINUX_DEFAULT` parameter
2. **Configuration Backup**: Create a timestamped backup of the original `/etc/default/grub` file before making any modifications
3. **Idempotent Updates**: Ensure the configuration can be safely run multiple times without duplicating the parameter or causing errors
4. **GRUB Bootloader Update**: Execute `update-grub` command to apply the configuration changes to the bootloader
5. **Reboot Handling**: Provide clear notification that a system reboot is required for changes to take effect, but do not automatically reboot (allow administrator control)
6. **Verification Command**: Provide ability to verify that the kernel parameter is active after reboot by checking `/proc/cmdline`
7. **Ansible Role Integration**: Implement as part of the existing `host-proxmox` Ansible role for automated deployment
8. **Targeted Deployment**: Apply configuration only to the Proxmox host (Android #19), not to other machines in the inventory

### User Interactions
**Primary Workflow:**
1. Administrator runs `make proxmox-host-setup` or `make proxmox-deploy` from the development environment
2. Ansible connects to Proxmox host via SSH using established key authentication
3. Ansible automatically:
   - Backs up current GRUB configuration
   - Modifies GRUB configuration file
   - Updates GRUB bootloader
   - Reports success/failure and whether reboot is needed
4. Administrator reviews Ansible output for any errors
5. Administrator schedules and executes system reboot at appropriate time
6. After reboot, administrator can verify configuration with `cat /proc/cmdline` (should show `pcie_aspm=off`)

**No manual steps required on the Proxmox host itself** - all configuration is automated through Ansible.

## Behavior-Driven Development Scenarios

### Scenario 1: First-Time Configuration on Clean System
**Given** the Proxmox host has a default GRUB configuration without `pcie_aspm=off` parameter
**And** the GRUB_CMDLINE_LINUX_DEFAULT line contains only `"quiet"`
**When** the Ansible playbook runs the GRUB configuration task
**Then** a backup of `/etc/default/grub` is created with timestamp
**And** the GRUB_CMDLINE_LINUX_DEFAULT line is modified to `"quiet pcie_aspm=off"`
**And** the `update-grub` command executes successfully
**And** Ansible reports that a reboot is required for changes to take effect

### Scenario 2: Idempotent Re-run on Already Configured System
**Given** the Proxmox host already has `pcie_aspm=off` in GRUB_CMDLINE_LINUX_DEFAULT
**And** the current configuration is `"quiet pcie_aspm=off"`
**When** the Ansible playbook runs the GRUB configuration task again
**Then** Ansible detects the parameter is already present
**And** no modifications are made to `/etc/default/grub`
**And** no new backup file is created
**And** the `update-grub` command is skipped
**And** Ansible reports no changes were needed

### Scenario 3: Verification After Reboot
**Given** the GRUB configuration has been updated with `pcie_aspm=off`
**And** the Proxmox host has been rebooted
**When** an administrator checks `/proc/cmdline`
**Then** the output contains `pcie_aspm=off` parameter
**And** the kernel is running with PCIe ASPM disabled
**And** network card stability is maintained without PCIe disconnections

### Scenario 4: Configuration Backup Creation
**Given** the Proxmox host has an existing `/etc/default/grub` file
**And** no previous backups exist from this automation
**When** the Ansible playbook runs the GRUB configuration task for the first time
**Then** a backup file is created at `/etc/default/grub.backup-YYYYMMDD-HHMMSS`
**And** the backup contains the exact original content
**And** the backup has the same permissions as the original file

### Scenario 5: Configuration with Existing Manual Parameter
**Given** the Proxmox host has GRUB_CMDLINE_LINUX_DEFAULT set to `"quiet intel_iommu=on"`
**And** no `pcie_aspm=off` parameter exists
**When** the Ansible playbook runs the GRUB configuration task
**Then** the configuration is updated to `"quiet intel_iommu=on pcie_aspm=off"`
**And** existing parameters are preserved
**And** parameters are space-separated correctly
**And** `update-grub` runs successfully

### Scenario 6: GRUB Update Failure Handling
**Given** the Proxmox host's `/etc/default/grub` has been modified correctly
**And** the `update-grub` command fails due to disk error or other issue
**When** the Ansible playbook attempts to run `update-grub`
**Then** Ansible reports the task failure with error details
**And** the playbook execution stops before proceeding to further tasks
**And** the administrator is notified that manual intervention is required

### Scenario 7: Rollback from Backup
**Given** the GRUB configuration has been modified but causes boot issues
**And** a backup file exists at `/etc/default/grub.backup-*`
**When** an administrator manually restores from the backup
**Then** the original GRUB configuration is restored
**And** `update-grub` can be run to revert the bootloader
**And** the system can boot with the original configuration

## Acceptance Criteria
- [ ] **GRUB Configuration**: `/etc/default/grub` file is modified to include `pcie_aspm=off` in GRUB_CMDLINE_LINUX_DEFAULT parameter
- [ ] **Backup Created**: A timestamped backup of original `/etc/default/grub` is created before any modifications
- [ ] **Idempotence**: Running the Ansible task multiple times does not duplicate the parameter or cause errors
- [ ] **GRUB Updated**: The `update-grub` command executes successfully and updates the bootloader configuration
- [ ] **Kernel Parameter Active**: After reboot, `/proc/cmdline` contains `pcie_aspm=off` parameter
- [ ] **Ansible Integration**: Configuration task is integrated into the `host-proxmox` Ansible role
- [ ] **Makefile Command**: The configuration can be deployed using `make proxmox-host-setup` or similar command
- [ ] **Error Handling**: Ansible playbook fails gracefully with clear error messages if `update-grub` fails
- [ ] **Existing Parameters Preserved**: Any existing kernel parameters in GRUB configuration are maintained
- [ ] **Reboot Notification**: Ansible output clearly indicates when a system reboot is required
- [ ] **Verification Process**: Documentation includes steps to verify the configuration is active after reboot
- [ ] **Network Stability**: After implementation and reboot, Proxmox network connectivity remains stable for extended periods (no PCIe link loss)
- [ ] **SSH Access**: SSH connectivity to Proxmox remains functional after reboot
- [ ] **Web UI Access**: Proxmox web UI (port 8006) remains accessible after reboot
- [ ] **Documentation**: Implementation is documented in project README or appropriate documentation file

## Non-Functional Requirements
### Performance
- GRUB configuration modification must complete within 5 seconds
- `update-grub` command should complete within 30 seconds under normal conditions
- No measurable performance impact on Proxmox host operation after implementation
- Ansible playbook execution time should not increase by more than 1 minute

### Security
- Backup files must maintain the same permissions as the original `/etc/default/grub` (typically 0644 root:root)
- No sensitive information should be exposed in Ansible logs or output
- Configuration changes must be traceable (backup files provide audit trail)
- Only authorized administrators with SSH access can deploy this configuration

### Usability
- Ansible output must clearly indicate success or failure of each step
- Error messages must be descriptive and actionable
- Administrator should not need to manually edit files on the Proxmox host
- Verification process should be simple (single command to check `/proc/cmdline`)
- Documentation must be clear enough for junior administrators to follow

## Constraints and Assumptions
### Technical Constraints
- **Bootloader Requirement**: Proxmox host must use GRUB2 as the bootloader (not systemd-boot, rEFInd, or other alternatives)
- **Operating System**: Must be Debian-based Proxmox VE (tested on Proxmox 7.x and later)
- **Privilege Requirement**: Ansible must have root/sudo access to modify system configuration files
- **Reboot Required**: Changes require a full system reboot to take effect (no hot-reload possible for kernel parameters)
- **Downtime Acceptance**: Administrator must accept brief downtime for reboot (affects all VMs and containers on host)
- **Single Host Target**: Configuration applies only to physical Proxmox host, not to VMs or containers

### Assumptions
- Proxmox host is using GRUB2 bootloader (standard for most installations)
- SSH key authentication to Proxmox is already configured and working
- Ansible has necessary privileges to modify `/etc/default/grub` and run `update-grub`
- The `/etc/default/grub` file exists and is in standard format
- Administrator has physical or remote console access in case of boot issues (IPMI, iLO, or physical access)
- Network issues are caused by PCIe ASPM and not by other hardware failures
- Disabling ASPM will not negatively impact other PCIe devices in the system

### Dependencies
- **Ansible**: Version 2.9 or later with standard modules (lineinfile, command, copy)
- **Python**: Python 3 on Proxmox host for Ansible module execution
- **GRUB Package**: grub-pc or grub-efi package installed on Proxmox host
- **SSH Connectivity**: Working SSH connection from development environment to Proxmox host
- **Existing Infrastructure**: `host-proxmox` Ansible role must exist in project structure
- **Make Targets**: Existing Makefile with targets for deploying Proxmox configuration

## Open Questions
- [ ] **Monitoring**: Should we implement monitoring to detect and alert on future PCIe link loss events in kernel logs?
- [ ] **Verification Task**: Should the Ansible playbook include an automatic verification task to check `/proc/cmdline` after manual reboot?
- [ ] **Rollback Documentation**: Should we create a formal runbook for rolling back this configuration if issues occur?
- [ ] **Testing Strategy**: Should we test this on a non-production Proxmox VM before applying to production?
- [ ] **Other Hardware**: Are there other PCIe devices in the system that might benefit from or be affected by disabling ASPM?
- [ ] **Alternative Solutions**: Should we investigate device-specific ASPM configuration instead of global disable?
- [ ] **Kernel Version**: Does this solution work consistently across different Proxmox/kernel versions (6.x, 5.x kernels)?

## Approval
- **Created by:** Claude Code (TDD Workflow)
- **Date:** 2025-10-15
- **Status:** Draft
- **Approved by:** Pending homelab administrator review
