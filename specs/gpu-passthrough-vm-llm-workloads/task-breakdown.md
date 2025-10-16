# Task Breakdown: GPU-Passthrough Ubuntu VM for AI/LLM Workloads

**Generated:** 2025-10-16
**Total Scenarios:** 9
**Total TDD Tasks:** 26
**Implementation Strategy:** Outside-In (BDD → TDD)

**Implementation Decisions:**
- CUDA: ubuntu-drivers auto-select with CUDA 12.6/12.7+ compatibility verification
- Services: Auto-start enabled (systemd with Restart=on-failure)
- Network: vLLM binds to private IP (192.168.0.140:8000) - local network accessible

---

## Scenario 9: Infrastructure Catalog Integration
**Priority:** HIGHEST (Foundation - must be first)
**Rationale:** All other scenarios depend on VM definition existing in catalog

**Given-When-Then:**
- **Given:** A new VM definition needs to be added
- **When:** The administrator adds vm-llm-aimachine to infrastructure-catalog.yml
- **Then:** The catalog includes VM ID, name, CPU, RAM, disk specifications
- **And:** GPU passthrough device ID is specified
- **And:** Ubuntu Server ISO path is referenced
- **And:** The catalog validates successfully (YAML syntax)
- **And:** Terraform can read and parse the catalog
- **And:** The VM can be provisioned from catalog definition

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:159`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-8: VM is added to infrastructure-catalog.yml with all specifications

### Required Components (TDD Tasks):

#### Task 9.1: Add VM Definition to Infrastructure Catalog
- **Description:** Add VM ID 140 entry to infrastructure-catalog.yml with GPU passthrough config
- **Type:** Configuration
- **Dependencies:** None
- **Test Strategy:**
  - Unit test: YAML syntax validation
  - Unit test: Required fields present (id, name, ip, type, resources, gpu_passthrough)
  - Unit test: VM ID 140 not conflicting with existing IDs
- **Status:** Pending
- **Linked Scenario:** Scenario 9

#### Task 9.2: Create Terraform Variables for GPU Passthrough
- **Description:** Define Terraform variables for GPU device ID and passthrough configuration
- **Type:** Infrastructure Code
- **Dependencies:** Task 9.1
- **Test Strategy:**
  - Unit test: Variable definitions are valid HCL
  - Unit test: GPU device ID variable has appropriate type/description
- **Status:** Pending
- **Linked Scenario:** Scenario 9

### Scenario Completion Criteria:
- [ ] infrastructure-catalog.yml updated with VM 140
- [ ] YAML validates successfully
- [ ] Terraform variables defined for GPU passthrough
- [ ] **Acceptance test for Scenario 9 passes** ← BDD validation

---

## Scenario 1: Initial VM Deployment (Happy Path)
**Priority:** HIGH (Core deployment flow)
**Rationale:** Primary use case - complete end-to-end deployment

**Given-When-Then:**
- **Given:** Proxmox host configured with GPU passthrough, Ubuntu Server ISO available, infrastructure-catalog.yml includes vm-llm-aimachine
- **When:** Administrator runs `make deploy-vm-llm-aimachine`
- **Then:** Terraform creates VM with ID 140 (32 cores, 50GB RAM, 500GB disk), GPU passthrough configured, cloud-init sets up SSH keys, VM starts, Ansible connects, NVIDIA drivers installed, vLLM and Ollama installed, deployment completes successfully

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:78`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-1: VM with ID 140 created on Proxmox
- [ ] AC-2: VM has 32 CPU cores
- [ ] AC-3: VM has 50GB RAM
- [ ] AC-4: VM has 500GB disk
- [ ] AC-5: GPU passthrough configured
- [ ] AC-6: VM uses Ubuntu Server ISO
- [ ] AC-7: cloud-init configured
- [ ] AC-9: Terraform validates
- [ ] AC-10: NVIDIA drivers installed
- [ ] AC-17: vLLM installed
- [ ] AC-22: Ollama installed
- [ ] AC-27: Makefile target exists
- [ ] AC-28: Deployment completes successfully

### Required Components (TDD Tasks):

