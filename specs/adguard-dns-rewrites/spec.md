# Specification: AdGuard DNS Rewrites for Homelab Services

**Status:** Approved
**Created:** 2025-10-22

## Overview
Add DNS rewrite entries to the AdGuard Home configuration for easy access to homelab services using friendly domain names instead of IP addresses. This enables users to access Coolify, Ollama, and vLLM services via `.homelab` domains.

### Purpose
Enable convenient access to infrastructure services through memorable domain names while maintaining infrastructure-as-code principles by sourcing IP addresses from the infrastructure catalog rather than hardcoding them.

### Stakeholders
- Homelab administrators accessing services via browser/CLI
- Ansible configuration management system
- AdGuard Home DNS server (container 125)
- Infrastructure services: Coolify (VM 160), vLLM (VM 140), Ollama (VM 140)

## Functional Requirements

### Core Functionality
- Add DNS rewrite for `coolify.homelab` → `192.168.0.160` (Coolify Platform VM)
- Add DNS rewrite for `ollama.homelab` → `192.168.0.140` (AI/LLM Machine VM)
- Add DNS rewrite for `vllm.homelab` → `192.168.0.140` (AI/LLM Machine VM)
- Source IP addresses from infrastructure catalog (`infrastructure-catalog.yml`)
- Maintain existing DNS rewrites for proxmox, pve, adguard, and dns domains
- Apply configuration to AdGuard Home container 125 via Ansible

### User Interactions
Users will access services by typing friendly domain names:
- `http://coolify.homelab:8000` - Access Coolify web interface
- `http://ollama.homelab:11434` - Access Ollama API
- `http://vllm.homelab:8000` - Access vLLM API

## BDD Scenarios

### Scenario 1: DNS Rewrite Configuration Added to Ansible Defaults
**Given** the AdGuard Ansible role has existing DNS rewrites configured
**When** the role defaults are applied
**Then** the configuration should include `coolify.homelab` pointing to `192.168.0.160`
**And** the configuration should include `ollama.homelab` pointing to `192.168.0.140`
**And** the configuration should include `vllm.homelab` pointing to `192.168.0.140`
**And** existing DNS rewrites should remain unchanged

### Scenario 2: DNS Rewrites Applied to AdGuard Container
**Given** AdGuard Home is running in container 125
**When** the Ansible playbook is executed
**Then** the AdGuard configuration file should contain all three new DNS rewrites
**And** the AdGuard service should reload the configuration successfully

### Scenario 3: DNS Resolution for Coolify Service
**Given** AdGuard DNS server is running at `192.168.0.25`
**When** a DNS query is made for `coolify.homelab`
**Then** the DNS server should respond with `192.168.0.160`

### Scenario 4: DNS Resolution for Ollama Service
**Given** AdGuard DNS server is running at `192.168.0.25`
**When** a DNS query is made for `ollama.homelab`
**Then** the DNS server should respond with `192.168.0.140`

### Scenario 5: DNS Resolution for vLLM Service
**Given** AdGuard DNS server is running at `192.168.0.25`
**When** a DNS query is made for `vllm.homelab`
**Then** the DNS server should respond with `192.168.0.140`

### Scenario 6: IPs Sourced from Infrastructure Catalog
**Given** the infrastructure catalog defines service IPs
**When** the Ansible role loads default variables
**Then** Coolify IP should be loaded from `catalog.services[160].ip`
**And** AI Machine IP should be loaded from `catalog.services[140].ip`
**And** the rewrites should use catalog values, not hardcoded IPs

## Acceptance Criteria

