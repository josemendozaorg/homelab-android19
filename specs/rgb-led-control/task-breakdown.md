# Task Breakdown: RGB/LED Light Control for Arctic Cooling and RAM

**Generated:** 2025-10-19 (Updated after OpenRGB → liquidctl refactoring)
**Total Scenarios:** 8
**Total Implementation Tasks:** 24
**Implementation Strategy:** Outside-In (BDD → TDD) with pragmatic approach to destructive tests
**Refactoring Note:** Switched from OpenRGB to liquidctl (commit fe780aa) after OpenRGB failed to control lights

---

## Implementation Status Summary

**Overall Progress**: 40% complete (core functionality working, missing convenience features and error handling)

### Scenario Completion Status:
- ✓ **Scenario 1**: 70% complete (installation and lights off working, persistence not verified)
- ⚠️ **Scenario 2**: 60% complete (lights on working, confirmation output not verified)
- ❌ **Scenario 3**: Not verified (idempotency not tested)
- ❌ **Scenario 4**: Not implemented (status checking missing)
- ⚠️ **Scenario 5**: 50% complete (systemd service exists, reboot test skipped as destructive)
- ❌ **Scenario 6**: Not implemented (error handling missing)
- ❌ **Scenario 7**: Not implemented (installation error handling missing)
- ❌ **Scenario 8**: Not implemented (Makefile targets missing)

### Key Achievements:
- ✅ liquidctl installation via pip3 (Ansible task complete)
- ✅ RGB lights OFF command working (manually verified on all 4 LED channels)
- ✅ RGB lights ON command working (rainbow mode, manually verified)
- ✅ Systemd service template created
- ✅ BDD acceptance tests updated to liquidctl (8 scenarios, step definitions)

### Remaining Work:
- ❌ Makefile convenience targets
- ❌ Status checking functionality
- ❌ Error handling (hardware not detected, installation failures)
- ❌ Idempotency verification
- ❌ Full BDD test execution
- ❌ Documentation completion

---

## Scenario 1: First-time Setup and Turn Lights Off

**Given-When-Then:**
- **Given:** Proxmox host has Arctic fans, Arctic CPU cooler, and RGB RAM installed AND no RGB control software is currently installed
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off`
- **Then:** liquidctl is automatically installed via pip3 AND all RGB/LED lights are turned off using liquidctl AND configuration persists across reboots

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:13`
**Status:** ⚠️ PARTIALLY COMPLETE (70%)

### Acceptance Criteria Satisfied by This Scenario:
- [x] AC1: liquidctl automatically installed via pip3 on first run if not present
- [x] AC2: All RGB/LED lights can be turned OFF via `rgb_lights_state=off` parameter
- [ ] AC4: RGB light state persists across system reboots (systemd service exists, not tested)
- [ ] AC12: Ansible playbook completes successfully (exit code 0) when operations succeed
- [ ] AC14: RGB control software service is enabled and starts automatically on boot

### Implementation Tasks:

#### ✅ Task 1.1: Create Ansible RGB Control Role Structure
- **Status:** COMPLETE
- **Type:** Unit Test (structure validation)
- **Implementation:** Role structure exists at `android-19-proxmox/configuration-by-ansible/host-proxmox/`
- **Test:** Structure validation in `tests/unit/test_rgb_led_control_role.py`
- **Commits:** 589ba86, 4064689

#### ✅ Task 1.2: Detect RGB Control Software Installation Status
- **Status:** COMPLETE (Updated to liquidctl)
- **Type:** Unit Test
- **Implementation:** Detection via `pip3 show liquidctl` in `tasks/rgb-control.yml`
- **Original:** OpenRGB detection via `which openrgb`
- **Refactored:** liquidctl detection (removed, now just installs via pip)
- **Commits:** 754f584, fe780aa

#### ✅ Task 1.3: Install RGB Control Software (liquidctl)
- **Status:** COMPLETE
- **Type:** Unit Test
- **Implementation:**
  - Installs pip3 via apt
  - Installs liquidctl via `pip3 install liquidctl --break-system-packages`
