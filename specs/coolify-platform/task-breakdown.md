# Task Breakdown: Coolify Platform Deployment

**Generated:** 2025-10-19
**Total Scenarios:** 9
**Total TDD Tasks:** 28
**Implementation Strategy:** Outside-In (BDD → TDD)

**Implementation Decisions (from research):**
- **Reverse Proxy:** Traefik (Coolify default, best for dynamic container configuration)
- **Let's Encrypt:** Staging first, then switch to production (avoids rate limits during testing)
- **GitHub Integration:** GitHub App (fine-grained permissions, better security, automatic webhooks)
- **Backup Storage:** Proxmox host local ZFS pool (compression, snapshots, fast access)

---

## Scenario 1: Initial Platform Deployment

**Given-When-Then:**
- **Given:** Proxmox host is accessible and cloud image template (VM 9000) exists
- **When:** administrator runs `make deploy-vm-coolify-platform`
- **Then:** Terraform creates VM 160 with Ubuntu 24.04 Server
- **And:** cloud-init configures SSH keys and network settings
- **And:** Ansible installs Coolify and all dependencies
- **And:** Coolify web UI is accessible at https://coolify.homelab:8000
- **And:** initial admin account is created

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:73`
**Status:** ❌ FAILING (as expected - outer RED phase)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] VM 160 is created on Proxmox with Ubuntu 24.04 Server
- [ ] VM has exactly 8 CPU cores, 16GB RAM, and 200GB disk allocated
- [ ] Cloud-init successfully configures SSH keys and network (static IP 192.168.0.160)
- [ ] Docker and Docker Compose are installed and running
- [ ] Coolify v4 is installed with PostgreSQL database
- [ ] Reverse proxy (Traefik) is configured and running
- [ ] Coolify web UI is accessible at https://coolify.homelab.local:8000
- [ ] Initial admin account can log in successfully
- [ ] Makefile target `make deploy-vm-coolify-platform` completes without errors
- [ ] Infrastructure catalog entry for VM 160 is complete and accurate
- [ ] Ansible role `vm-coolify` follows existing project conventions
- [ ] Terraform configuration matches existing VM patterns

### Required Components (TDD Tasks):

#### Task 1.1: Infrastructure Catalog Entry
- **Description:** Add VM 160 entry to infrastructure-catalog.yml
- **Type:** Configuration
- **Dependencies:** None
- **Test Strategy:** Unit test validates YAML structure and required fields
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.2: Terraform VM Configuration
- **Description:** Create Terraform configuration for VM 160 cloning from template 9000
- **Type:** Infrastructure as Code
- **Dependencies:** Task 1.1
- **Test Strategy:** Unit test validates .tf file structure and variables
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.3: Ansible Role Structure
- **Description:** Create vm-coolify Ansible role following project conventions
- **Type:** Configuration Management
- **Dependencies:** Task 1.1
- **Test Strategy:** Unit test validates role directory structure (tasks/, defaults/, handlers/)
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.4: Cloud-init Configuration Task
- **Description:** Create Ansible task for cloud-init configuration (SSH keys, network)
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:** Unit test validates task YAML and cloud-init user-data template
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.5: Docker Installation Task
- **Description:** Create Ansible task to install Docker and Docker Compose
- **Type:** Configuration Management
- **Dependencies:** Task 1.3
- **Test Strategy:** Unit test validates task ensures Docker is installed and running
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.6: Coolify Installation Task
- **Description:** Create Ansible task to run Coolify installation script
- **Type:** Configuration Management
- **Dependencies:** Task 1.5
- **Test Strategy:** Unit test validates installation script execution with proper environment
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.7: Traefik Reverse Proxy Configuration
- **Description:** Create Ansible task to configure Traefik as reverse proxy
- **Type:** Configuration Management
- **Dependencies:** Task 1.6
- **Test Strategy:** Unit test validates Traefik configuration and docker-compose setup
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.8: Network Configuration Task
- **Description:** Create Ansible task for static IP (192.168.0.160) and DNS entry
- **Type:** Configuration Management
- **Dependencies:** Task 1.4
- **Test Strategy:** Unit test validates network interface configuration
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.9: Initial Admin Account Setup
- **Description:** Create Ansible task to configure Coolify admin account
- **Type:** Configuration Management
- **Dependencies:** Task 1.6
- **Test Strategy:** Unit test validates admin user creation with secure password
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.10: Makefile Target
- **Description:** Add deploy-vm-coolify-platform target to Makefile
- **Type:** Automation
- **Dependencies:** Tasks 1.2, 1.3
- **Test Strategy:** Unit test validates Makefile target calls Terraform and Ansible
- **Status:** Pending
- **Linked Scenario:** Scenario 1

#### Task 1.11: Integration Test - Full Deployment
- **Description:** Integration test that runs make deploy-vm-coolify-platform
- **Type:** Integration Test
- **Dependencies:** All previous tasks in Scenario 1
- **Test Strategy:** Verifies VM is created, Coolify is installed, web UI accessible
- **Status:** Pending
- **Linked Scenario:** Scenario 1

### Scenario Completion Criteria:
- [ ] All 11 component tasks completed
- [ ] All unit tests pass
- [ ] Integration test passes
- [ ] **Acceptance test for Scenario 1 passes** ← BDD validation

---

## Scenario 2: GitHub Repository Deployment

**Given-When-Then:**
- **Given:** Coolify platform is running and GitHub integration is configured
- **When:** developer connects a GitHub repository containing a web application
- **And:** developer configures deployment settings (branch, build command, environment)
- **And:** developer triggers a deployment
- **Then:** Coolify clones the repository
- **And:** Coolify builds the application using specified build command
- **And:** Coolify deploys the application in a Docker container
- **And:** application is accessible via assigned subdomain with automatic SSL certificate
- **And:** application status shows "Running" in Coolify dashboard

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:82`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] GitHub App integration is configured and functional
- [ ] Test application can be deployed from GitHub repository
- [ ] Application receives automatic SSL certificate from Let's Encrypt
- [ ] HTTP requests are redirected to HTTPS automatically