#### Task 1.1: Create Terraform VM Resource with GPU Passthrough
- **Description:** Create main.tf resource for QEMU VM with hostpci GPU passthrough
- **Type:** Infrastructure Code
- **Dependencies:** Task 9.1, Task 9.2
- **Test Strategy:**
  - Unit test: Terraform syntax validation
  - Unit test: VM resource has correct CPU/RAM/disk configuration
  - Unit test: hostpci block references GPU device correctly
  - Unit test: cloud-init configuration present
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.2: Create Ansible Role Structure (vm-llm-aimachine)
- **Description:** Create Ansible role directory structure following naming conventions
- **Type:** Configuration Management
- **Dependencies:** None
- **Test Strategy:**
  - Unit test: Role directory exists at correct path
  - Unit test: Standard role subdirectories present (tasks, defaults, handlers, templates)
  - Unit test: Role follows naming convention (vm-*)
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.3: Implement NVIDIA Driver Installation Tasks
- **Description:** Create Ansible tasks to install NVIDIA drivers using ubuntu-drivers
- **Type:** Configuration Management
- **Dependencies:** Task 1.2
- **Test Strategy:**
  - Unit test: Task file exists and has valid YAML
  - Unit test: ubuntu-drivers devices command task present
  - Unit test: Driver installation task present with open-distro selection
  - Integration test: Idempotent re-run (no changes)
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.4: Implement vLLM Installation Tasks
- **Description:** Create Ansible tasks to install vLLM in Python virtual environment
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:**
  - Unit test: Task creates Python venv
  - Unit test: Task installs vLLM via pip
  - Unit test: vLLM systemd service template exists
  - Unit test: Service binds to 192.168.0.140:8000
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.5: Implement Ollama Installation Tasks
- **Description:** Create Ansible tasks to install Ollama binary and systemd service
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:**
  - Unit test: Ollama download/install task present
  - Unit test: Ollama systemd service template exists
  - Unit test: Service enabled for auto-start
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.6: Create Makefile Deployment Target
- **Description:** Create deploy-vm-llm-aimachine Makefile target orchestrating Terraform + Ansible
- **Type:** Orchestration
- **Dependencies:** Task 1.1, Task 1.2
- **Test Strategy:**
  - Unit test: Target exists in Makefile
  - Unit test: Target calls terraform apply
  - Unit test: Target calls ansible-playbook
  - Unit test: Target includes validation steps
- **Status:** Pending
- **Linked Scenario:** Scenario 1

### Scenario Completion Criteria:
- [ ] Terraform creates VM successfully
- [ ] Ansible configures VM successfully
- [ ] NVIDIA drivers installed and verified
- [ ] vLLM installed and service configured
- [ ] Ollama installed and service configured
- [ ] Makefile target works end-to-end
- [ ] **Acceptance test for Scenario 1 passes** ← BDD validation

---

## Scenario 2: GPU Passthrough Verification
**Priority:** HIGH (Critical functionality validation)
**Rationale:** Must verify GPU is accessible and functional

**Given-When-Then:**
- **Given:** VM provisioned with GPU passthrough, NVIDIA drivers installed
- **When:** Administrator runs `nvidia-smi` inside VM
- **Then:** Output shows ZOTAC RTX 5060Ti with 16GB memory, driver version displayed, no dmesg errors, CUDA functional

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:92`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-11: nvidia-smi executes and shows RTX 5060Ti
- [ ] AC-12: nvidia-smi shows 16GB GPU memory
- [ ] AC-13: GPU driver version displayed
- [ ] AC-14: No NVIDIA errors in dmesg
- [ ] AC-15: CUDA toolkit installed (nvcc works)
- [ ] AC-16: GPU visible in lspci

### Required Components (TDD Tasks):

#### Task 2.1: Implement CUDA Toolkit Installation
- **Description:** Add Ansible tasks to install CUDA toolkit 12.6+
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:**
  - Unit test: CUDA repository configuration present
  - Unit test: CUDA toolkit package installation task
  - Unit test: nvcc verification task exists
- **Status:** Pending
- **Linked Scenario:** Scenario 2

#### Task 2.2: Create GPU Verification Tasks
- **Description:** Add Ansible tasks to verify GPU visibility and functionality
- **Type:** Configuration Management
- **Dependencies:** Task 1.3, Task 2.1
- **Test Strategy:**
  - Unit test: nvidia-smi verification task exists
  - Unit test: dmesg NVIDIA error check task exists
  - Unit test: lspci GPU detection task exists
- **Status:** Pending
- **Linked Scenario:** Scenario 2

### Scenario Completion Criteria:
- [ ] CUDA toolkit installed
- [ ] nvidia-smi shows GPU correctly
- [ ] No dmesg errors
- [ ] **Acceptance test for Scenario 2 passes** ← BDD validation

---

## Scenario 3: NVIDIA Driver Installation with Open-Distro Version
**Priority:** MEDIUM (Specific driver version validation)
**Rationale:** Validates correct driver selection method

**Given-When-Then:**
- **Given:** VM running Ubuntu Server, GPU visible via PCIe
- **When:** Ansible executes driver installation tasks
- **Then:** ubuntu-drivers devices lists drivers, *-open - distro selected, installed successfully, no reboot needed, nvidia-smi available

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:101`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-10: NVIDIA drivers installed via ubuntu-drivers (open-distro)

