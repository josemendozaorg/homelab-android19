# Specification: GPU-Passthrough Ubuntu VM for AI/LLM Workloads

## Overview
### Purpose
This feature enables running large language models (LLMs) and AI workloads locally on the homelab infrastructure by provisioning a dedicated Ubuntu Server VM with GPU passthrough. The implementation leverages the high-performance ZOTAC GAMING RTX 5060Ti 16GB GPU to provide hardware-accelerated inference for AI models, supporting both production-like LLM serving (vLLM) and local model experimentation (Ollama).

**Problems Solved:**
- Enables local, private AI/LLM inference without cloud dependencies
- Provides isolated, reproducible environment for AI experimentation
- Maximizes GPU utilization through dedicated passthrough configuration
- Establishes Infrastructure as Code foundation for AI services in the homelab

### Stakeholders
- **Homelab Administrator**: Primary user managing AI infrastructure and running experiments
- **AI/ML Workloads**: LLM inference services, model testing, and AI application development
- **Proxmox Infrastructure**: Resource allocation, GPU passthrough management, VM lifecycle
- **Future AI Services**: Applications and services requiring local LLM capabilities (chatbots, embeddings, RAG systems)

## Functional Requirements
### Core Functionality

#### FR-1: Terraform VM Provisioning
- **FR-1.1**: Create VM resource definition in `android-19-proxmox/provisioning-by-terraform/`
- **FR-1.2**: Configure VM with 32 CPU cores, 50GB RAM, 500GB disk storage
- **FR-1.3**: Configure PCIe GPU passthrough for ZOTAC RTX 5060Ti (16GB)
- **FR-1.4**: Use existing Ubuntu Server ISO from Proxmox ISO storage
- **FR-1.5**: Configure cloud-init for SSH key injection and initial user setup
- **FR-1.6**: Add VM definition to `infrastructure-catalog.yml`
- **FR-1.7**: Assign unique VM ID following Proxmox numbering conventions
- **FR-1.8**: Configure network bridge (vmbr0) for VM connectivity

#### FR-2: Ansible VM Configuration Role
- **FR-2.1**: Create `vm-llm-aimachine` Ansible role in `configuration-by-ansible/`
- **FR-2.2**: Install NVIDIA GPU drivers using `ubuntu-drivers devices` (open-distro version)
- **FR-2.3**: Verify GPU driver installation with `dmesg | grep -i nvidia` and `nvidia-smi`
- **FR-2.4**: Install CUDA toolkit compatible with RTX 5060Ti
- **FR-2.5**: Install and configure vLLM for LLM inference serving
- **FR-2.6**: Install and configure Ollama for local model management
- **FR-2.7**: Set up Python virtual environment with AI/ML dependencies
- **FR-2.8**: Configure systemd services for vLLM and Ollama (optional auto-start)
- **FR-2.9**: Install monitoring tools (nvidia-smi, nvtop) for GPU metrics

#### FR-3: Makefile Orchestration
- **FR-3.1**: Create `deploy-vm-llm-aimachine` target in root Makefile
- **FR-3.2**: Implement Terraform provisioning step (terraform apply)
- **FR-3.3**: Implement Ansible configuration step (ansible-playbook)
- **FR-3.4**: Add validation checks (ping, SSH, GPU verification)
- **FR-3.5**: Provide helpful output messages for deployment progress

#### FR-4: Testing and Validation
- **FR-4.1**: Create unit tests for Ansible role structure validation
- **FR-4.2**: Verify Terraform configuration syntax with `terraform validate`
- **FR-4.3**: Test GPU passthrough functionality post-deployment
- **FR-4.4**: Validate NVIDIA driver installation and GPU visibility
- **FR-4.5**: Test vLLM API availability
- **FR-4.6**: Test Ollama CLI functionality

### User Interactions

