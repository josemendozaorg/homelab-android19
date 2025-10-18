# Task Breakdown: RGB/LED Light Control for Arctic Cooling and RAM

**Generated:** 2025-10-18
**Total Scenarios:** 8
**Total TDD Tasks:** 18
**Implementation Strategy:** Outside-In (BDD → TDD)

---

## Scenario 1: First-time Setup and Turn Lights Off

**Given-When-Then:**
- **Given:** Proxmox host has Arctic fans, Arctic CPU cooler, and RGB RAM installed AND no RGB control software is currently installed
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off`
- **Then:** Required RGB control software is automatically installed AND all RGB/LED lights are turned off AND configuration persists across reboots

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:13`
**Status:** ❌ FAILING (as expected - outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC1: RGB control software automatically installed on first run if not present
- [ ] AC2: All RGB/LED lights can be turned OFF via `rgb_lights_state=off` parameter
- [ ] AC4: RGB light state persists across system reboots
- [ ] AC12: Ansible playbook completes successfully (exit code 0) when operations succeed

### Required Components (TDD Tasks):

#### Task 1.1: Create Ansible RGB Control Role Structure
- **Description:** Create the base Ansible role structure for RGB LED control within host-proxmox
- **Type:** Unit Test (structure validation)
- **Dependencies:** None
- **Test Strategy:** Verify role directories and files exist with correct structure
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.2: Detect RGB Control Software Installation Status
- **Description:** Ansible task to check if OpenRGB or liquidctl is already installed
- **Type:** Unit Test
- **Dependencies:** Task 1.1
- **Test Strategy:** Test detection logic for installed vs not installed states
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.3: Install RGB Control Software (OpenRGB)
- **Description:** Ansible task to install OpenRGB via apt package manager
- **Type:** Unit Test
- **Dependencies:** Task 1.2
- **Test Strategy:** Test package installation task (idempotent, handles errors)
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.4: Detect RGB Hardware Components
- **Description:** Validate RGB hardware is detected by OpenRGB
- **Type:** Unit Test
- **Dependencies:** Task 1.3
- **Test Strategy:** Test hardware detection command execution and parsing
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.5: Turn RGB Lights Off
- **Description:** Ansible task to execute OpenRGB command to turn lights off
- **Type:** Unit Test
- **Dependencies:** Task 1.4
- **Test Strategy:** Test command execution for turning lights off
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.6: Configure RGB Persistence (Systemd Service)
- **Description:** Create and enable systemd service to maintain RGB state on reboot
- **Type:** Unit Test
- **Dependencies:** Task 1.5
- **Test Strategy:** Test systemd service creation and enablement
- **Status:** Pending
- **Linked Scenario:** Scenario 1

### Scenario Completion Criteria:
- [ ] All component unit tests pass
- [ ] All integration tests pass
- [ ] **Acceptance test for Scenario 1 passes** ← BDD validation

---

## Scenario 2: Turn Lights On After Being Off

**Given-When-Then:**
- **Given:** RGB control software is already installed AND all RGB/LED lights are currently turned off
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=on`
- **Then:** All RGB/LED lights are turned on AND system displays confirmation

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:23`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC3: All RGB/LED lights can be turned ON via `rgb_lights_state=on` parameter
- [ ] AC12: Ansible playbook completes successfully

### Required Components (TDD Tasks):

#### Task 2.1: Turn RGB Lights On
- **Description:** Ansible task to execute OpenRGB command to turn lights on
- **Type:** Unit Test
- **Dependencies:** Task 1.5 (reuses RGB control infrastructure)
- **Test Strategy:** Test command execution for turning lights on
- **Status:** Pending
- **Linked Scenario:** Scenario 2

#### Task 2.2: Display State Change Confirmation
- **Description:** Add debug output showing which components' lights were affected
- **Type:** Unit Test
- **Dependencies:** Task 2.1
- **Test Strategy:** Test Ansible debug/logging output formatting
- **Status:** Pending
- **Linked Scenario:** Scenario 2

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 2 passes**

---

## Scenario 3: Idempotent Operation - Lights Already Off

**Given-When-Then:**
- **Given:** RGB control software is installed AND all RGB/LED lights are already turned off
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off` again
- **Then:** Playbook completes successfully AND lights remain off AND Ansible reports no changes made

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:30`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC5: Running playbook multiple times with same configuration produces no changes (idempotent)
- [ ] AC12: Ansible playbook completes successfully

### Required Components (TDD Tasks):

#### Task 3.1: Check Current RGB Light State
- **Description:** Query OpenRGB for current RGB light state before making changes
- **Type:** Unit Test
- **Dependencies:** Task 1.4
- **Test Strategy:** Test state query command and result parsing
- **Status:** Pending
- **Linked Scenario:** Scenario 3

#### Task 3.2: Implement Idempotent State Change Logic
- **Description:** Only change lights if current state differs from desired state
- **Type:** Unit Test
- **Dependencies:** Task 3.1
- **Test Strategy:** Test conditional execution (changed=0 when state matches)
- **Status:** Pending
- **Linked Scenario:** Scenario 3

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 3 passes**

---

## Scenario 4: Check RGB Light Status

**Given-When-Then:**
- **Given:** RGB control software is installed AND RGB lights are in a known state
- **When:** Administrator runs the Ansible playbook with `rgb_lights_action=status`
- **Then:** System displays current state of RGB/LED lights for each component AND no state changes occur AND output clearly indicates on/off

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:38`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC6: RGB light status can be queried via `rgb_lights_action=status` without changing state
- [ ] AC7: Status output clearly shows ON/OFF state for Arctic fans, CPU cooler, and RAM

### Required Components (TDD Tasks):

#### Task 4.1: Implement Status Query Action
- **Description:** Add `rgb_lights_action=status` parameter handling separate from state changes
- **Type:** Unit Test
- **Dependencies:** Task 3.1
- **Test Strategy:** Test status action routing (no state changes)
- **Status:** Pending
- **Linked Scenario:** Scenario 4

#### Task 4.2: Format Status Output for All Components
- **Description:** Parse OpenRGB output and display status for Arctic fans, CPU cooler, RAM
- **Type:** Unit Test
- **Dependencies:** Task 4.1
- **Test Strategy:** Test output formatting (clear ON/OFF indicators per component)
- **Status:** Pending
- **Linked Scenario:** Scenario 4

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 4 passes**

---

## Scenario 5: RGB Lights Persist After Reboot

**Given-When-Then:**
- **Given:** RGB control software is installed AND administrator has set RGB lights to off
- **When:** Proxmox host is rebooted
- **Then:** RGB/LED lights remain off after system boots AND RGB control software service starts automatically

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:46`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC4: RGB light state persists across system reboots
- [ ] AC14: RGB control software service is enabled and starts automatically on boot

### Required Components (TDD Tasks):

#### Task 5.1: Verify Systemd Service Auto-Start
- **Description:** Ensure systemd service created in Task 1.6 is enabled and will start on boot
- **Type:** Unit Test
- **Dependencies:** Task 1.6
- **Test Strategy:** Test systemd service enable status
- **Status:** Pending
- **Linked Scenario:** Scenario 5

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 5 passes** (Note: May require integration test with actual reboot)

---

## Scenario 6: Hardware Not Detected

**Given-When-Then:**
- **Given:** RGB control software is installed AND Arctic fans or CPU cooler are not detected by RGB control software
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off`
- **Then:** Playbook displays clear error message indicating which hardware is not detected AND provides troubleshooting guidance AND Ansible task fails with meaningful error code

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:53`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC8: When hardware is not detected, error message clearly identifies which component failed
- [ ] AC9: Error messages include troubleshooting guidance and actionable next steps
- [ ] AC13: Ansible playbook fails with meaningful error code when operations fail

### Required Components (TDD Tasks):

#### Task 6.1: Validate Hardware Detection
- **Description:** Check that expected RGB hardware is detected; fail with clear error if not
- **Type:** Unit Test
- **Dependencies:** Task 1.4
- **Test Strategy:** Test hardware validation logic and error message generation
- **Status:** Pending
- **Linked Scenario:** Scenario 6

#### Task 6.2: Add Troubleshooting Guidance to Error Messages
- **Description:** Provide actionable troubleshooting steps in error output
- **Type:** Unit Test
- **Dependencies:** Task 6.1
- **Test Strategy:** Test error message formatting includes troubleshooting guidance
- **Status:** Pending
- **Linked Scenario:** Scenario 6

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 6 passes**

---

## Scenario 7: Software Installation Failure

**Given-When-Then:**
- **Given:** No RGB control software is installed AND package repository is unavailable
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off`
- **Then:** Playbook displays clear error message about installation failure AND fails gracefully without leaving system in inconsistent state AND troubleshooting steps are provided

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:62`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC9: Error messages include troubleshooting guidance
- [ ] AC10: Installation failures leave system in consistent state (no partial configurations)
- [ ] AC13: Ansible playbook fails with meaningful error code

### Required Components (TDD Tasks):

#### Task 7.1: Handle Package Installation Failures Gracefully
- **Description:** Catch package installation errors and provide clear error messages
- **Type:** Unit Test
- **Dependencies:** Task 1.3
- **Test Strategy:** Test error handling for failed package installation
- **Status:** Pending
- **Linked Scenario:** Scenario 7

#### Task 7.2: Ensure No Partial State on Failure
- **Description:** Implement proper rollback/cleanup if installation fails partway
- **Type:** Unit Test
- **Dependencies:** Task 7.1
- **Test Strategy:** Test that failed runs leave no partial configurations
- **Status:** Pending
- **Linked Scenario:** Scenario 7

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 7 passes**

---

## Scenario 8: Using Makefile Convenience Targets

**Given-When-Then:**
- **Given:** Makefile has been configured with RGB light control targets
- **When:** Administrator runs `make proxmox-rgb-lights-off`
- **Then:** Underlying Ansible playbook is executed with `rgb_lights_state=off` AND all RGB/LED lights are turned off AND output is formatted clearly

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:71`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC11: Makefile targets correctly invoke Ansible playbook
- [ ] AC2: Lights can be turned off (via Makefile)

### Required Components (TDD Tasks):

#### Task 8.1: Create Makefile Targets for RGB Control
- **Description:** Add `proxmox-rgb-lights-off`, `proxmox-rgb-lights-on`, `proxmox-rgb-lights-status` targets to Makefile
- **Type:** Unit Test
- **Dependencies:** Task 1.5, Task 2.1, Task 4.1
- **Test Strategy:** Test Makefile targets invoke correct Ansible commands
- **Status:** Pending
- **Linked Scenario:** Scenario 8

### Scenario Completion Criteria:
- [ ] All component tests pass
- [ ] **Acceptance test for Scenario 8 passes**

---

## Implementation Order

**Outside-In Approach:**

1. **Scenario 1** (Priority: CRITICAL - foundational)
   - Tasks: 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → Verify acceptance test PASSES
   - Rationale: Establishes all core infrastructure (installation, detection, control, persistence)
   - Estimated time: ~3-4 hours

2. **Scenario 2** (Priority: HIGH - core functionality)
   - Tasks: 2.1 → 2.2 → Verify acceptance test PASSES
   - Rationale: Adds "turn on" capability (complements "turn off")
   - Estimated time: ~30 minutes

3. **Scenario 3** (Priority: HIGH - quality requirement)
   - Tasks: 3.1 → 3.2 → Verify acceptance test PASSES
   - Rationale: Ensures idempotent behavior (Ansible best practice)
   - Estimated time: ~45 minutes

4. **Scenario 4** (Priority: MEDIUM - usability)
   - Tasks: 4.1 → 4.2 → Verify acceptance test PASSES
   - Rationale: Adds status checking capability
   - Estimated time: ~30 minutes

5. **Scenario 5** (Priority: MEDIUM - validation of Scenario 1)
   - Tasks: 5.1 → Verify acceptance test PASSES
   - Rationale: Validates reboot persistence (mostly testing existing systemd service)
   - Estimated time: ~20 minutes (Note: May require actual reboot for full validation)

6. **Scenario 6** (Priority: MEDIUM - error handling)
   - Tasks: 6.1 → 6.2 → Verify acceptance test PASSES
   - Rationale: Graceful handling of missing hardware
   - Estimated time: ~45 minutes

7. **Scenario 7** (Priority: MEDIUM - error handling)
   - Tasks: 7.1 → 7.2 → Verify acceptance test PASSES
   - Rationale: Graceful handling of installation failures
   - Estimated time: ~45 minutes

8. **Scenario 8** (Priority: LOW - convenience)
   - Tasks: 8.1 → Verify acceptance test PASSES
   - Rationale: Makefile convenience wrappers
   - Estimated time: ~15 minutes

**Key Dependencies:**
- Scenarios 2-8 all depend on Scenario 1 (foundational infrastructure)
- Scenario 3 depends on Scenario 1.4 (hardware detection)
- Scenario 4 depends on Scenario 3.1 (state query)
- Scenario 5 validates Scenario 1.6 (persistence)
- Scenario 6 depends on Scenario 1.4 (hardware detection validation)
- Scenario 7 depends on Scenario 1.3 (installation error handling)
- Scenario 8 depends on Scenarios 1, 2, and 4 (all core functions)

**Total Estimated Time:** ~7-8 hours for complete implementation

---

## Progress Tracking

### Overall Progress:
- **Scenarios:** 0/8 complete (0%)
- **TDD Tasks:** 0/18 complete (0%)
- **Acceptance Tests Passing:** 0/8

### Scenario Status:
- ⏳ Scenario 1: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 2: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 3: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 4: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 5: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 6: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 7: Not started (acceptance test FAILING - outer RED ❌)
- ⏳ Scenario 8: Not started (acceptance test FAILING - outer RED ❌)

---

## Notes

### Outside-In Workflow:
For each scenario:
1. Run acceptance test → FAILS (outer RED ❌)
2. Implement component tasks via /tdd (inner RED-GREEN cycles)
3. Re-run acceptance test → PASSES (outer GREEN ✓)
4. Mark scenario complete
5. Move to next scenario

### Implementation Strategy:
- **Ansible Role Location:** `android-19-proxmox/configuration-by-ansible/host-proxmox/tasks/rgb-control.yml`
- **Defaults:** `android-19-proxmox/configuration-by-ansible/host-proxmox/defaults/main.yml` (add RGB variables)
- **Systemd Service:** Template for RGB persistence service
- **RGB Control Tool:** Use OpenRGB (better hardware support than liquidctl for Arctic products)
- **Testing Approach:** Unit tests for Ansible task structure, integration tests will use BDD acceptance tests

### Technical Decisions:
1. **OpenRGB vs liquidctl:** Choose OpenRGB (better Arctic hardware support)
2. **Persistence Method:** Systemd service that applies saved state on boot
3. **State Storage:** Save desired state in `/etc/openrgb/state.conf`
4. **Error Handling:** Use Ansible `failed_when` and `block/rescue` for graceful failures
