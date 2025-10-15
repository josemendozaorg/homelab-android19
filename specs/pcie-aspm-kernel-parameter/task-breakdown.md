# Task Breakdown: PCIe ASPM Kernel Parameter Configuration

**Generated:** 2025-10-15
**Total Tasks:** 14
**Scenarios Covered:** 7/7

## Task List

### Task 1: Create Ansible role tasks directory structure for GRUB PCIe ASPM configuration
- **Priority:** High
- **Dependencies:** None
- **Related Scenario:** All scenarios (infrastructure prerequisite)
- **Related Acceptance Criteria:** Ansible Integration
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Verify that task files exist in `android-19-proxmox/configuration-by-ansible/host-proxmox/tasks/` with correct naming (grub-pcie-aspm-*.yml)

### Task 2: Implement task to check if PCIe ASPM parameter already exists in GRUB config
- **Priority:** High
- **Dependencies:** Task 1
- **Related Scenario:** Scenario 2 (Idempotent Re-run)
- **Related Acceptance Criteria:** Idempotence
- **Complexity:** Medium
- **Status:** Pending
- **Test Strategy:** Test reads `/etc/default/grub`, searches for `pcie_aspm=off` in GRUB_CMDLINE_LINUX_DEFAULT, registers fact variable

### Task 3: Implement task to create timestamped backup of GRUB configuration
- **Priority:** High
- **Dependencies:** Task 1
- **Related Scenario:** Scenario 4 (Configuration Backup Creation)
- **Related Acceptance Criteria:** Backup Created
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test uses ansible.builtin.copy with remote_src, preserves permissions, creates timestamped filename, only runs when parameter not already configured

### Task 4: Implement task to add pcie_aspm=off parameter to GRUB configuration
- **Priority:** High
- **Dependencies:** Task 2, Task 3
- **Related Scenario:** Scenario 1 (First-Time Configuration), Scenario 5 (Existing Manual Parameter)
- **Related Acceptance Criteria:** GRUB Configuration, Existing Parameters Preserved
- **Complexity:** Medium
- **Status:** Pending
- **Test Strategy:** Test uses ansible.builtin.lineinfile or replace module, appends `pcie_aspm=off` to GRUB_CMDLINE_LINUX_DEFAULT, preserves existing parameters, only runs when parameter not configured

### Task 5: Implement task to update GRUB bootloader with new configuration
- **Priority:** High
- **Dependencies:** Task 4
- **Related Scenario:** Scenario 1 (First-Time Configuration)
- **Related Acceptance Criteria:** GRUB Updated
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test executes `update-grub` command, registers result, only runs when configuration was changed

### Task 6: Implement task to display reboot notification message
- **Priority:** Medium
- **Dependencies:** Task 5
- **Related Scenario:** Scenario 1 (First-Time Configuration)
- **Related Acceptance Criteria:** Reboot Notification
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test uses ansible.builtin.debug to display message about required reboot, only runs when changes were made

### Task 7: Implement task to verify kernel parameter is active after reboot
- **Priority:** Medium
- **Dependencies:** None (verification task, runs independently)
- **Related Scenario:** Scenario 3 (Verification After Reboot)
- **Related Acceptance Criteria:** Kernel Parameter Active, Verification Process
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test reads `/proc/cmdline`, searches for `pcie_aspm=off`, can run standalone for post-reboot verification

### Task 8: Integrate PCIe ASPM configuration tasks into host-proxmox role main.yml
- **Priority:** High
- **Dependencies:** Task 1-7
- **Related Scenario:** All scenarios
- **Related Acceptance Criteria:** Ansible Integration, Makefile Command
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test that host-proxmox/tasks/main.yml includes grub-pcie-aspm tasks with appropriate tags

### Task 9: Add error handling for GRUB update failures
- **Priority:** Medium
- **Dependencies:** Task 5
- **Related Scenario:** Scenario 6 (GRUB Update Failure Handling)
- **Related Acceptance Criteria:** Error Handling
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test that update-grub task has `failed_when` or similar error handling, displays clear error message, stops playbook on failure