**Primary Workflow:**
1. Administrator reviews specification and confirms requirements
2. Administrator runs: `make deploy-vm-llm-aimachine`
3. System executes Terraform provisioning (creates VM with GPU passthrough)
4. System executes Ansible configuration (installs drivers, vLLM, Ollama)
5. System displays deployment status and validation results
6. Administrator verifies GPU functionality with `nvidia-smi`
7. Administrator tests vLLM API: `curl http://<vm-ip>:8000/health`
8. Administrator tests Ollama: `ollama list` (via SSH to VM)

**Secondary Interactions:**
- **Manual validation**: `make test-ping` to verify network connectivity
- **SSH access**: `ssh ubuntu@<vm-ip>` for direct VM management
- **Re-configuration**: Re-run `make deploy-vm-llm-aimachine` for updates (idempotent)
- **Infrastructure updates**: Modify `infrastructure-catalog.yml` and re-deploy

## Behavior-Driven Development Scenarios

### Scenario 1: Initial VM Deployment (Happy Path)
**Given** the Proxmox host is configured with GPU passthrough enabled
**And** Ubuntu Server ISO is available in Proxmox storage
**And** the infrastructure-catalog.yml includes vm-llm-aimachine definition
**When** the administrator runs `make deploy-vm-llm-aimachine`
**Then** Terraform creates a VM with ID 140 with 32 cores, 50GB RAM, 500GB disk
**And** the VM has GPU passthrough configured for RTX 5060Ti
**And** cloud-init configures SSH keys and creates ubuntu user
**And** the VM is started successfully
**And** Ansible connects to the VM via SSH
**And** NVIDIA drivers are installed using ubuntu-drivers
**And** vLLM and Ollama are installed and configured
**And** the deployment completes with success message

### Scenario 2: GPU Passthrough Verification
**Given** the VM has been provisioned with GPU passthrough
**And** NVIDIA drivers are installed
**When** the administrator runs `nvidia-smi` inside the VM
**Then** the output shows ZOTAC RTX 5060Ti with 16GB memory
**And** the GPU driver version is displayed
**And** no errors are present in `dmesg | grep -i nvidia`
**And** CUDA is available and functional

### Scenario 3: NVIDIA Driver Installation with Open-Distro Version
**Given** the VM is running Ubuntu Server
**And** the GPU is visible via PCIe passthrough
**When** Ansible executes the driver installation tasks
**Then** `ubuntu-drivers devices` lists available drivers
**And** the "*-open - distro" driver version is selected
**And** the driver is installed successfully
**And** the system does not require reboot for driver activation
**And** `nvidia-smi` command is available and functional

### Scenario 4: vLLM Service Deployment
**Given** NVIDIA drivers and CUDA are installed
**And** Python virtual environment is configured
**When** Ansible installs and configures vLLM
**Then** vLLM is installed in the Python virtual environment
**And** vLLM API server can be started
**And** the health endpoint responds: `curl http://localhost:8000/health`
**And** vLLM can detect and utilize the GPU

### Scenario 5: Ollama Installation and Verification
**Given** the VM has NVIDIA drivers installed
**When** Ansible installs Ollama
**Then** Ollama CLI is available in PATH
**And** `ollama --version` returns version information
**And** Ollama service is running
**And** `ollama list` command executes without errors
**And** Ollama can detect and utilize the GPU

### Scenario 6: Idempotent Re-deployment
**Given** the VM vm-llm-aimachine already exists and is configured
**And** all services are running
**When** the administrator runs `make deploy-vm-llm-aimachine` again
**Then** Terraform detects existing VM and makes no changes
**And** Ansible re-applies configuration idempotently
**And** no services are disrupted
**And** GPU passthrough remains functional
**And** deployment completes successfully without errors

### Scenario 7: GPU Passthrough Failure Detection
**Given** the Proxmox host has GPU passthrough enabled
**And** the VM is being provisioned
**When** GPU passthrough configuration fails (device busy or not available)
**Then** Terraform reports a clear error message
**And** VM creation is rolled back
**And** administrator receives actionable error information
**And** no partial VM remains in broken state

