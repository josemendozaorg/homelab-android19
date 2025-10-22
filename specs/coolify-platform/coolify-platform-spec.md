# Specification: Coolify Platform Deployment

## Overview
### Purpose
Deploy a self-hosted Platform-as-a-Service (PaaS) solution on Proxmox to enable easy application deployment without vendor lock-in or recurring cloud costs. Coolify provides a Heroku/Netlify-like experience for deploying applications, databases, and services directly on homelab infrastructure.

**Problems Solved:**
- Eliminates dependency on commercial PaaS providers (Heroku, Netlify, Vercel)
- Reduces operational complexity of manual Docker deployments
- Provides centralized management for multiple applications and services
- Enables git-based deployments with automatic SSL certificate management
- Offers production-grade features (monitoring, backups, health checks) in a homelab environment

### Stakeholders
- **Homelab Administrator**: Primary user managing the Coolify platform and deployed applications
- **Application Developers**: Users deploying web applications, APIs, and services through Coolify
- **Proxmox Infrastructure**: Android #19 host providing virtualization resources
- **Deployed Applications**: Services running on Coolify (databases, web apps, APIs, etc.)

## Functional Requirements
### Core Functionality
- **VM Provisioning**: Create Ubuntu 24.04 Server VM (ID 160) with cloud-init on Proxmox using Terraform
  - 8 CPU cores, 16GB RAM, 200GB disk storage
  - Clone from cloud image template (VM 9000)
  - Cloud-init configuration for SSH keys, user accounts, network setup