### Task 10: Write unit tests for GRUB PCIe ASPM configuration tasks
- **Priority:** High
- **Dependencies:** Task 1
- **Related Scenario:** All scenarios
- **Related Acceptance Criteria:** All acceptance criteria
- **Complexity:** Medium
- **Status:** Pending
- **Test Strategy:** Create test file similar to test_gpu_passthrough.py, verify task file structure, YAML validity, correct module usage, parameter presence

### Task 11: Create documentation for PCIe ASPM configuration feature
- **Priority:** Low
- **Dependencies:** Task 1-9
- **Related Scenario:** Scenario 7 (Rollback from Backup)
- **Related Acceptance Criteria:** Documentation, Verification Process
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Update CLAUDE.md or create dedicated doc with: deployment instructions, verification steps, rollback procedure, troubleshooting guide

### Task 12: Add Makefile target for PCIe ASPM configuration deployment (if needed)
- **Priority:** Low
- **Dependencies:** Task 8
- **Related Scenario:** All scenarios
- **Related Acceptance Criteria:** Makefile Command
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Verify that existing `make proxmox-host-setup` includes PCIe ASPM configuration, or create new target if needed

### Task 13: Test idempotence by running configuration multiple times
- **Priority:** Medium
- **Dependencies:** Task 1-9
- **Related Scenario:** Scenario 2 (Idempotent Re-run)
- **Related Acceptance Criteria:** Idempotence
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Integration test that runs playbook twice, verifies no changes on second run, no duplicate parameters, no errors

### Task 14: Test preservation of existing kernel parameters
- **Priority:** Medium
- **Dependencies:** Task 4
- **Related Scenario:** Scenario 5 (Configuration with Existing Manual Parameter)
- **Related Acceptance Criteria:** Existing Parameters Preserved
- **Complexity:** Simple
- **Status:** Pending
- **Test Strategy:** Test with mock GRUB config containing `intel_iommu=on`, verify both parameters present after modification

## Implementation Order

1. **Task 10** - Write unit tests first (TDD approach)
2. **Task 1** - Create Ansible role structure
3. **Task 2** - Implement check for existing parameter (enables idempotence)
4. **Task 3** - Implement backup creation
5. **Task 4** - Implement GRUB modification (core functionality)
6. **Task 14** - Test parameter preservation (validate Task 4)
7. **Task 5** - Implement GRUB update
8. **Task 9** - Add error handling to GRUB update
9. **Task 6** - Add reboot notification
10. **Task 7** - Implement verification task
11. **Task 8** - Integrate into host-proxmox role
12. **Task 13** - Test idempotence (integration test)
13. **Task 12** - Verify/add Makefile target
14. **Task 11** - Create documentation

## Implementation Decisions (User Approved)

✓ **Decision 1:** Use `ansible.builtin.replace` module (matches GPU passthrough pattern - consistency with codebase)
✓ **Decision 2:** Add as separate `include_tasks` in `main.yml` with tags (follows existing role pattern)
✓ **Decision 3:** Display notification only, manual reboot (matches specification, safer for production)
✓ **Decision 4:** Create `test_grub_pcie_aspm.py` following GPU passthrough pattern (comprehensive testing)

## Assumptions & Questions (RESOLVED)

### Assumption 1: Ansible Module Choice for GRUB Modification
**Context:** The GPU passthrough role uses `ansible.builtin.replace` with regexp to modify GRUB_CMDLINE_LINUX_DEFAULT. We need to decide the best approach for adding `pcie_aspm=off`.

**Research Summary** (Web search: "Ansible GRUB kernel parameters best practice 2025"):
- `lineinfile` with backrefs and negative lookahead is most common for single parameters
- `replace` module works well for complex modifications with proper regex escaping
- `ini_file` module is simpler but less flexible
- Community consensus: `lineinfile` with negative lookahead for single parameter additions