### Required Components (TDD Tasks):

#### Task 2.1: GitHub App Integration Configuration
- **Description:** Create Ansible task to configure GitHub App credentials in Coolify
- **Type:** Configuration Management
- **Dependencies:** Scenario 1 complete
- **Test Strategy:** Unit test validates GitHub App configuration in Coolify database
- **Status:** Pending
- **Linked Scenario:** Scenario 2

#### Task 2.2: Test Repository Connection
- **Description:** Create Ansible task/script to test GitHub repository connection
- **Type:** Integration Test Helper
- **Dependencies:** Task 2.1
- **Test Strategy:** Unit test validates connection test functionality
- **Status:** Pending
- **Linked Scenario:** Scenario 2

#### Task 2.3: Deployment Configuration Handling
- **Description:** Verify Coolify handles deployment configuration (branch, build command)
- **Type:** Verification Task
- **Dependencies:** Task 2.1
- **Test Strategy:** Unit test validates deployment configuration schema
- **Status:** Pending
- **Linked Scenario:** Scenario 2

### Scenario Completion Criteria:
- [ ] All 3 component tasks completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 2 passes** ← BDD validation

---

## Scenario 3: Automatic SSL Certificate Provisioning

**Given-When-Then:**
- **Given:** Coolify platform is running with Let's Encrypt integration
- **When:** new application is deployed with a custom domain configured
- **Then:** Coolify automatically requests SSL certificate from Let's Encrypt
- **And:** certificate is installed and configured in reverse proxy
- **And:** application is accessible via HTTPS with valid certificate
- **And:** HTTP requests are automatically redirected to HTTPS

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:93`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] Application receives automatic SSL certificate from Let's Encrypt
- [ ] HTTP requests are redirected to HTTPS automatically

### Required Components (TDD Tasks):

#### Task 3.1: Let's Encrypt Staging Configuration
- **Description:** Create Ansible task to configure Let's Encrypt staging in Traefik
- **Type:** Configuration Management
- **Dependencies:** Scenario 1 complete (Task 1.7)
- **Test Strategy:** Unit test validates ACME configuration for staging endpoint
- **Status:** Pending
- **Linked Scenario:** Scenario 3

#### Task 3.2: Certificate Request Automation Verification
- **Description:** Verify Traefik automatically requests certificates for new services
- **Type:** Verification Task
- **Dependencies:** Task 3.1
- **Test Strategy:** Unit test validates Traefik certificate resolver configuration
- **Status:** Pending
- **Linked Scenario:** Scenario 3

#### Task 3.3: HTTP to HTTPS Redirect Configuration
- **Description:** Ensure Traefik is configured to redirect HTTP to HTTPS
- **Type:** Configuration Management
- **Dependencies:** Task 3.1
- **Test Strategy:** Unit test validates redirect middleware in Traefik config
- **Status:** Pending
- **Linked Scenario:** Scenario 3

### Scenario Completion Criteria:
- [ ] All 3 component tasks completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 3 passes** ← BDD validation

---

## Scenario 4: Resource Monitoring and Metrics

**Given-When-Then:**
- **Given:** Coolify platform is running with multiple applications deployed
- **When:** administrator accesses the Coolify dashboard
- **Then:** dashboard displays resource usage for each application (CPU, RAM, disk, network)
- **And:** overall VM resource usage is shown
- **And:** application logs are accessible and searchable
- **And:** health check status is displayed for each service

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:101`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] Dashboard displays resource metrics (CPU, RAM, disk, network) for applications
- [ ] Application logs are accessible through Coolify UI
- [ ] Health checks run and display status for all services

