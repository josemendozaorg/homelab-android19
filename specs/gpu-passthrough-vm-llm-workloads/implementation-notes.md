# Implementation Notes: GPU-Passthrough Ubuntu VM for AI/LLM Workloads

**Implementation Started:** 2025-10-16
**Strategy:** Outside-in TDD (BDD scenarios guide implementation)

---

## Scenario 9: Infrastructure Catalog Integration
**Completed:** 2025-10-16
**Acceptance Test Status:** Unit tests ✓ (11/11 passing)
**Note:** BDD acceptance tests require actual infrastructure - will implement step definitions incrementally

### Tasks Completed (1 task):

#### Task 9.1: Add VM Definition to Infrastructure Catalog
**Commit:** f119807
**Test:** 11 unit tests validating catalog entry

**Implementation:**
- Added VM ID 140 to infrastructure-catalog.yml
- Configured: 32 cores, 50GB (51200 MB) RAM, 500GB disk
- GPU passthrough: RTX 5060Ti with device_id and hostpci configuration
- ISO: ubuntu-24.04.1-live-server-amd64.iso
- cloud-init: enabled for automated setup
- agent: QEMU guest agent enabled
- onboot: true (auto-start on boot)

**Key Decisions:**
- VM ID 140 follows network strategy (140 → 192.168.0.140)
- GPU device_id "0000:01:00" is placeholder (to be verified on hardware)
- cloud-init enabled for automated SSH key injection
- onboot=true since this is an AI workload server

#### Task 9.2: Create Terraform Variables for GPU Passthrough
**Status:** Deferred to Scenario 1
**Rationale:** Variables will be created with actual Terraform VM resource

### Acceptance Criteria Satisfied by This Scenario:
- [x] AC-8: VM is added to infrastructure-catalog.yml with all specifications

### Scenario Validation:
- ✓ Unit tests: 11 unit tests created and passing
- ⏳ BDD acceptance test: Step definitions are templates (to be implemented with infrastructure)
- ✓ Catalog entry: Functionally complete and validated

### Notes
- Catalog entry follows existing project patterns (VM 101, 103)
- GPU passthrough configuration includes both device_id and hostpci for Terraform flexibility
- Ubuntu Server ISO path matches existing patterns in catalog

---

## Scenario 1: Initial VM Deployment
**Started:** 2025-10-16
**Acceptance Test Status:** Unit tests ✓ (19/19 passing across Tasks 1.1-1.2)
**Progress:** 2/6 tasks complete

### Tasks Completed:

#### Task 1.1: Create Terraform VM Resource with GPU Passthrough
**Commit:** 41013e2
**Test:** 9 unit tests validating Terraform configuration

**Implementation:**
- Added dynamic hostpci block to existing proxmox_virtual_environment_vm resource
- GPU passthrough enabled conditionally when catalog has gpu_passthrough.enabled = true
- Supports configurable device_id and hostpci identifier from catalog
- PCIe passthrough, ROM bar enabled; xvga disabled (GPU as secondary initially)

**Key Decisions:**
- Used dynamic block pattern to maintain for_each loop over catalog
- Reusable for any future GPU VMs (not hardcoded to VM 140)
- Tests validate catalog-driven pattern, not hardcoded resource names
- VM 140 gets RTX 5060Ti via device "0000:01:00"

**Test Strategy:**
- Tests verify for_each pattern exists and uses catalog
- Validate GPU passthrough block presence
- Check resources, ISO, cloud-init, network, VMID all use catalog lookups
- 9/9 tests passing (GREEN phase)

#### Task 1.2: Create Ansible Role Structure (vm-llm-aimachine)
**Commit:** 381cd5b
**Test:** 10 unit tests validating role structure

**Implementation:**
- Created vm-llm-aimachine Ansible role directory structure
- defaults/main.yml with NVIDIA, vLLM, Ollama configuration
- tasks/main.yml orchestrates installation with modular includes
- Placeholder task files: nvidia-drivers.yml, vllm-install.yml, ollama-install.yml

**Key Decisions:**
- References catalog for VM configuration (single source of truth)
- NVIDIA: ubuntu-drivers with open-kernel preference, CUDA 12.6+ requirement
- vLLM: Binds to 192.168.0.140:8000 AND localhost, auto-start enabled
- Ollama: Port 11434, systemd service, auto-start enabled
- Model storage: /opt/models (vLLM), /opt/ollama/models (Ollama)

**Test Strategy:**
- 10 tests verify directory structure, YAML validity, catalog references
- Tests check all required task files exist
- 10/10 tests passing (GREEN phase)

### Tasks Remaining:
- Task 1.3: Implement NVIDIA Driver Installation Tasks
- Task 1.4: Implement vLLM Installation Tasks
- Task 1.5: Implement Ollama Installation Tasks
- Task 1.6: Create Makefile Deployment Target

---