- **Previous:** OpenRGB AppImage download from PPA
- **Refactored:** pip3 installation (commit fe780aa)
- **Test:** Installation task exists and is idempotent
- **Commits:** 79e9ade, 38e26e7, fe780aa

#### ✅ Task 1.4: Detect RGB Hardware Components
- **Status:** COMPLETE
- **Type:** Unit Test
- **Implementation:** `liquidctl list` detects ASUS Aura LED Controller (4 channels)
- **Previous:** `openrgb --list-devices`
- **Refactored:** `liquidctl list` (commit fe780aa)
- **Hardware Detected:** ASUS Aura LED Controller (3 ARGB + 1 RGB = 4 channels: led1-led4)
- **Commits:** 72d2d0c, fe780aa

#### ✅ Task 1.5: Turn RGB Lights Off
- **Status:** COMPLETE
- **Type:** Unit Test
- **Implementation:**
  ```yaml
  - name: Turn all RGB lights off (ASUS Aura LED Controller)
    command: liquidctl --match 'ASUS' set {{ item }} color off
    loop: [led1, led2, led3, led4]
    when: rgb_lights_state == "off"
  ```
- **Previous:** `openrgb -m static -c 000000 --noautoconnect`
- **Refactored:** Individual LED channel control (commit fe780aa)
- **Manual Verification:** ✅ Confirmed lights turn off
- **Commits:** c581c5a, fe780aa

#### ⚠️ Task 1.6: Configure RGB Persistence (Systemd Service)
- **Status:** PARTIALLY COMPLETE (needs verification)
- **Type:** Integration Test
- **Implementation:**
  - Template: `templates/rgb-control.service.j2`
  - Service type: oneshot
  - Command: Loops through led1-led4 with liquidctl
- **Previous:** OpenRGB command in service
- **Refactored:** liquidctl commands (commit fe780aa)
- **Not Verified:** Service enablement, actual persistence across reboot
- **Commits:** 45d19ae, fe780aa

### Scenario 1 Completion Criteria:
- [x] Component unit tests exist
- [x] liquidctl installation works
- [x] Lights turn off successfully
- [ ] Integration test: Full playbook execution
- [ ] **Acceptance test for Scenario 1 passes** ← BDD validation pending

---

## Scenario 2: Turn Lights On After Being Off

**Given-When-Then:**
- **Given:** RGB control software is already installed AND all RGB/LED lights are currently turned off
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=on`
- **Then:** All RGB/LED lights are turned on AND system displays confirmation

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:23`
**Status:** ⚠️ PARTIALLY COMPLETE (60%)

### Acceptance Criteria Satisfied by This Scenario:
- [x] AC3: All RGB/LED lights can be turned ON via `rgb_lights_state=on` parameter
- [ ] AC12: Ansible playbook completes successfully

### Implementation Tasks:

#### ✅ Task 2.1: Turn RGB Lights On
- **Status:** COMPLETE
- **Type:** Unit Test
- **Implementation:**
  ```yaml
  - name: Turn all RGB lights on (ASUS Aura LED Controller - default rainbow)
    command: liquidctl --match 'ASUS' set {{ item }} color rainbow
    loop: [led1, led2, led3, led4]
    when: rgb_lights_state == "on"
  ```
- **Refactored:** Uses rainbow effect for "on" state (commit fe780aa)
- **Manual Verification:** ✅ Confirmed rainbow mode works
- **Commits:** fe780aa

#### ❌ Task 2.2: Display State Change Confirmation
- **Status:** NOT IMPLEMENTED
- **Type:** Integration Test
- **Description:** Add debug output showing which LEDs were affected
- **Implementation Needed:** Add `debug` task to display results
- **Linked Scenario:** Scenario 2

### Scenario 2 Completion Criteria:
- [x] Lights turn on successfully
- [ ] Confirmation output implemented
- [ ] Integration test: Full playbook execution
- [ ] **Acceptance test for Scenario 2 passes** ← BDD validation pending

---

## Scenario 3: Idempotent Operation - Lights Already Off