### Required Components (TDD Tasks):

#### Task 4.1: Verify Coolify Built-in Monitoring
- **Description:** Verify Coolify's built-in monitoring is enabled by default
- **Type:** Verification Task
- **Dependencies:** Scenario 1 complete
- **Test Strategy:** Unit test checks Coolify configuration includes monitoring
- **Status:** Pending
- **Linked Scenario:** Scenario 4

#### Task 4.2: Dashboard Metrics Verification
- **Description:** Verify dashboard displays resource metrics correctly
- **Type:** Verification Task
- **Dependencies:** Task 4.1
- **Test Strategy:** Integration test accesses dashboard and verifies metrics are present
- **Status:** Pending
- **Linked Scenario:** Scenario 4

### Scenario Completion Criteria:
- [ ] All 2 component tasks completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 4 passes** ← BDD validation

---

## Scenario 5: Automated Database Backup

**Given-When-Then:**
- **Given:** Coolify platform has been running for 24 hours
- **When:** scheduled backup job executes
- **Then:** PostgreSQL database is backed up to designated location
- **And:** backup includes Coolify configuration and application metadata
- **And:** backup is stored on Proxmox ZFS pool with compression
- **And:** backup retention policy removes backups older than 7 days (for daily) and 4 weeks (for weekly)
- **And:** backup completion is logged in Coolify system logs

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:109`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] Daily PostgreSQL database backups are automated
- [ ] Backups are stored on Proxmox ZFS pool with compression enabled
- [ ] Backup retention policy enforces 7-day daily and 4-week weekly retention

### Required Components (TDD Tasks):

#### Task 5.1: Backup Script Creation
- **Description:** Create Ansible task to deploy backup script for Coolify database
- **Type:** Configuration Management
- **Dependencies:** Scenario 1 complete
- **Test Strategy:** Unit test validates backup script functionality
- **Status:** Pending
- **Linked Scenario:** Scenario 5

#### Task 5.2: Cron Job Configuration
- **Description:** Create Ansible task to configure cron job for daily backups
- **Type:** Configuration Management
- **Dependencies:** Task 5.1
- **Test Strategy:** Unit test validates cron job is created correctly
- **Status:** Pending
- **Linked Scenario:** Scenario 5

#### Task 5.3: ZFS Storage Path Configuration
- **Description:** Configure backup destination path on Proxmox ZFS pool
- **Type:** Configuration Management
- **Dependencies:** Task 5.1
- **Test Strategy:** Unit test validates ZFS path exists and is writable
- **Status:** Pending
- **Linked Scenario:** Scenario 5

#### Task 5.4: Retention Policy Implementation
- **Description:** Add retention policy logic to backup script (7 daily, 4 weekly)
- **Type:** Configuration Management
- **Dependencies:** Task 5.1
- **Test Strategy:** Unit test validates old backups are removed according to policy
- **Status:** Pending
- **Linked Scenario:** Scenario 5

### Scenario Completion Criteria:
- [ ] All 4 component tasks completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 5 passes** ← BDD validation

---

## Scenario 6: Git Push Automatic Deployment

**Given-When-Then:**
- **Given:** application is deployed and connected to GitHub with webhook configured
- **When:** developer pushes new commit to the monitored branch
- **Then:** GitHub webhook notifies Coolify of the change
- **And:** Coolify automatically pulls latest code
- **And:** Coolify rebuilds and redeploys the application
- **And:** zero-downtime deployment is performed (old version runs until new version is ready)
- **And:** deployment status notification is sent (success/failure)

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:118`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] Git webhook triggers automatic redeployment on push
- [ ] Zero-downtime deployments work (old version runs until new version is healthy)