### Scenario 8: NVIDIA Driver Installation Failure Handling
**Given** the VM is provisioned successfully
**And** Ansible begins driver installation
**When** driver installation fails (e.g., incompatible kernel, missing dependencies)
**Then** Ansible reports the failure clearly
**And** the playbook stops at the failed task
**And** error logs are displayed to the administrator
**And** the VM remains accessible for debugging
**And** re-running the playbook after fixing issues succeeds

### Scenario 9: Infrastructure Catalog Integration
**Given** a new VM definition needs to be added
**When** the administrator adds vm-llm-aimachine to infrastructure-catalog.yml
**Then** the catalog includes VM ID, name, CPU, RAM, disk specifications
**And** GPU passthrough device ID is specified
**And** Ubuntu Server ISO path is referenced
**And** the catalog validates successfully (YAML syntax)
**And** Terraform can read and parse the catalog
**And** the VM can be provisioned from catalog definition

## Acceptance Criteria

### Infrastructure Provisioning (Terraform)
- [ ] **AC-1**: VM with ID 140 is created on Proxmox with name `vm-llm-aimachine`
- [ ] **AC-2**: VM has 32 CPU cores allocated (`qm config 140 | grep cores`)
- [ ] **AC-3**: VM has 50GB (51200 MB) RAM allocated (`qm config 140 | grep memory`)
- [ ] **AC-4**: VM has 500GB disk storage allocated
- [ ] **AC-5**: GPU passthrough is configured for RTX 5060Ti (`qm config 140 | grep hostpci`)
- [ ] **AC-6**: VM is configured to use Ubuntu Server ISO
- [ ] **AC-7**: cloud-init is configured with SSH keys and ubuntu user
- [ ] **AC-8**: VM is added to `infrastructure-catalog.yml` with all specifications
- [ ] **AC-9**: Terraform configuration validates without errors (`terraform validate`)

### GPU and Driver Configuration (Ansible)
- [ ] **AC-10**: NVIDIA drivers are installed using `ubuntu-drivers devices` (open-distro version)
- [ ] **AC-11**: `nvidia-smi` command executes successfully and shows RTX 5060Ti
- [ ] **AC-12**: `nvidia-smi` displays 16GB GPU memory
- [ ] **AC-13**: GPU driver version is displayed in `nvidia-smi` output
- [ ] **AC-14**: `dmesg | grep -i nvidia` shows no errors
- [ ] **AC-15**: CUDA toolkit is installed and `nvcc --version` returns version information
- [ ] **AC-16**: GPU is visible in `lspci | grep -i nvidia` output

### vLLM Installation and Configuration
- [ ] **AC-17**: vLLM is installed in Python virtual environment (`pip list | grep vllm`)
- [ ] **AC-18**: vLLM API server can be started successfully
- [ ] **AC-19**: vLLM health endpoint responds: `curl http://localhost:8000/health` returns 200 OK
- [ ] **AC-20**: vLLM detects and can utilize the GPU (check logs/startup output)
- [ ] **AC-21**: vLLM systemd service file exists (if configured for auto-start)

### Ollama Installation and Configuration
- [ ] **AC-22**: Ollama binary is installed and in PATH (`which ollama`)
- [ ] **AC-23**: `ollama --version` returns version information
- [ ] **AC-24**: Ollama systemd service is running (`systemctl status ollama`)
- [ ] **AC-25**: `ollama list` command executes without errors
- [ ] **AC-26**: Ollama detects and can utilize the GPU

### Deployment Orchestration
- [ ] **AC-27**: Makefile target `deploy-vm-llm-aimachine` exists in root Makefile
- [ ] **AC-28**: Running `make deploy-vm-llm-aimachine` completes successfully
- [ ] **AC-29**: Deployment is idempotent (can be re-run without errors or changes)
- [ ] **AC-30**: Deployment completes in under 30 minutes (reasonable time limit)

### Testing and Validation
- [ ] **AC-31**: Unit tests exist for Ansible role structure validation
- [ ] **AC-32**: BDD acceptance tests exist for all 9 scenarios
- [ ] **AC-33**: All acceptance tests can be run: `pytest tests/bdd/ -v -m acceptance`
- [ ] **AC-34**: VM is reachable via SSH after deployment
- [ ] **AC-35**: VM is reachable via ping after deployment