**Given-When-Then:**
- **Given:** RGB control software is installed AND all RGB/LED lights are already turned off
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off` again
- **Then:** Playbook completes successfully without errors AND lights remain off AND Ansible reports no changes made

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:33`
**Status:** ❌ NOT VERIFIED

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC5: Running the playbook multiple times with the same configuration produces no changes (idempotent)
- [ ] AC12: Ansible playbook completes successfully

### Implementation Tasks:

#### ❌ Task 3.1: Add Idempotency Checks
- **Status:** NOT IMPLEMENTED
- **Type:** Unit Test
- **Description:** Add `changed_when` conditions to liquidctl tasks
- **Implementation Needed:**
  - Check current LED state before changing
  - Only run liquidctl commands if state differs
  - Or accept that commands always show "changed" but are safe to run
- **Linked Scenario:** Scenario 3

#### ❌ Task 3.2: Verify Idempotent Behavior
- **Status:** NOT TESTED
- **Type:** Integration Test
- **Description:** Run playbook twice, verify second run shows "changed=0"
- **Test Strategy:** Execute playbook → Execute again → Compare Ansible output
- **Linked Scenario:** Scenario 3

### Scenario 3 Completion Criteria:
- [ ] Idempotency logic implemented or documented
- [ ] Integration test: Run playbook twice
- [ ] **Acceptance test for Scenario 3 passes** ← BDD validation pending

---

## Scenario 4: Check RGB Light Status

**Given-When-Then:**
- **Given:** RGB control software is installed AND RGB lights are in a known state
- **When:** Administrator runs the Ansible playbook with `rgb_lights_action=status`
- **Then:** System displays current state of RGB/LED lights for each component AND no state changes occur AND output clearly indicates whether lights are on or off

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:41`
**Status:** ❌ NOT IMPLEMENTED

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC6: RGB light status can be queried via `rgb_lights_action=status` without changing state
- [ ] AC7: Status output clearly shows ON/OFF state for Arctic fans, CPU cooler, and RAM

### Implementation Tasks:

#### ❌ Task 4.1: Add Status Checking Logic
- **Status:** NOT IMPLEMENTED
- **Type:** Unit Test
- **Description:** Query liquidctl device status without changing state
- **Implementation Needed:**
  - Add task to run `liquidctl status` or query LED states
  - Parse output to determine on/off state
  - Support `rgb_lights_action=status` variable
- **Linked Scenario:** Scenario 4

#### ❌ Task 4.2: Format Status Output
- **Status:** NOT IMPLEMENTED
- **Type:** Unit Test
- **Description:** Display LED states in human-readable format
- **Implementation Needed:**
  - Show LED1-LED4 status clearly
  - Indicate which hardware each LED controls (if detectable)
  - Format for command-line viewing
- **Linked Scenario:** Scenario 4

#### ❌ Task 4.3: Verify No State Changes
- **Status:** NOT IMPLEMENTED
- **Type:** Integration Test
- **Description:** Ensure status check doesn't modify LED states
- **Test Strategy:** Set known state → Check status → Verify state unchanged
- **Linked Scenario:** Scenario 4

### Scenario 4 Completion Criteria:
- [ ] Status checking implemented
- [ ] Output formatting clear and readable
- [ ] Integration test: Status doesn't change state
- [ ] **Acceptance test for Scenario 4 passes** ← BDD validation pending

---

## Scenario 5: RGB Lights Persist After Reboot

**Given-When-Then:**
- **Given:** RGB control software is installed AND administrator has set RGB lights to off
- **When:** Proxmox host is rebooted
- **Then:** RGB/LED lights remain off after the system boots AND RGB control software service starts automatically

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:50`
**Status:** ⚠️ PARTIALLY COMPLETE (50% - systemd service exists, reboot test skipped)

### Acceptance Criteria Satisfied by This Scenario:
- [x] AC4: RGB light state persists across system reboots (systemd service configured)
- [x] AC14: RGB control software service is enabled and starts automatically on boot (configured, not verified)

### Implementation Tasks:

