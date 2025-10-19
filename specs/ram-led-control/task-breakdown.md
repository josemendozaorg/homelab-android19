# Task Breakdown: RAM LED Control for Kingston HyperX Fury

**Generated:** 2025-10-19
**Total Scenarios:** 8
**Total TDD Tasks:** 15
**Implementation Strategy:** Outside-In (BDD → TDD)

---

## Scenario 1: Turn RAM LEDs Off Independently

**Given-When-Then:**
- **Given:** Proxmox host has Kingston HyperX Fury RAM with LED capability
- **And:** liquidctl is already installed (from RGB control feature)
- **And:** Arctic lights are currently ON (rainbow effect)
- **When:** Administrator runs Ansible playbook with `ram_lights_state=off`
- **Then:** RAM LEDs (led4 channel) are turned off
- **And:** Arctic lights remain ON in rainbow mode (led1, led2, led3 unchanged)
- **And:** System displays confirmation showing "RAM LEDs: OFF, Arctic lights: UNCHANGED"

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:12`
**Status:** ❌ FAILING (as expected - outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC1: RAM LED control uses existing liquidctl installation
- [ ] AC2: RAM LEDs can be turned OFF via `ram_lights_state=off` parameter
- [ ] AC8: Turning RAM LEDs off does NOT affect Arctic lights

### Required Components (TDD Tasks):

#### Task 1.1: Create Ansible tasks for RAM LED control off
- **Description:** Create ram-led-control.yml tasks file with liquidctl command targeting led4 for off state
- **Type:** Unit Test (Ansible role structure validation)
- **Dependencies:** None
- **Test Strategy:** Verify tasks file exists, contains liquidctl command for led4 with 'off' color, uses ram_lights_state variable
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.2: Add variable handling for ram_lights_state in defaults
- **Description:** Add ram_lights_state and ram_lights_enabled variables to host-proxmox defaults
- **Type:** Unit Test (defaults file validation)
- **Dependencies:** Task 1.1
- **Test Strategy:** Verify defaults/main.yml contains ram_lights_state and ram_lights_enabled with proper defaults
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.3: Include RAM LED control tasks in main playbook
- **Description:** Add ram-led-control.yml to host-proxmox/tasks/main.yml with proper conditional
- **Type:** Integration Test (playbook execution)
- **Dependencies:** Task 1.1, 1.2
- **Test Strategy:** Verify tasks are included when ram_lights_enabled is true, can execute without errors
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.4: Add confirmation output for RAM LED state changes
- **Description:** Add debug task showing RAM LED state and Arctic lights status
- **Type:** Unit Test (output validation)
- **Dependencies:** Task 1.1
- **Test Strategy:** Verify debug task exists, shows "Arctic lights: UNCHANGED" message
- **Status:** Pending
- **Linked Scenario:** Scenario 1

### Scenario Completion Criteria:
- [ ] All component unit tests pass
- [ ] All integration tests pass
- [ ] **Acceptance test for Scenario 1 passes** ← BDD validation

---

## Scenario 2: Turn RAM LEDs On Independently

**Given-When-Then:**
- **Given:** Proxmox host has Kingston HyperX Fury RAM
- **And:** RAM LEDs are currently turned off
- **And:** Arctic lights are currently OFF
- **When:** Administrator runs Ansible playbook with `ram_lights_state=on`
- **Then:** RAM LEDs (led4 channel) are turned on with rainbow effect
- **And:** Arctic lights remain OFF (led1, led2, led3 unchanged)
- **And:** System displays confirmation showing "RAM LEDs: ON, Arctic lights: UNCHANGED"

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:21`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC3: RAM LEDs can be turned ON via `ram_lights_state=on` parameter
- [ ] AC9: Turning RAM LEDs on does NOT affect Arctic lights
- [ ] AC14: Confirmation messages explicitly state "Arctic lights UNCHANGED"

### Required Components (TDD Tasks):