### Required Components (TDD Tasks):

#### Task 6.1: GitHub Webhook Configuration Verification
- **Description:** Verify GitHub App integration automatically configures webhooks
- **Type:** Verification Task
- **Dependencies:** Scenario 2 complete (Task 2.1)
- **Test Strategy:** Unit test validates webhook is registered in GitHub
- **Status:** Pending
- **Linked Scenario:** Scenario 6

#### Task 6.2: Webhook Handling Verification
- **Description:** Verify Coolify handles webhook payloads correctly
- **Type:** Verification Task
- **Dependencies:** Task 6.1
- **Test Strategy:** Integration test simulates webhook and verifies deployment triggers
- **Status:** Pending
- **Linked Scenario:** Scenario 6

### Scenario Completion Criteria:
- [ ] All 2 component tasks completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 6 passes** ← BDD validation

---

## Scenario 7: Platform Restart and Recovery

**Given-When-Then:**
- **Given:** Coolify VM (160) is running with multiple applications
- **When:** VM is restarted (e.g., host maintenance)
- **Then:** all Docker containers start automatically on boot
- **And:** Coolify control panel becomes accessible within 2 minutes
- **And:** all deployed applications resume operation
- **And:** monitoring and metrics collection resumes
- **And:** no manual intervention is required

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:127`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] VM restart automatically brings up all Docker containers
- [ ] Coolify control panel becomes accessible within 2 minutes of boot

### Required Components (TDD Tasks):

#### Task 7.1: Docker Auto-restart Configuration
- **Description:** Ensure Docker containers are configured with restart policy
- **Type:** Configuration Management
- **Dependencies:** Scenario 1 complete (Task 1.6)
- **Test Strategy:** Unit test validates docker-compose files have restart: unless-stopped
- **Status:** Pending
- **Linked Scenario:** Scenario 7

#### Task 7.2: System Service Configuration
- **Description:** Ensure Docker service starts on boot
- **Type:** Configuration Management
- **Dependencies:** Scenario 1 complete (Task 1.5)
- **Test Strategy:** Unit test validates Docker systemd service is enabled
- **Status:** Pending
- **Linked Scenario:** Scenario 7

### Scenario Completion Criteria:
- [ ] All 2 component tasks completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 7 passes** ← BDD validation

---

## Scenario 8: Application Environment Variables Management

**Given-When-Then:**
- **Given:** application is deployed on Coolify
- **When:** administrator updates environment variables through Coolify UI
- **And:** administrator triggers application restart
- **Then:** new environment variables are injected into application container
- **And:** application restarts with updated configuration
- **And:** previous environment state is backed up for rollback

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:136`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] Environment variables can be updated through UI
- [ ] Environment variable changes trigger application restart

### Required Components (TDD Tasks):

#### Task 8.1: Environment Variable Management Verification
- **Description:** Verify Coolify's built-in env var management works correctly
- **Type:** Verification Task
- **Dependencies:** Scenario 2 complete
- **Test Strategy:** Integration test updates env vars and verifies application receives them
- **Status:** Pending
- **Linked Scenario:** Scenario 8

### Scenario Completion Criteria:
- [ ] 1 component task completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 8 passes** ← BDD validation

---

## Scenario 9: Deployment Rollback

**Given-When-Then:**
- **Given:** application has multiple deployment versions in history
- **When:** new deployment introduces a bug or failure
- **And:** administrator initiates rollback to previous version
- **Then:** Coolify stops current deployment
- **And:** Coolify restarts previous stable deployment
- **And:** rollback completion time is under 30 seconds
- **And:** application returns to stable state

**Acceptance Test:** `tests/bdd/features/coolify_platform.feature:144`
**Status:** ❌ FAILING (as expected)

### Acceptance Criteria Satisfied by This Scenario:
- [ ] Deployment rollback completes in under 30 seconds

### Required Components (TDD Tasks):

#### Task 9.1: Rollback Functionality Verification
- **Description:** Verify Coolify's built-in rollback functionality works
- **Type:** Verification Task
- **Dependencies:** Scenario 2 complete
- **Test Strategy:** Integration test deploys multiple versions and verifies rollback
- **Status:** Pending
- **Linked Scenario:** Scenario 9