**Options:**
- **A)** Use `ansible.builtin.lineinfile` with backrefs and negative lookahead ⭐ **RECOMMENDED**
  - Pro: Industry best practice for single parameter additions (backed by research)
  - Pro: Built-in idempotence with negative lookahead pattern `(?!.*pcie_aspm=off)`
  - Pro: Simpler logic, better error messages
  - Pro: Works with backup option
  - Example pattern: `regexp: '^GRUB_CMDLINE_LINUX_DEFAULT="((?:(?!pcie_aspm=off).)*?)"$'`

- **B)** Use `ansible.builtin.replace` with regexp (same as GPU passthrough)
  - Pro: Consistent with existing codebase GPU passthrough pattern
  - Con: More complex regexp for checking if parameter exists
  - Con: Requires separate check task for idempotence

- **C)** Use `ansible.builtin.ini_file` module
  - Pro: Simplest syntax
  - Con: Overwrites entire line (doesn't append), loses existing parameters

- **D)** Create file in `/etc/default/grub.d/` with append syntax
  - Pro: Cleanest separation, easy rollback
  - Con: Not all GRUB versions support grub.d includes
  - Con: Untested pattern in this codebase

### Assumption 2: Integration with Existing host-proxmox Role
**Context:** The host-proxmox role exists with tasks/main.yml. We need to decide how to integrate PCIe ASPM configuration.

**Options:**
- **A)** Add as separate include_tasks in main.yml with tags ⭐ **RECOMMENDED**
  - Pro: Follows existing pattern (see system.yml, storage.yml includes)
  - Pro: Allows selective execution via tags
  - Pro: Clean separation of concerns

- **B)** Add directly to system.yml task file
  - Pro: GRUB is system configuration
  - Con: system.yml might get too large

- **C)** Create separate host-proxmox-pcie-aspm role
  - Pro: Complete isolation
  - Con: Overkill for 4-5 tasks, creates role proliferation

### Assumption 3: Reboot Handling Strategy
**Context:** The kernel parameter requires reboot to take effect. GPU passthrough has a reboot task.

**Options:**
- **A)** Display notification only, manual reboot ⭐ **RECOMMENDED**
  - Pro: Matches specification requirement (#5: "do not automatically reboot")
  - Pro: Administrator controls downtime
  - Pro: Safer for production

- **B)** Include reboot task with `when: false` default
  - Pro: Available if needed
  - Con: Adds complexity

- **C)** Automatic reboot with confirmation prompt
  - Con: Violates specification
  - Con: Dangerous for production

### Assumption 4: Testing Strategy
**Context:** Existing GPU passthrough has comprehensive unit tests. We need to decide testing approach.

**Options:**
- **A)** Create test_grub_pcie_aspm.py following GPU passthrough pattern ⭐ **RECOMMENDED**
  - Pro: Consistent with codebase
  - Pro: Comprehensive coverage
  - Pro: Easy to maintain

- **B)** Add tests to existing test_playbooks.py
  - Pro: Centralized
  - Con: File gets large

- **C)** Use molecule for integration testing
  - Pro: Real environment testing
  - Con: Overkill, requires Docker/VM setup

## Notes

**Leveraging Existing Patterns:**
The `host-proxmox-gpu-passthrough` role provides excellent patterns we can reuse:
- `backup-grub-config.yml` - Timestamped backup with `ansible.builtin.copy`
- `check-iommu-grub.yml` - Fact registration pattern for idempotence
- `configure-grub-iommu.yml` - GRUB modification (though we may use different module)
- `update-grub.yml` - Command execution with result registration
- Comprehensive test coverage in `test_gpu_passthrough.py`

**Key Difference:**
GPU passthrough adds `amd_iommu=on iommu=pt` which are two parameters. We're adding `pcie_aspm=off` which is one parameter. The regexp/lineinfile logic might be simpler.

**Critical Consideration:**
The GRUB modification MUST preserve existing parameters. The GPU passthrough implementation uses:
```yaml
regexp: '^(GRUB_CMDLINE_LINUX_DEFAULT="[^"]*)"$'
replace: '\1 amd_iommu=on iommu=pt"'
```
This appends to the end. We need similar logic that:
1. Checks if `pcie_aspm=off` already exists (don't duplicate)
2. Appends if not present
3. Preserves all existing parameters