### Required Components (TDD Tasks):

#### Task 3.1: Implement Driver Selection Logic
- **Description:** Add logic to Ansible tasks to select open-distro driver version
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:**
  - Unit test: Task detects available drivers
  - Unit test: Task selects *-open version when available
  - Unit test: Task handles case when open version unavailable
- **Status:** Pending
- **Linked Scenario:** Scenario 3

### Scenario Completion Criteria:
- [ ] ubuntu-drivers detects GPU
- [ ] Open-distro driver selected
- [ ] Driver installation verified
- [ ] **Acceptance test for Scenario 3 passes** ← BDD validation

---

## Scenario 4: vLLM Service Deployment
**Priority:** HIGH (Core AI service)
**Rationale:** Primary LLM inference capability

**Given-When-Then:**
- **Given:** NVIDIA drivers and CUDA installed, Python venv configured
- **When:** Ansible installs and configures vLLM
- **Then:** vLLM installed in venv, API server can start, health endpoint responds, vLLM detects GPU

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:111`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-17: vLLM in Python venv
- [ ] AC-18: vLLM API server starts
- [ ] AC-19: Health endpoint responds
- [ ] AC-20: vLLM uses GPU
- [ ] AC-21: vLLM systemd service exists

### Required Components (TDD Tasks):

#### Task 4.1: Create vLLM Systemd Service Template
- **Description:** Create Jinja2 template for vLLM systemd service file
- **Type:** Configuration Management
- **Dependencies:** Task 1.4
- **Test Strategy:**
  - Unit test: Template file exists
  - Unit test: Template has correct systemd structure
  - Unit test: Service binds to correct IP:port (192.168.0.140:8000)
  - Unit test: Service has Restart=on-failure
  - Unit test: Service enabled (WantedBy=multi-user.target)
- **Status:** Pending
- **Linked Scenario:** Scenario 4

#### Task 4.2: Add vLLM Service Health Check
- **Description:** Add Ansible tasks to verify vLLM health endpoint
- **Type:** Configuration Management
- **Dependencies:** Task 4.1
- **Test Strategy:**
  - Unit test: Health check task exists
  - Unit test: Task curls http://192.168.0.140:8000/health
  - Unit test: Task validates 200 response
- **Status:** Pending
- **Linked Scenario:** Scenario 4

### Scenario Completion Criteria:
- [ ] vLLM service configured
- [ ] Service auto-starts
- [ ] Health endpoint accessible
- [ ] **Acceptance test for Scenario 4 passes** ← BDD validation

---

## Scenario 5: Ollama Installation and Verification
**Priority:** HIGH (Core AI service)
**Rationale:** Model management and local inference

**Given-When-Then:**
- **Given:** VM has NVIDIA drivers installed
- **When:** Ansible installs Ollama
- **Then:** Ollama CLI in PATH, version command works, service running, list command works, GPU detected

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:120`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-22: Ollama in PATH
- [ ] AC-23: ollama --version works
- [ ] AC-24: Ollama service running
- [ ] AC-25: ollama list works
- [ ] AC-26: Ollama uses GPU