#### Task 2.1: Add Ansible task for RAM LED control on (rainbow)
- **Description:** Add liquidctl command for led4 with 'rainbow' color when ram_lights_state=on
- **Type:** Unit Test (task definition validation)
- **Dependencies:** Task 1.1 (reuses same file)
- **Test Strategy:** Verify task exists with liquidctl rainbow command for led4, conditional on ram_lights_state=on
- **Status:** Pending
- **Linked Scenario:** Scenario 2

### Scenario Completion Criteria:
- [ ] Component test passes
- [ ] **Acceptance test for Scenario 2 passes**

---

## Scenario 3: RAM LED State Persists After Reboot

**Given-When-Then:**
- **Given:** liquidctl is installed
- **And:** Administrator has set RAM LEDs to off
- **And:** Arctic lights are set to on
- **When:** Proxmox host is rebooted
- **Then:** RAM LEDs remain off after the system boots
- **And:** Arctic lights remain on after the system boots
- **And:** Both RGB control service and RAM control service start automatically

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:31`
**Status:** ❌ FAILING (as expected - will SKIP reboot test as too destructive)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC4: RAM LED state persists across system reboots
- [ ] AC13: RAM LED control service is enabled and starts automatically on boot

### Required Components (TDD Tasks):

#### Task 3.1: Create systemd service template for RAM LED control
- **Description:** Create ram-led-control.service.j2 template targeting led4 only
- **Type:** Unit Test (template file validation)
- **Dependencies:** Task 1.1, 2.1
- **Test Strategy:** Verify template exists, uses liquidctl for led4, references ram_lights_state variable
- **Status:** Pending
- **Linked Scenario:** Scenario 3

#### Task 3.2: Add task to deploy RAM LED control systemd service
- **Description:** Add Ansible task to deploy service template and enable it
- **Type:** Integration Test (service deployment)
- **Dependencies:** Task 3.1
- **Test Strategy:** Verify service is created, enabled, and configured correctly
- **Status:** Pending
- **Linked Scenario:** Scenario 3

### Scenario Completion Criteria:
- [ ] Service template test passes
- [ ] Service deployment test passes
- [ ] **Acceptance test for Scenario 3 passes (SKIPPED - reboot too destructive)**

---

## Scenario 4: Idempotent Operation - RAM LEDs Already Off

**Given-When-Then:**
- **Given:** liquidctl is installed
- **And:** RAM LEDs are already turned off
- **When:** Administrator runs Ansible playbook with `ram_lights_state=off` again
- **Then:** Playbook completes successfully without errors
- **And:** RAM LEDs remain off
- **And:** Ansible reports no changes made (idempotent behavior)

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:41`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC5: Running playbook multiple times produces no changes (idempotent)

### Required Components (TDD Tasks):

#### Task 4.1: Add changed_when: false to liquidctl tasks
- **Description:** Mark liquidctl tasks as unchanged since state can't be reliably queried
- **Type:** Unit Test (idempotency validation)
- **Dependencies:** Task 1.1, 2.1
- **Test Strategy:** Verify liquidctl tasks have changed_when: false, playbook runs show no changes
- **Status:** Pending
- **Linked Scenario:** Scenario 4

### Scenario Completion Criteria:
- [ ] Idempotency test passes
- [ ] **Acceptance test for Scenario 4 passes**

---

## Scenario 5: Check RAM LED Status