- **Coolify Installation**: Install and configure Coolify v4 using official installation script
  - Docker and Docker Compose installation
  - Coolify control panel and database (PostgreSQL)
  - Reverse proxy (Traefik or Caddy) for routing
  - SSL/TLS certificate management (Let's Encrypt)

- **GitHub Integration**: Configure GitHub OAuth for git-based deployments
  - GitHub App or OAuth application setup
  - Repository access and webhook configuration
  - Automatic deployments on git push

- **Monitoring and Metrics**: Enable built-in Coolify monitoring
  - Resource usage tracking (CPU, RAM, disk, network)
  - Application health checks and status monitoring
  - Container logs and metrics collection

- **Backup Automation**: Configure automated backups
  - Daily backups of Coolify PostgreSQL database
  - Application configuration and deployment data backups
  - Backup retention policy (7 daily, 4 weekly)
  - Storage on Proxmox ZFS pool for compression and integrity

- **Network Configuration**: Set up proper network access
  - Static IP address assignment (192.168.0.160)
  - DNS configuration for Coolify web UI (coolify.homelab.local)
  - Firewall rules (ports 80, 443, 8000 for Coolify)
  - Traefik/Caddy reverse proxy for application routing

### User Interactions
**Homelab Administrator:**
1. Deploys Coolify platform using Makefile command: `make deploy-vm-coolify-platform`
2. Accesses Coolify web UI at https://coolify.homelab.local:8000
3. Configures GitHub integration through Coolify settings
4. Creates new applications/services through Coolify dashboard
5. Monitors application health and resource usage through web UI
6. Reviews and manages backups through Coolify backup interface

**Application Developers:**
1. Connects GitHub repositories to Coolify
2. Configures deployment settings (environment variables, build commands)
3. Triggers deployments via git push or manual deployment button
4. Views application logs and metrics in Coolify dashboard
5. Manages application lifecycle (start, stop, restart, redeploy)

## Behavior-Driven Development Scenarios

### Scenario 1: Initial Platform Deployment
**Given** Proxmox host is accessible and cloud image template (VM 9000) exists
**When** administrator runs `make deploy-vm-coolify-platform`
**Then** Terraform creates VM 160 with Ubuntu 24.04 Server
**And** cloud-init configures SSH keys and network settings
**And** Ansible installs Coolify and all dependencies
**And** Coolify web UI is accessible at https://coolify.homelab.local:8000
**And** initial admin account is created

### Scenario 2: GitHub Repository Deployment
**Given** Coolify platform is running and GitHub integration is configured
**When** developer connects a GitHub repository containing a web application
**And** developer configures deployment settings (branch, build command, environment)
**And** developer triggers a deployment
**Then** Coolify clones the repository
**And** Coolify builds the application using specified build command
**And** Coolify deploys the application in a Docker container
**And** application is accessible via assigned subdomain with automatic SSL certificate
**And** application status shows "Running" in Coolify dashboard

### Scenario 3: Automatic SSL Certificate Provisioning
**Given** Coolify platform is running with Let's Encrypt integration
**When** new application is deployed with a custom domain configured
**Then** Coolify automatically requests SSL certificate from Let's Encrypt
**And** certificate is installed and configured in reverse proxy
**And** application is accessible via HTTPS with valid certificate
**And** HTTP requests are automatically redirected to HTTPS

### Scenario 4: Resource Monitoring and Metrics
**Given** Coolify platform is running with multiple applications deployed
**When** administrator accesses the Coolify dashboard
**Then** dashboard displays resource usage for each application (CPU, RAM, disk, network)
**And** overall VM resource usage is shown
**And** application logs are accessible and searchable
**And** health check status is displayed for each service

### Scenario 5: Automated Database Backup
**Given** Coolify platform has been running for 24 hours
**When** scheduled backup job executes
**Then** PostgreSQL database is backed up to designated location
**And** backup includes Coolify configuration and application metadata
**And** backup is stored on Proxmox ZFS pool with compression
**And** backup retention policy removes backups older than 7 days (for daily) and 4 weeks (for weekly)
**And** backup completion is logged in Coolify system logs

### Scenario 6: Git Push Automatic Deployment
**Given** application is deployed and connected to GitHub with webhook configured
**When** developer pushes new commit to the monitored branch
**Then** GitHub webhook notifies Coolify of the change
**And** Coolify automatically pulls latest code
**And** Coolify rebuilds and redeploys the application
**And** zero-downtime deployment is performed (old version runs until new version is ready)
**And** deployment status notification is sent (success/failure)

### Scenario 7: Platform Restart and Recovery
**Given** Coolify VM (160) is running with multiple applications
**When** VM is restarted (e.g., host maintenance)
**Then** all Docker containers start automatically on boot
**And** Coolify control panel becomes accessible within 2 minutes
**And** all deployed applications resume operation
**And** monitoring and metrics collection resumes
**And** no manual intervention is required

### Scenario 8: Application Environment Variables Management
**Given** application is deployed on Coolify
**When** administrator updates environment variables through Coolify UI
**And** administrator triggers application restart
**Then** new environment variables are injected into application container
**And** application restarts with updated configuration
**And** previous environment state is backed up for rollback

### Scenario 9: Deployment Rollback
**Given** application has multiple deployment versions in history
**When** new deployment introduces a bug or failure
**And** administrator initiates rollback to previous version
**Then** Coolify stops current deployment
**And** Coolify restarts previous stable deployment
**And** rollback completion time is under 30 seconds
**And** application returns to stable state

## Acceptance Criteria
- [ ] VM 160 is created on Proxmox with Ubuntu 24.04 Server
- [ ] VM has exactly 8 CPU cores, 16GB RAM, and 200GB disk allocated
- [ ] Cloud-init successfully configures SSH keys and network (static IP 192.168.0.160)
- [ ] Docker and Docker Compose are installed and running
- [ ] Coolify v4 is installed with PostgreSQL database
- [ ] Reverse proxy (Traefik or Caddy) is configured and running
- [ ] Coolify web UI is accessible at https://coolify.homelab.local:8000
- [ ] Initial admin account can log in successfully
- [ ] GitHub OAuth integration is configured and functional
- [ ] Test application can be deployed from GitHub repository
- [ ] Application receives automatic SSL certificate from Let's Encrypt
- [ ] HTTP requests are redirected to HTTPS automatically
- [ ] Dashboard displays resource metrics (CPU, RAM, disk, network) for applications
- [ ] Application logs are accessible through Coolify UI
- [ ] Health checks run and display status for all services
- [ ] Daily PostgreSQL database backups are automated
- [ ] Backups are stored on Proxmox ZFS pool with compression enabled
- [ ] Backup retention policy enforces 7-day daily and 4-week weekly retention
- [ ] Git webhook triggers automatic redeployment on push
- [ ] Zero-downtime deployments work (old version runs until new version is healthy)
- [ ] VM restart automatically brings up all Docker containers
- [ ] Coolify control panel becomes accessible within 2 minutes of boot
- [ ] Environment variables can be updated through UI
- [ ] Environment variable changes trigger application restart
- [ ] Deployment rollback completes in under 30 seconds
- [ ] All BDD acceptance tests pass (9 scenarios)
- [ ] Makefile target `make deploy-vm-coolify-platform` completes without errors
- [ ] Infrastructure catalog entry for VM 160 is complete and accurate
- [ ] Ansible role `vm-coolify` follows existing project conventions
- [ ] Terraform configuration matches existing VM patterns
- [ ] Documentation is updated in CLAUDE.md

## Non-Functional Requirements
### Performance
- **Coolify web UI response time**: < 2 seconds for dashboard load
- **VM boot to Coolify accessible**: < 2 minutes (includes Docker container startup)
- **Application deployment time**: < 5 minutes for typical web application (build + deploy)
- **Rollback time**: < 30 seconds to restore previous deployment
- **Resource overhead**: Coolify platform itself should use < 4GB RAM at idle
- **Concurrent deployments**: Support at least 3 simultaneous application deployments

### Security
- **SSH key-based authentication**: No password authentication allowed for VM access
- **SSL/TLS certificates**: All applications must use valid SSL certificates (Let's Encrypt)
- **HTTP to HTTPS redirect**: Mandatory for all deployed applications
- **Coolify admin password**: Must be strong (16+ characters, generated)
- **PostgreSQL database**: Local only, not exposed to external network
- **Docker socket access**: Limited to Coolify containers only
- **Secret management**: Environment variables stored encrypted in Coolify database
- **GitHub token**: OAuth token with minimum required permissions (read repo, write webhooks)
- **Firewall rules**: Only ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (Coolify UI) exposed

### Usability
- **Web UI accessibility**: Must work on modern browsers (Chrome, Firefox, Safari)
- **Error messages**: Clear, actionable error messages for deployment failures
- **Logs accessibility**: Application logs searchable and filterable in UI
- **Status indicators**: Clear visual status (running, stopped, deploying, error) for all applications
- **Deployment history**: Visible history of past deployments with ability to rollback
- **Documentation**: Inline help and tooltips in Coolify UI for common tasks

## Constraints and Assumptions
### Technical Constraints
- **Proxmox version**: Requires Proxmox VE 8.0+ for cloud-init support
- **Network**: Requires DHCP or static IP on 192.168.0.x network
- **DNS**: Requires local DNS server (AdGuard) for coolify.homelab.local resolution
- **Internet access**: VM requires internet for downloading Coolify, Docker images, and Let's Encrypt validation
- **ZFS pool**: Requires existing ZFS pool on Proxmox for backup storage
- **Cloud image template**: Depends on VM 9000 (Ubuntu 24.04 cloud image) existing
- **Resource availability**: Proxmox host must have 8 free CPU cores and 16GB free RAM
- **Disk space**: Proxmox must have 200GB available on ZFS pool

### Assumptions
- Proxmox host (Android #19, 192.168.0.19) is accessible and operational
- Cloud image template (VM 9000) has been created via `make proxmox-host-cloud-templates`
- SSH key authentication is configured for root@192.168.0.19
- Infrastructure catalog (`android-19-proxmox/infrastructure-catalog.yml`) is up to date
- Existing Terraform and Ansible patterns will be followed consistently
- GitHub account exists and can create OAuth apps
- Local DNS (AdGuard on 192.168.0.125) can add custom domain entries
- ZFS compression is enabled on backup destination pool
- Administrator has access to Proxmox web UI for troubleshooting if needed

### Dependencies
- **Proxmox API**: Terraform uses Proxmox API for VM provisioning
- **Cloud image template (VM 9000)**: Source for VM 160 OS installation
- **Docker Hub**: For pulling Coolify and application Docker images
- **GitHub**: For OAuth integration and repository access
- **Let's Encrypt**: For SSL certificate issuance (requires internet and DNS validation)
- **AdGuard DNS (VM 125)**: For local domain resolution
- **ZFS filesystem**: For backup storage with compression
- **Ansible roles**: `host-proxmox` for Proxmox host configuration
- **Terraform modules**: Existing VM provisioning patterns
- **Python pytest-bdd-ng**: For acceptance test execution

## Open Questions
- [ ] Which reverse proxy should be used: Traefik or Caddy? (Coolify supports both)
- [ ] Should Coolify use Let's Encrypt staging or production API? (staging for testing, production for real certs)
- [ ] What should be the default admin email for Coolify?
- [ ] Should GitHub integration use OAuth App or GitHub App? (OAuth simpler, GitHub App more features)
- [ ] Where should backups be stored: Proxmox host local ZFS or network share?
- [ ] Should Coolify monitoring data be retained indefinitely or have retention policy?
- [ ] Should we pre-deploy a test application as part of acceptance criteria?
- [ ] What should be the naming convention for deployed applications? (subdomain scheme)
- [ ] Should Coolify database backups be encrypted at rest?
- [ ] Should we configure email notifications for deployment failures?

## Approval
- **Created by:** Claude Code (AI Assistant)
- **Date:** 2025-10-19
- **Status:** Draft - Ready for Implementation
- **Approved by:** Pending user review