### Functional Requirements
- [ ] `adguard_dns_rewrites` list in `defaults/main.yml` includes entry for `coolify.homelab` → `{{ catalog.services[160].ip }}`
- [ ] `adguard_dns_rewrites` list in `defaults/main.yml` includes entry for `ollama.homelab` → `{{ catalog.services[140].ip }}`
- [ ] `adguard_dns_rewrites` list in `defaults/main.yml` includes entry for `vllm.homelab` → `{{ catalog.services[140].ip }}`
- [ ] DNS rewrites use catalog lookup (not hardcoded IPs)
- [ ] Existing DNS rewrites for proxmox, pve, adguard, and dns remain unchanged
- [ ] AdGuard configuration template correctly renders DNS rewrites from the list
- [ ] Running the playbook successfully applies configuration to container 125

### DNS Resolution Verification
- [ ] DNS query for `coolify.homelab` returns `192.168.0.160`
- [ ] DNS query for `ollama.homelab` returns `192.168.0.140`
- [ ] DNS query for `vllm.homelab` returns `192.168.0.140`
- [ ] DNS queries can be verified via `nslookup` against `192.168.0.25`

### Quality Criteria
- [ ] Unit tests validate YAML structure and variable definitions
- [ ] Integration tests verify Ansible playbook syntax
- [ ] BDD tests validate end-to-end DNS resolution
- [ ] Test coverage ≥ 80% for new code
- [ ] All existing tests continue to pass
- [ ] No CRITICAL or HIGH security vulnerabilities introduced

### Documentation
- [ ] DNS rewrites documented in AdGuard role README
- [ ] Infrastructure catalog correctly reflects service IPs
- [ ] Commit message follows conventional commits format

### Definition of Done
- [ ] All 6 BDD scenarios pass
- [ ] Code reviewed and follows project conventions
- [ ] Configuration successfully deployed to AdGuard container
- [ ] Manual DNS resolution tests confirm functionality
- [ ] Changes committed with proper documentation

## Non-Functional Requirements

### Performance
- DNS resolution should complete in < 10ms (typical for local DNS)
- No measurable impact on AdGuard Home performance
- Configuration deployment should complete in < 30 seconds

### Security
- DNS rewrites only accessible within local network (192.168.0.0/24)
- No exposure of internal services to external networks
- Maintains existing AdGuard security filtering and blocking

### Maintainability
- Configuration changes managed through Ansible (infrastructure as code)
- IP addresses sourced from infrastructure catalog (single source of truth)
- Changes testable and reversible

## Constraints and Assumptions

### Technical Constraints
- Requires AdGuard Home container 125 to be running and accessible
- Requires Ansible connection to Proxmox host (192.168.0.19)
- Uses `pct exec` for container management (no direct SSH to container)
- Infrastructure catalog must be kept in sync with actual deployments

### Assumptions
- Services (Coolify, vLLM, Ollama) are running on their designated VMs
- AdGuard Home is configured as the network DNS server
- Local network clients are configured to use AdGuard DNS (192.168.0.25)
- VM IPs remain static as defined in infrastructure catalog

### Dependencies
- Infrastructure catalog (`android-19-proxmox/infrastructure-catalog.yml`)
- AdGuard Ansible role (`android-19-proxmox/configuration-by-ansible/lxc-adguard/`)
- AdGuard Home container (LXC 125) must exist and be running
- Network connectivity between DNS server and service VMs

## Implementation Details

### Files to Modify
1. `android-19-proxmox/configuration-by-ansible/lxc-adguard/defaults/main.yml`
   - Add three entries to `adguard_dns_rewrites` list (lines 93-104)

### Configuration Template
The template `AdGuardHome.yaml.j2` already handles rendering DNS rewrites from the `adguard_dns_rewrites` variable (line 65), so no template changes needed.

### Testing Approach
- **Unit tests:** Validate YAML syntax and variable structure
- **Integration tests:** Verify Ansible playbook can load and render configuration
- **BDD tests:** Execute DNS queries and verify responses
- **Manual tests:** Use `nslookup` and browser access to confirm resolution

## Open Questions
None - all requirements clarified.

## Approval
- **Created by:** AI Assistant (Claude Code)
- **Date:** 2025-10-22
- **Status:** Approved ✅