**Given-When-Then:**
- **Given:** liquidctl is installed
- **And:** RAM LEDs are in a known state (either on or off)
- **When:** Administrator runs Ansible playbook with `ram_lights_action=status`
- **Then:** System displays the current state of RAM LEDs
- **And:** No state changes occur to RAM or Arctic lights
- **And:** Output clearly indicates whether RAM LEDs are on or off
- **And:** Output shows Arctic lights status for comparison

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:50`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC6: RAM LED status can be queried via `ram_lights_action=status` without changing state
- [ ] AC7: Status output clearly shows RAM LED state and compares with Arctic lights status

### Required Components (TDD Tasks):

#### Task 5.1: Add status checking tasks for RAM LED
- **Description:** Create status checking logic with ram_lights_action=status variable
- **Type:** Unit Test (status task validation)
- **Dependencies:** Task 1.1, 2.1
- **Test Strategy:** Verify status tasks exist, check service status, display current state, show Arctic comparison
- **Status:** Pending
- **Linked Scenario:** Scenario 5

#### Task 5.2: Add formatted output for RAM LED status display
- **Description:** Create debug output showing RAM LED state and Arctic lights comparison
- **Type:** Unit Test (output formatting validation)
- **Dependencies:** Task 5.1
- **Test Strategy:** Verify output is clear, shows both RAM and Arctic status, formatted for readability
- **Status:** Pending
- **Linked Scenario:** Scenario 5

### Scenario Completion Criteria:
- [ ] Status checking tests pass
- [ ] Output formatting test passes
- [ ] **Acceptance test for Scenario 5 passes**

---

## Scenario 6: Using Makefile Convenience Targets

**Given-When-Then:**
- **Given:** Makefile has been configured with RAM LED control targets
- **When:** Administrator runs `make proxmox-ram-lights-off`
- **Then:** Underlying Ansible playbook is executed with `ram_lights_state=off`
- **And:** RAM LEDs are turned off
- **And:** Arctic lights remain in their current state
- **And:** Output is formatted clearly for command-line viewing

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:63`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC11: Makefile targets correctly invoke Ansible playbook
- [ ] AC12: Ansible playbook completes successfully (exit code 0)

### Required Components (TDD Tasks):

#### Task 6.1: Add Makefile targets for RAM LED control
- **Description:** Add proxmox-ram-lights-off, proxmox-ram-lights-on, proxmox-ram-lights-status targets
- **Type:** Unit Test (Makefile validation)
- **Dependencies:** Task 1.1, 2.1, 5.1
- **Test Strategy:** Verify targets exist in Makefile, invoke correct playbook with correct variables
- **Status:** Pending
- **Linked Scenario:** Scenario 6

### Scenario Completion Criteria:
- [ ] Makefile targets test passes
- [ ] **Acceptance test for Scenario 6 passes**

---

## Scenario 7: Mixed State - RAM Off, Arctic On