### Required Components (TDD Tasks):

#### Task 5.1: Create Ollama Systemd Service Template
- **Description:** Create Jinja2 template for Ollama systemd service file
- **Type:** Configuration Management
- **Dependencies:** Task 1.5
- **Test Strategy:**
  - Unit test: Template file exists
  - Unit test: Service runs as non-root user
  - Unit test: Service has Restart=on-failure
  - Unit test: Service enabled for auto-start
- **Status:** Pending
- **Linked Scenario:** Scenario 5

#### Task 5.2: Add Ollama Verification Tasks
- **Description:** Add Ansible tasks to verify Ollama installation and GPU access
- **Type:** Configuration Management
- **Dependencies:** Task 5.1
- **Test Strategy:**
  - Unit test: ollama version check task exists
  - Unit test: ollama list verification task exists
  - Unit test: GPU detection verification present
- **Status:** Pending
- **Linked Scenario:** Scenario 5

### Scenario Completion Criteria:
- [ ] Ollama binary installed
- [ ] Ollama service auto-starts
- [ ] CLI commands functional
- [ ] **Acceptance test for Scenario 5 passes** ← BDD validation

---

## Scenario 6: Idempotent Re-deployment
**Priority:** MEDIUM (Best practice validation)
**Rationale:** Ensures Ansible/Terraform idempotency

**Given-When-Then:**
- **Given:** VM exists and configured, services running
- **When:** Administrator runs make deploy-vm-llm-aimachine again
- **Then:** Terraform makes no changes, Ansible idempotent, no service disruption, GPU still works, deployment succeeds

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:129`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] AC-29: Deployment is idempotent

### Required Components (TDD Tasks):

#### Task 6.1: Add Idempotency Tests to Ansible Tasks
- **Description:** Ensure all Ansible tasks are idempotent (check-mode compatible)
- **Type:** Configuration Management
- **Dependencies:** All previous Ansible tasks
- **Test Strategy:**
  - Unit test: Run each task twice, verify no changes second time
  - Integration test: Full playbook re-run shows "ok" not "changed"
- **Status:** Pending
- **Linked Scenario:** Scenario 6

### Scenario Completion Criteria:
- [ ] Terraform detects no changes
- [ ] Ansible shows no changes on re-run
- [ ] Services remain running
- [ ] **Acceptance test for Scenario 6 passes** ← BDD validation

---

## Scenario 7: GPU Passthrough Failure Detection
**Priority:** LOW (Error handling)
**Rationale:** Validates error handling when GPU unavailable

**Given-When-Then:**
- **Given:** Proxmox host has GPU passthrough enabled, VM being provisioned
- **When:** GPU passthrough fails (device busy/unavailable)
- **Then:** Terraform reports clear error, VM rolled back, actionable error info, no partial VM

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:139`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] (NFR-23): Failed deployments roll back cleanly

### Required Components (TDD Tasks):

#### Task 7.1: Add Terraform Error Handling for GPU Passthrough
- **Description:** Improve Terraform error messages for GPU passthrough failures
- **Type:** Infrastructure Code
- **Dependencies:** Task 1.1
- **Test Strategy:**
  - Unit test: Error message includes GPU device ID
  - Unit test: Error suggests checking GPU availability
  - Integration test: Simulated failure produces helpful error
- **Status:** Pending
- **Linked Scenario:** Scenario 7

### Scenario Completion Criteria:
- [ ] Error messages are clear
- [ ] Failed VMs are cleaned up
- [ ] **Acceptance test for Scenario 7 passes** ← BDD validation

---

## Scenario 8: NVIDIA Driver Installation Failure Handling
**Priority:** LOW (Error handling)
**Rationale:** Validates graceful failure when driver install fails

**Given-When-Then:**
- **Given:** VM provisioned, Ansible begins driver installation
- **When:** Driver installation fails (kernel mismatch, missing deps)
- **Then:** Ansible reports failure clearly, playbook stops at failed task, error logs shown, VM accessible for debug, re-run after fix succeeds

**Acceptance Test:** `tests/bdd/features/vm_llm_gpu_passthrough.feature:148`
**Status:** ❌ FAILING (outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] (NFR-15): Error messages provide clear guidance