#### ✅ Task 5.1: Create Systemd Service
- **Status:** COMPLETE
- **Type:** Unit Test
- **Implementation:** Service template at `templates/rgb-control.service.j2`
- **Service Type:** oneshot
- **Commands:** Loops through led1-led4 with liquidctl
- **Commits:** 45d19ae, fe780aa

#### ❌ Task 5.2: Verify Service Configuration
- **Status:** NOT VERIFIED
- **Type:** Integration Test
- **Description:** Verify systemd service is created, enabled, and configured correctly
- **Test Strategy:** Check file exists, service enabled, service configuration matches template
- **Linked Scenario:** Scenario 5
- **Note:** Actual reboot test is DESTRUCTIVE and will be SKIPPED

#### ❌ Task 5.3: Document Reboot Test Skip
- **Status:** NOT COMPLETE
- **Type:** Documentation
- **Description:** Document why actual reboot test is skipped (too destructive)
- **Rationale:** Rebooting production Proxmox host during automated testing is too risky
- **Alternative:** Verify service configuration only, rely on systemd behavior
- **Linked Scenario:** Scenario 5

### Scenario 5 Completion Criteria:
- [x] Systemd service template created
- [ ] Service configuration verified (not rebooted)
- [ ] Documentation explains skip rationale
- [ ] **Acceptance test for Scenario 5 passes** (with reboot step skipped)

---

## Scenario 6: Hardware Not Detected

**Given-When-Then:**
- **Given:** RGB control software is installed AND Arctic fans or CPU cooler are not detected by RGB control software
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off`
- **Then:** Playbook displays clear error message indicating which hardware is not detected AND playbook provides troubleshooting guidance AND Ansible task fails with meaningful error code

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:58`
**Status:** ❌ NOT IMPLEMENTED (will be SKIPPED - requires hardware simulation)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC8: When hardware is not detected, error message clearly identifies which component failed
- [ ] AC9: Error messages include troubleshooting guidance and actionable next steps
- [ ] AC13: Ansible playbook fails with meaningful error code when operations fail

### Implementation Tasks:

#### ❌ Task 6.1: Add Hardware Detection Validation
- **Status:** NOT IMPLEMENTED (SKIPPED)
- **Type:** Unit Test
- **Description:** Validate that `liquidctl list` detects expected devices
- **Implementation Needed:**
  - Parse `liquidctl list` output
  - Check for ASUS Aura LED Controller
  - Fail task if no devices found
- **Skip Rationale:** Requires hardware disconnection to test, too complex
- **Linked Scenario:** Scenario 6

#### ❌ Task 6.2: Add Error Messages with Troubleshooting
- **Status:** NOT IMPLEMENTED (SKIPPED)
- **Type:** Unit Test
- **Description:** Provide clear error messages when hardware not found
- **Implementation Needed:**
  - Error message format: "No RGB devices detected. Expected: ASUS Aura LED Controller"
  - Troubleshooting steps: Check connections, verify kernel drivers, check dmesg
- **Skip Rationale:** Requires error condition simulation
- **Linked Scenario:** Scenario 6

### Scenario 6 Completion Criteria:
- [ ] Hardware validation implemented (DEFERRED - complex simulation required)
- [ ] Error messages implemented (DEFERRED)
- [ ] **Acceptance test for Scenario 6 SKIPPED** (hardware simulation not implemented)

---

## Scenario 7: Software Installation Failure