### Scenario Completion Criteria:
- [ ] 1 component task completed
- [ ] All tests pass
- [ ] **Acceptance test for Scenario 9 passes** ← BDD validation

---

## Implementation Order

**Outside-In Approach:**

1. **Scenario 1** (Priority: Critical - foundational)
   - Tasks 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7 → 1.8 → 1.9 → 1.10 → 1.11 → Verify acceptance test PASSES
   - **Rationale:** All other scenarios depend on basic platform deployment. Must complete first.

2. **Scenario 3** (Priority: High - security requirement)
   - Tasks 3.1 → 3.2 → 3.3 → Verify acceptance test PASSES
   - **Rationale:** SSL/TLS is critical for security. Should be configured before deploying applications.

3. **Scenario 2** (Priority: High - core functionality)
   - Tasks 2.1 → 2.2 → 2.3 → Verify acceptance test PASSES
   - **Rationale:** GitHub integration enables application deployments. Required for scenarios 6, 8, 9.

4. **Scenario 5** (Priority: Medium - data protection)
   - Tasks 5.1 → 5.2 → 5.3 → 5.4 → Verify acceptance test PASSES
   - **Rationale:** Backup automation ensures data safety. Independent of other scenarios.

5. **Scenario 7** (Priority: Medium - resilience)
   - Tasks 7.1 → 7.2 → Verify acceptance test PASSES
   - **Rationale:** Auto-restart ensures platform reliability. Independent of other scenarios.

6. **Scenario 4** (Priority: Medium - observability)
   - Tasks 4.1 → 4.2 → Verify acceptance test PASSES
   - **Rationale:** Monitoring verification. Mostly built-in functionality check.

7. **Scenario 6** (Priority: Low - CI/CD automation)
   - Tasks 6.1 → 6.2 → Verify acceptance test PASSES
   - **Rationale:** Webhook automation. Depends on Scenario 2.

8. **Scenario 8** (Priority: Low - configuration management)
   - Task 8.1 → Verify acceptance test PASSES
   - **Rationale:** Environment variable management verification. Depends on Scenario 2.

9. **Scenario 9** (Priority: Low - failure recovery)
   - Task 9.1 → Verify acceptance test PASSES
   - **Rationale:** Rollback verification. Depends on Scenario 2.

**Key Dependencies:**
- Scenarios 2-9 all require Scenario 1 complete
- Scenarios 6, 8, 9 require Scenario 2 complete
- Scenario 3 can be implemented right after Scenario 1 (recommended for security)

---

## Progress Tracking

### Overall Progress:
- **Scenarios:** 0/9 complete
- **TDD Tasks:** 0/28 complete
- **Acceptance Tests Passing:** 0/9

### Scenario Status:
- ⏳ Scenario 1: Not started (acceptance test FAILING) - 11 tasks
- ⏳ Scenario 2: Not started (acceptance test FAILING) - 3 tasks
- ⏳ Scenario 3: Not started (acceptance test FAILING) - 3 tasks
- ⏳ Scenario 4: Not started (acceptance test FAILING) - 2 tasks
- ⏳ Scenario 5: Not started (acceptance test FAILING) - 4 tasks
- ⏳ Scenario 6: Not started (acceptance test FAILING) - 2 tasks
- ⏳ Scenario 7: Not started (acceptance test FAILING) - 2 tasks
- ⏳ Scenario 8: Not started (acceptance test FAILING) - 1 task
- ⏳ Scenario 9: Not started (acceptance test FAILING) - 1 task

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
This breakdown follows the existing homelab infrastructure patterns:
- **Infrastructure catalog** defines VM resources
- **Terraform** provisions VMs from cloud-init templates
- **Ansible** configures software and services
- **Makefile** provides convenient deployment targets
- **Tests** validate at multiple layers (unit, integration, acceptance)

### Documentation Updates:
As scenarios are completed, update:
- `specs/coolify-platform/coolify-platform-spec.md` - Check off acceptance criteria
- `specs/coolify-platform/implementation-notes.md` - Document implementation decisions
- `CLAUDE.md` - Add Coolify platform documentation

### Staging to Production Transition:
After Scenario 3 is complete and verified with staging certificates:
- Create Task 3.4: "Switch Let's Encrypt from staging to production"
- Update Traefik ACME configuration to production endpoint
- Re-request certificates for all services
- Verify production certificates are issued and trusted