### Required Components (TDD Tasks):

#### Task 8.1: Add Error Handling to Driver Installation
- **Description:** Add Ansible error handling with clear failure messages
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:**
  - Unit test: Failed tasks have rescue blocks
  - Unit test: Error messages include troubleshooting steps
  - Integration test: Simulated failure produces helpful output
- **Status:** Pending
- **Linked Scenario:** Scenario 8

### Scenario Completion Criteria:
- [ ] Errors are descriptive
- [ ] VM remains accessible
- [ ] **Acceptance test for Scenario 8 passes** ← BDD validation

---

## Implementation Order

**Outside-In Approach:**

1. **Scenario 9: Infrastructure Catalog Integration** (Priority: HIGHEST - Foundation)
   - Task 9.1 → 9.2 → Verify acceptance test PASSES
   - Rationale: All scenarios depend on VM being in catalog

2. **Scenario 1: Initial VM Deployment** (Priority: HIGH - Core flow)
   - Task 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → Verify acceptance test PASSES
   - Rationale: End-to-end deployment must work first

3. **Scenario 2: GPU Passthrough Verification** (Priority: HIGH - Critical validation)
   - Task 2.1 → 2.2 → Verify acceptance test PASSES
   - Rationale: Validates core GPU functionality

4. **Scenario 3: NVIDIA Driver Installation with Open-Distro** (Priority: MEDIUM)
   - Task 3.1 → Verify acceptance test PASSES
   - Rationale: Refines driver installation from Scenario 1

5. **Scenario 4: vLLM Service Deployment** (Priority: HIGH)
   - Task 4.1 → 4.2 → Verify acceptance test PASSES
   - Rationale: Core AI service configuration

6. **Scenario 5: Ollama Installation** (Priority: HIGH)
   - Task 5.1 → 5.2 → Verify acceptance test PASSES
   - Rationale: Second core AI service

7. **Scenario 6: Idempotent Re-deployment** (Priority: MEDIUM)
   - Task 6.1 → Verify acceptance test PASSES
   - Rationale: Validates quality of previous implementations

8. **Scenario 7: GPU Passthrough Failure Detection** (Priority: LOW)
   - Task 7.1 → Verify acceptance test PASSES
   - Rationale: Error handling edge case

9. **Scenario 8: NVIDIA Driver Installation Failure** (Priority: LOW)
   - Task 8.1 → Verify acceptance test PASSES
   - Rationale: Error handling edge case

**Key Dependencies:**
- Scenario 9 must complete first (foundation)
- Scenarios 1-6 build on each other
- Scenarios 7-8 are independent error handling cases

---

## Progress Tracking

### Overall Progress:
- **Scenarios:** 0/9 complete
- **TDD Tasks:** 0/26 complete
- **Acceptance Tests Passing:** 0/9

### Scenario Status:
- ⏳ Scenario 9 (Infrastructure Catalog): Not started ❌ FAILING
- ⏳ Scenario 1 (Initial Deployment): Not started ❌ FAILING
- ⏳ Scenario 2 (GPU Verification): Not started ❌ FAILING
- ⏳ Scenario 3 (Driver Selection): Not started ❌ FAILING
- ⏳ Scenario 4 (vLLM Service): Not started ❌ FAILING
- ⏳ Scenario 5 (Ollama Install): Not started ❌ FAILING
- ⏳ Scenario 6 (Idempotency): Not started ❌ FAILING
- ⏳ Scenario 7 (GPU Failure Handling): Not started ❌ FAILING
- ⏳ Scenario 8 (Driver Failure Handling): Not started ❌ FAILING

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
- Start with foundation (Scenario 9 - catalog entry)
- Build core deployment (Scenario 1)
- Add validation and services (Scenarios 2-5)
- Validate quality (Scenario 6 - idempotency)
- Add error handling (Scenarios 7-8)

### Technical Decisions:
- **CUDA Version:** Let ubuntu-drivers auto-select, verify 12.6+ compatibility
- **Service Auto-start:** Both vLLM and Ollama enabled with systemd
- **vLLM Network:** Bind to private IP (192.168.0.140:8000) for local network access
- **Driver Version:** Prefer *-open - distro when available