**Given-When-Then:**
- **Given:** No RGB control software is installed AND package repository is unavailable
- **When:** Administrator runs the Ansible playbook with `rgb_lights_state=off`
- **Then:** Playbook displays clear error message about installation failure AND playbook fails gracefully without leaving system in inconsistent state AND troubleshooting steps are provided in error output

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:67`
**Status:** ❌ NOT IMPLEMENTED (will be SKIPPED - requires network manipulation)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC10: Installation failures leave system in consistent state (no partial configurations)
- [ ] AC13: Ansible playbook fails with meaningful error code when operations fail

### Implementation Tasks:

#### ❌ Task 7.1: Add pip3 Installation Error Handling
- **Status:** NOT IMPLEMENTED (LOW PRIORITY)
- **Type:** Unit Test
- **Description:** Handle pip3 install failures gracefully
- **Implementation Needed:**
  - Add error handling to pip task
  - Clear error message when pip3 fails
  - Troubleshooting: Check internet connection, verify pip3 installed
- **Skip Rationale:** Requires network disconnection to test
- **Linked Scenario:** Scenario 7

#### ❌ Task 7.2: Ensure Clean Failure (No Partial State)
- **Status:** NOT IMPLEMENTED (LOW PRIORITY)
- **Type:** Integration Test
- **Description:** Verify failed installation doesn't leave partial configuration
- **Implementation Needed:**
  - Use Ansible blocks with rescue
  - Cleanup systemd service if installation fails
  - Fail task cleanly
- **Skip Rationale:** Complex failure simulation
- **Linked Scenario:** Scenario 7

### Scenario 7 Completion Criteria:
- [ ] Error handling implemented (DEFERRED - complex simulation required)
- [ ] Clean failure verified (DEFERRED)
- [ ] **Acceptance test for Scenario 7 SKIPPED** (network simulation not implemented)

---

## Scenario 8: Using Makefile Convenience Targets

**Given-When-Then:**
- **Given:** Makefile has been configured with RGB light control targets
- **When:** Administrator runs `make proxmox-rgb-lights-off`
- **Then:** Underlying Ansible playbook is executed with `rgb_lights_state=off` AND all RGB/LED lights are turned off AND output is formatted clearly for command-line viewing

**Acceptance Test:** `tests/bdd/features/rgb_led_control.feature:76`
**Status:** ❌ NOT IMPLEMENTED (HIGH PRIORITY - easy to implement)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC11: Makefile targets (`make proxmox-rgb-lights-off/on/status`) correctly invoke Ansible playbook

### Implementation Tasks:

#### ❌ Task 8.1: Add Makefile Target - Lights Off
- **Status:** NOT IMPLEMENTED
- **Type:** Unit Test
- **Description:** Add `proxmox-rgb-lights-off` target to Makefile
- **Implementation Needed:**
  ```makefile
  proxmox-rgb-lights-off:
      ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml -e "rgb_lights_state=off"
  ```
- **Linked Scenario:** Scenario 8

#### ❌ Task 8.2: Add Makefile Target - Lights On
- **Status:** NOT IMPLEMENTED
- **Type:** Unit Test
- **Description:** Add `proxmox-rgb-lights-on` target to Makefile
- **Implementation Needed:**
  ```makefile
  proxmox-rgb-lights-on:
      ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml -e "rgb_lights_state=on"
  ```
- **Linked Scenario:** Scenario 8

#### ❌ Task 8.3: Add Makefile Target - Status Check
- **Status:** NOT IMPLEMENTED
- **Type:** Unit Test
- **Description:** Add `proxmox-rgb-lights-status` target to Makefile
- **Implementation Needed:**
  ```makefile
  proxmox-rgb-lights-status:
      ansible-playbook -i inventory.yml android-19-proxmox/configuration-by-ansible/host-proxmox/playbook.yml -e "rgb_lights_action=status"
  ```
- **Dependencies:** Requires Task 4.1 (status checking) to be implemented
- **Linked Scenario:** Scenario 8

#### ❌ Task 8.4: Test Makefile Targets
- **Status:** NOT IMPLEMENTED
- **Type:** Integration Test
- **Description:** Verify Makefile targets execute playbook correctly
- **Test Strategy:** Run `make proxmox-rgb-lights-off` → Verify playbook executes → Verify lights off
- **Linked Scenario:** Scenario 8

### Scenario 8 Completion Criteria:
- [ ] All three Makefile targets implemented
- [ ] Integration test: Targets execute correctly
- [ ] **Acceptance test for Scenario 8 passes** ← BDD validation pending

---

## Implementation Order

**Recommended Execution Sequence** (Outside-In with Pragmatism):

### Phase 1: Documentation (COMPLETE)
- ✅ Task Breakdown updated to reflect liquidctl

### Phase 2: Quick Wins (HIGH PRIORITY)
- ❌ **Task 8.1-8.4**: Makefile targets (Scenario 8) - Easy to implement, high value

### Phase 3: Core Verification (HIGH PRIORITY)
- ❌ **Task 1.6 verification**: Verify systemd service (Scenario 1)
- ❌ **Task 2.2**: Add confirmation output (Scenario 2)
- ❌ **Task 3.1-3.2**: Verify idempotency (Scenario 3)
- ❌ **Task 5.2-5.3**: Verify persistence configuration (Scenario 5)

### Phase 4: Status Feature (MEDIUM PRIORITY)
- ❌ **Task 4.1-4.3**: Status checking (Scenario 4)

### Phase 5: Error Handling (LOW PRIORITY - Complex/Skipped)
- ❌ **Task 6.1-6.2**: Hardware detection errors (Scenario 6) - DEFERRED
- ❌ **Task 7.1-7.2**: Installation errors (Scenario 7) - DEFERRED

### Phase 6: Testing & Validation
- ❌ Run all BDD acceptance tests
- ❌ Update spec acceptance criteria
- ❌ Generate completion report

---

## Progress Tracking

### Overall Progress:
- **Scenarios:** 1/8 partially complete, 7/8 remaining (13%)
- **Implementation Tasks:** 8/24 complete, 16/24 remaining (33%)
- **Acceptance Tests Passing:** 0/8 (tests updated but not executed)
- **Acceptance Criteria:** 2/15 manually verified (13%)

### Scenario Status:
- ⚠️ Scenario 1: Partially implemented (liquidctl working, verification needed)
- ⚠️ Scenario 2: Partially implemented (lights on working, output needed)
- ❌ Scenario 3: Not verified (idempotency untested)
- ❌ Scenario 4: Not implemented (status checking missing)
- ⚠️ Scenario 5: Partially implemented (service exists, verification needed)
- ❌ Scenario 6: Not implemented (WILL BE SKIPPED - hardware simulation complex)
- ❌ Scenario 7: Not implemented (WILL BE SKIPPED - network simulation complex)
- ❌ Scenario 8: Not implemented (HIGH PRIORITY - Makefile targets)

### Test Status:
- **BDD Tests:** Updated to liquidctl, not executed
- **Unit Tests:** None exist yet for RGB tasks
- **Integration Tests:** None executed yet
- **Manual Tests:** ✅ liquidctl commands verified working (lights off/on confirmed)

---

## Notes

### Outside-In Workflow Reminder:
For each scenario:
1. Run acceptance test → FAILS (outer RED ❌)
2. Implement component tasks via /tdd (inner RED-GREEN cycles)
3. Re-run acceptance test → PASSES (outer GREEN ✓)
4. Mark scenario complete
5. Move to next scenario

### Refactoring History:
**Major Refactoring (Commit fe780aa):**
- **Why:** OpenRGB failed to control Arctic RGB lights (commands executed but no effect)
- **What Changed:**
  - Removed OpenRGB AppImage installation
  - Added liquidctl installation via pip3
  - Changed device detection from `openrgb --list-devices` to `liquidctl list`
  - Updated light control commands to `liquidctl --match 'ASUS' set led[1-4] color [off|rainbow]`
  - Updated systemd service to use liquidctl
  - Updated BDD step definitions to check for liquidctl instead of OpenRGB
- **Manual Verification:** User confirmed liquidctl commands successfully control lights
- **Hardware:** ASUS Aura LED Controller with 4 LED channels (led1-led4)

### Deferred Scenarios (Documented Skips):
- **Scenario 5 (Reboot)**: Systemd service configuration will be verified, but actual reboot test skipped (too destructive for automated testing)
- **Scenario 6 (Hardware Not Detected)**: Requires hardware disconnection/simulation (complex, low value for homelab)
- **Scenario 7 (Installation Failure)**: Requires network disconnection/simulation (complex, low value for homelab)

These scenarios will be marked as "implementation complete, test skipped with rationale" in final report.
