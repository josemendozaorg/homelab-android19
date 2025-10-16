# Task Breakdown: Cloud-Init Adjustment

**Generated:** 2025-10-16
**Purpose:** Adjust VM deployment from manual ISO installation to automated cloud-init
**Total Tasks:** 6 tasks
**Implementation Strategy:** Refactor existing Scenario 1 implementation

---

## Overview

**Current State:**
- VM uses Ubuntu Server ISO (`ubuntu-24.04.1-live-server-amd64.iso`)
- Requires manual installation (cloud_init: false)
- GPU passthrough disabled in catalog (added manually via qm set)
- Ansible playbook targets wrong host (Proxmox instead of VM)

**Target State:**
- VM uses Ubuntu Cloud Image template
- Automated setup with cloud-init (cloud_init: true)
- GPU passthrough enabled in catalog
- Ansible playbook targets VM at 192.168.0.140
- Fully automated one-command deployment

---

## Task 1: Download and Prepare Ubuntu Cloud Image

**Description:** Download Ubuntu 24.04 cloud image and upload to Proxmox storage

**Type:** Infrastructure Setup

**Dependencies:** None

**Implementation Steps:**
1. Download Ubuntu 24.04 cloud image (`.img` file)
2. Upload to Proxmox ISO storage via SSH/scp
3. Verify image integrity

**Test Strategy:**
- Verify file exists on Proxmox: `ls -lh /var/lib/vz/template/iso/*.img`
- Check file size is reasonable (>500MB)

**Status:** Pending

---

## Task 2: Create Cloud-Init VM Template

**Description:** Create a reusable VM template from the cloud image

**Type:** Infrastructure Setup

**Dependencies:** Task 1

**Implementation Steps:**
1. Create temporary VM (ID 9000) with minimal resources
2. Import cloud image as disk to the VM
3. Configure cloud-init drive
4. Convert VM to template
5. Verify template is ready

**Test Strategy:**
- Verify template exists: `qm list | grep 9000`
- Check template flag: `qm config 9000 | grep template`

**Status:** Pending

---

## Task 3: Update Infrastructure Catalog for Cloud-Init

**Description:** Modify catalog to use cloud image template instead of ISO

**Type:** Configuration Change

**Dependencies:** Task 2

**Implementation Changes:**
- Remove `iso:` key
- Add `template_vm_id: 9000`
- Change `cloud_init: false` → `cloud_init: true`
- Change `gpu_passthrough.enabled: false` → `gpu_passthrough.enabled: true`
- Update comments to reflect cloud-init automation

**Test Strategy:**
- Unit test: Verify catalog has template_vm_id
- Unit test: Verify cloud_init is true
- Unit test: Verify gpu_passthrough.enabled is true
- YAML syntax validation

**Files Modified:**
- `android-19-proxmox/infrastructure-catalog.yml`

**Status:** Pending

---

## Task 4: Update Terraform for Cloud Image Cloning

**Description:** Modify Terraform to clone from template instead of using ISO

**Type:** Code Refactoring

**Dependencies:** Task 3

**Implementation Changes:**
- Update `main.tf` to use `clone` block for cloud-init VMs
- Remove/update `cdrom` block logic
- Ensure `initialization` block is used for cloud-init VMs
- Update `started` flag (cloud-init VMs can auto-start)

**Test Strategy:**
- Terraform validate passes
- Unit tests verify clone configuration exists
- Unit tests verify initialization block for cloud-init

**Files Modified:**
- `android-19-proxmox/provisioning-by-terraform/main.tf`

**Status:** Pending

---

## Task 5: Fix Ansible Playbook Target Host

**Description:** Change playbook from targeting Proxmox to targeting the VM

**Type:** Bug Fix

**Dependencies:** None (independent)

**Implementation Changes:**
- Change `hosts: proxmox` → `hosts: vm_llm_aimachine`
- Add `vm_llm_aimachine` to inventory.yml
- Update connection settings for VM (user: ubuntu, IP: 192.168.0.140)
- Remove delegation to Proxmox (tasks run directly on VM)

**Test Strategy:**
- Ansible syntax check passes
- Inventory includes vm_llm_aimachine host
- Connection test to VM succeeds

**Files Modified:**
- `android-19-proxmox/configuration-by-ansible/vm-llm-aimachine-setup.yml`
- `inventory.yml`

**Status:** Pending

---

## Task 6: Integration Test - Full Deployment

**Description:** Deploy VM end-to-end with cloud-init and verify

**Type:** Integration Test

**Dependencies:** Tasks 1-5

**Implementation Steps:**
1. Destroy existing VM 140 if present
2. Run `make deploy-vm-llm-aimachine`
3. Verify VM boots successfully
4. Verify cloud-init completes (SSH access works)
5. Verify GPU passthrough is configured
6. Verify Ansible configuration succeeds

**Test Strategy:**
- VM exists: `ssh root@192.168.0.19 "qm status 140"`
- VM has GPU: `ssh root@192.168.0.19 "qm config 140 | grep hostpci"`
- SSH works: `ssh -o ConnectTimeout=5 ubuntu@192.168.0.140 "echo success"`
- Ansible connects and configures successfully

**Success Criteria:**
- Deployment completes without manual intervention
- VM is accessible via SSH with cloud-init user
- GPU passthrough is configured
- NVIDIA drivers install successfully (from Ansible)

**Status:** Pending

---

## Implementation Order

1. **Task 1** → Download cloud image (5 min)
2. **Task 2** → Create template (10 min)
3. **Task 3** → Update catalog (2 min)
4. **Task 4** → Update Terraform (10 min)
5. **Task 5** → Fix Ansible target (5 min)
6. **Task 6** → Integration test (15-20 min)

**Estimated Total Time:** 45-50 minutes

---

## Progress Tracking

- **Tasks:** 0/6 complete
- **Status:** Not started

---

## Notes

### Key Decisions

**Cloud Image vs ISO:**
- Cloud images support automated cloud-init configuration
- No manual installation required
- SSH keys injected automatically
- Faster deployment (no installer)

**Template Approach:**
- Reusable template (ID 9000) for future VM clones
- Follows Proxmox best practices
- Enables quick VM provisioning

**GPU Passthrough via Terraform:**
- With root@pam API token, can configure via Terraform
- More reliable than post-creation manual configuration
- Enables true Infrastructure as Code

### Risks

- **Risk 1**: Cloud image may require different disk configuration than ISO
- **Mitigation**: Follow Proxmox documentation for cloud-init setup

- **Risk 2**: Template creation may fail if cloud image is incompatible
- **Mitigation**: Use official Ubuntu cloud images from releases.ubuntu.com

- **Risk 3**: Cloud-init may not complete before Ansible runs
- **Mitigation**: Increase wait time or add cloud-init status check

---