**Given-When-Then:**
- **Given:** liquidctl is installed
- **And:** Both RAM and Arctic lights are currently on
- **When:** Administrator runs `make proxmox-ram-lights-off`
- **And:** Verifies Arctic lights are still on
- **Then:** RAM LEDs are off
- **And:** Arctic fans, CPU cooler LEDs remain on in rainbow mode
- **And:** System can maintain this mixed state across reboots

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:70`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC10: Mixed lighting states are supported (e.g., RAM off + Arctic on)

### Required Components (TDD Tasks):

#### Task 7.1: Verify independent operation (integration test)
- **Description:** Integration test confirming RAM and Arctic lights operate independently
- **Type:** Integration Test (cross-feature validation)
- **Dependencies:** All previous tasks
- **Test Strategy:** Run both RGB and RAM playbooks, verify independence, check service states
- **Status:** Pending
- **Linked Scenario:** Scenario 7

### Scenario Completion Criteria:
- [ ] Integration test passes
- [ ] **Acceptance test for Scenario 7 passes**

---

## Scenario 8: liquidctl Not Installed - Dependency Check

**Given-When-Then:**
- **Given:** liquidctl is NOT installed on the Proxmox host
- **When:** Administrator runs Ansible playbook with `ram_lights_state=off`
- **Then:** Playbook displays clear error message indicating liquidctl is required
- **And:** Error message suggests running RGB control feature first
- **And:** Playbook fails gracefully without making changes

**Acceptance Test:** `tests/bdd/features/ram_led_control.feature:77`
**Status:** ❌ FAILING (as expected - DEFERRED for homelab use case)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC1: RAM LED control uses existing liquidctl installation (validates dependency)

### Required Components (TDD Tasks):

#### Task 8.1: Add pre-task to check liquidctl installation (DEFERRED)
- **Description:** Add pre-task that checks if liquidctl is installed and fails gracefully if not
- **Type:** Unit Test (dependency validation)
- **Dependencies:** None (independent check)
- **Test Strategy:** Verify pre-task exists, fails with helpful message if liquidctl missing
- **Status:** DEFERRED - Low priority for homelab (RGB feature already deploys liquidctl)
- **Linked Scenario:** Scenario 8

### Scenario Completion Criteria:
- [ ] Dependency check test passes (DEFERRED)
- [ ] **Acceptance test for Scenario 8 SKIPPED (deferred functionality)**

---

## Implementation Order

**Outside-In Approach:**

1. **Scenario 1** (Priority: High - foundational)
   - Task 1.1 → 1.2 → 1.3 → 1.4 → Verify acceptance test PASSES
   - Rationale: Core off functionality, establishes architecture

2. **Scenario 2** (Priority: High - complementary to Scenario 1)
   - Task 2.1 → Verify acceptance test PASSES
   - Rationale: Core on functionality, reuses Scenario 1 infrastructure

3. **Scenario 4** (Priority: High - quality assurance)
   - Task 4.1 → Verify acceptance test PASSES
   - Rationale: Ensures idempotent operation, critical for reliability

4. **Scenario 3** (Priority: High - persistence)
   - Task 3.1 → 3.2 → Verify acceptance test PASSES (SKIPPED)
   - Rationale: Persistence across reboots, builds on Scenarios 1 & 2

5. **Scenario 5** (Priority: Medium - status checking)
   - Task 5.1 → 5.2 → Verify acceptance test PASSES
   - Rationale: Status functionality, independent feature

6. **Scenario 6** (Priority: Medium - convenience)
   - Task 6.1 → Verify acceptance test PASSES
   - Rationale: Makefile targets for user convenience

7. **Scenario 7** (Priority: Low - validation)
   - Task 7.1 → Verify acceptance test PASSES
   - Rationale: Validates independent operation, integration test

8. **Scenario 8** (Priority: Deferred)
   - Task 8.1 (DEFERRED) → Acceptance test SKIPPED
   - Rationale: Error handling, low value for homelab where RGB feature is prerequisite

**Key Dependencies:**
- Scenarios 2, 3, 4 depend on Scenario 1's infrastructure
- Scenario 6 depends on Scenarios 1, 2, 5 being complete
- Scenario 7 depends on all functional scenarios (1-6)
- Scenario 8 is independent but deferred

---

## Progress Tracking

### Overall Progress:
- **Scenarios:** 0/8 complete
- **TDD Tasks:** 0/15 complete (1 deferred)
- **Acceptance Tests Passing:** 0/8

### Scenario Status:
- ⏳ Scenario 1: Not started (acceptance test FAILING)
- ⏳ Scenario 2: Not started (acceptance test FAILING)
- ⏳ Scenario 3: Not started (acceptance test FAILING - will SKIP reboot)
- ⏳ Scenario 4: Not started (acceptance test FAILING)
- ⏳ Scenario 5: Not started (acceptance test FAILING)
- ⏳ Scenario 6: Not started (acceptance test FAILING)
- ⏳ Scenario 7: Not started (acceptance test FAILING)
- ⏳ Scenario 8: Not started (DEFERRED - acceptance test will SKIP)

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

**Architecture Pattern:**
- Reuse liquidctl from RGB control feature (AC1 dependency)
- Target ONLY led4 channel (RAM RGB header)
- Keep Arctic lights (led1-led3) completely untouched
- Separate systemd service (ram-led-control.service) for independence
- Similar task structure to rgb-control.yml but RAM-specific

**Key Technical Decisions:**
- Use liquidctl --match 'ASUS' set led4 color off/rainbow
- Service type: oneshot (same as RGB control)
- Idempotency: changed_when: false (liquidctl can't query state)
- Variable naming: ram_lights_state (parallel to rgb_lights_state)
- Service independence: Both services can run concurrently

**Testing Approach:**
- Unit tests: Role structure, variable handling, task definitions
- Integration tests: Full playbook execution, service deployment
- Acceptance tests: BDD scenarios with actual hardware verification
- Deferred tests: Reboot (too destructive), error handling (low value)

**Deferred/Skipped Items:**
- Scenario 3: Reboot test skipped (too destructive for automated testing)
- Scenario 8: Error handling deferred (RGB feature is prerequisite)
- Both scenarios' acceptance tests will SKIP with explanatory messages