### Documentation
- [ ] **AC-36**: Specification document is complete and committed
- [ ] **AC-37**: README.md or CLAUDE.md is updated with deployment instructions
- [ ] **AC-38**: Example usage for vLLM and Ollama is documented
- [ ] **AC-39**: Troubleshooting guide is provided for common issues

## Non-Functional Requirements

### Performance
- **NFR-1**: VM provisioning completes in under 10 minutes
- **NFR-2**: VM boot time is under 5 minutes after creation
- **NFR-3**: NVIDIA driver installation completes in under 10 minutes
- **NFR-4**: vLLM and Ollama installation completes in under 15 minutes
- **NFR-5**: Total end-to-end deployment completes in under 30 minutes
- **NFR-6**: GPU inference latency is within acceptable limits for LLM workloads (sub-second token generation)
- **NFR-7**: System remains responsive during model loading

### Security
- **NFR-8**: SSH access requires key-based authentication only (no password authentication)
- **NFR-9**: VM firewall is configured to restrict unnecessary ports
- **NFR-10**: vLLM API server binds to localhost by default (not publicly exposed)
- **NFR-11**: Ollama service runs as non-root user
- **NFR-12**: GPU passthrough does not compromise host security
- **NFR-13**: SSH keys are never stored in Terraform state or Ansible playbooks

### Usability
- **NFR-14**: Deployment requires single command: `make deploy-vm-llm-aimachine`
- **NFR-15**: Error messages provide clear, actionable guidance
- **NFR-16**: Deployment progress is visible to administrator
- **NFR-17**: Common operations (start/stop VM, restart services) are well-documented
- **NFR-18**: GPU status can be checked with simple commands (nvidia-smi)

### Maintainability
- **NFR-19**: All configuration is managed via Infrastructure as Code (no manual changes)
- **NFR-20**: Deployment is fully idempotent (safe to re-run)
- **NFR-21**: Ansible roles follow project naming conventions (vm-*)
- **NFR-22**: Code follows existing project structure and patterns

### Reliability
- **NFR-23**: Failed deployments roll back cleanly without leaving broken VMs
- **NFR-24**: GPU passthrough remains stable across VM reboots
- **NFR-25**: Services (vLLM, Ollama) can recover from crashes
- **NFR-26**: VM can be safely restarted without data loss

## Constraints and Assumptions

### Technical Constraints
- **TC-1**: Only one VM can use the physical GPU at a time (hardware limitation)
- **TC-2**: GPU must be isolated from Proxmox host (cannot be used by both)
- **TC-3**: Proxmox host must have IOMMU enabled in BIOS and kernel
- **TC-4**: GPU must be bound to vfio-pci driver on host
- **TC-5**: Requires minimum Ubuntu Server 22.04 (for NVIDIA driver compatibility)
- **TC-6**: NVIDIA open-source drivers require kernel 5.15 or later
- **TC-7**: VM requires significant resources (32 cores, 50GB RAM) - limits other VMs
- **TC-8**: ZFS storage pool must have at least 500GB free space

### Assumptions
- **AS-1**: Proxmox host (Android #19) is already configured with GPU passthrough
- **AS-2**: IOMMU groups are properly configured for GPU isolation
- **AS-3**: Ubuntu Server ISO (22.04 or 24.04) is already present in Proxmox ISO storage
- **AS-4**: SSH key authentication is configured for root@192.168.0.19
- **AS-5**: Terraform Proxmox provider is configured with valid API token
- **AS-6**: Network bridge (vmbr0) is configured and functional
- **AS-7**: Sufficient CPU cores available (at least 32 of 64 total cores)
- **AS-8**: Sufficient RAM available (at least 50GB of 96GB total RAM)
- **AS-9**: Administrator has basic knowledge of LLM inference tools
- **AS-10**: Internet connectivity is available for downloading drivers and packages

### Dependencies

#### Infrastructure Dependencies
- **DEP-1**: Proxmox VE 8.x or later (tested on Proxmox 8.2)
- **DEP-2**: ZOTAC GAMING RTX 5060Ti 16GB GPU
- **DEP-3**: AMD Ryzen 9 9950X3D CPU with IOMMU support
- **DEP-4**: ZFS storage pool with 500GB+ available space
- **DEP-5**: Network infrastructure (DHCP or static IP assignment)

#### Software Dependencies
- **DEP-6**: Terraform >= 1.5.0 (for Proxmox provider compatibility)
- **DEP-7**: Ansible >= 2.15.0 (for modern module support)
- **DEP-8**: Python >= 3.10 (required by vLLM)
- **DEP-9**: Ubuntu Server 22.04 LTS or 24.04 LTS ISO
- **DEP-10**: NVIDIA CUDA Toolkit 12.x (compatible with RTX 5060Ti)
- **DEP-11**: NVIDIA driver 550+ (open-kernel version)

#### Service Dependencies
- **DEP-12**: vLLM package (installed via pip)
- **DEP-13**: Ollama binary (installed from official source)
- **DEP-14**: Docker development environment (for running Terraform/Ansible)

#### External Dependencies
- **DEP-15**: Ubuntu package repositories (for ubuntu-drivers)
- **DEP-16**: NVIDIA driver repository (for latest drivers)
- **DEP-17**: PyPI repository (for Python packages)
- **DEP-18**: Ollama official download server

## Open Questions
- [ ] **OQ-1**: Which specific CUDA toolkit version should be installed? (12.4, 12.5, or latest?)
- [ ] **OQ-2**: Should vLLM and Ollama services auto-start on VM boot?
- [ ] **OQ-3**: What default LLM models should be pre-downloaded (if any)?
- [ ] **OQ-4**: Should we configure firewall rules to restrict external access?
- [ ] **OQ-5**: What backup strategy should be implemented for downloaded AI models?
- [ ] **OQ-6**: Should vLLM API be exposed externally or remain localhost-only?
- [ ] **OQ-7**: What monitoring should be configured for GPU metrics?
- [ ] **OQ-8**: Should we implement automatic model cleanup to manage disk space?
- [ ] **OQ-9**: What is the strategy for updating NVIDIA drivers after initial deployment?
- [ ] **OQ-10**: Should we configure swap space for large model loading?

## Approval
- **Created by:** Claude Code (AI Assistant)
- **Date:** 2025-10-16
- **Status:** Draft - Ready for Review
- **Approved by:** Pending homelab administrator review

## Implementation Readiness

### Next Steps
1. **Review Specification**: Administrator should review all requirements, constraints, and open questions
2. **Answer Open Questions**: Resolve 10 open questions (OQ-1 through OQ-10) before implementation
3. **Install BDD Framework**: `pip install -r android-19-proxmox/tests/bdd/requirements.txt`
4. **Begin Implementation**: Use `/auto-tdd-feature` workflow for automated TDD implementation

### Implementation Phases
**Phase 1: Infrastructure Provisioning (Terraform)**
- Add VM definition to `infrastructure-catalog.yml`
- Create Terraform configuration for VM with GPU passthrough
- Test Terraform provisioning

**Phase 2: Base Configuration (Ansible)**
- Create `vm-llm-aimachine` Ansible role
- Implement GPU driver installation tasks
- Verify GPU passthrough and driver functionality

**Phase 3: AI Stack Installation (Ansible)**
- Install CUDA toolkit
- Install and configure vLLM
- Install and configure Ollama
- Verify GPU access from both services

**Phase 4: Orchestration (Makefile)**
- Create `deploy-vm-llm-aimachine` target
- Integrate Terraform + Ansible workflow
- Add validation checks

**Phase 5: Testing & Documentation**
- Implement BDD step definitions
- Run acceptance tests
- Update README/CLAUDE.md with usage instructions
- Create troubleshooting guide
