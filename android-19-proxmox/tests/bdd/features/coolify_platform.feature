@acceptance @bdd @coolify @platform @deployment
Feature: Coolify Platform Deployment on Proxmox
  As a homelab administrator
  I want to deploy a self-hosted PaaS platform (Coolify)
  So that I can easily deploy applications without vendor lock-in or recurring cloud costs

  Background:
    Given the Proxmox host "192.168.0.19" is accessible
    And the cloud image template VM 9000 exists

  @deployment @first_time_setup @slow
  Scenario: Initial Platform Deployment
    Given the infrastructure catalog defines VM 160 for Coolify
    When the administrator runs "make deploy-vm-coolify-platform"
    Then Terraform creates VM 160 with Ubuntu 24.04 Server
    And the VM has 8 CPU cores, 16GB RAM, and 200GB disk
    And cloud-init configures SSH keys and network settings
    And Ansible installs Coolify and all dependencies
    And the Coolify web UI is accessible at "https://coolify.homelab:8000"
    And an initial admin account is created

  @application @github @slow
  Scenario: GitHub Repository Deployment
    Given Coolify platform is running
    And GitHub integration is configured
    When a developer connects a GitHub repository containing a web application
    And the developer configures deployment settings with branch "main" and build command "npm run build"
    And the developer triggers a deployment
    Then Coolify clones the repository
    And Coolify builds the application using the specified build command
    And Coolify deploys the application in a Docker container
    And the application is accessible via assigned subdomain with automatic SSL certificate
    And the application status shows "Running" in Coolify dashboard

  @ssl @security
  Scenario: Automatic SSL Certificate Provisioning
    Given Coolify platform is running with Let's Encrypt integration
    When a new application is deployed with custom domain "app.example.com"
    Then Coolify automatically requests an SSL certificate from Let's Encrypt
    And the certificate is installed and configured in the reverse proxy
    And the application is accessible via HTTPS with a valid certificate
    And HTTP requests are automatically redirected to HTTPS

  @monitoring @observability
  Scenario: Resource Monitoring and Metrics
    Given Coolify platform is running with multiple applications deployed
    When the administrator accesses the Coolify dashboard
    Then the dashboard displays resource usage for each application including CPU, RAM, disk, and network
    And overall VM resource usage is shown
    And application logs are accessible and searchable
    And health check status is displayed for each service

  @backup @slow
  Scenario: Automated Database Backup
    Given Coolify platform has been running for 24 hours
    And backup automation is configured
    When the scheduled backup job executes
    Then the PostgreSQL database is backed up to the designated location
    And the backup includes Coolify configuration and application metadata
    And the backup is stored on Proxmox ZFS pool with compression
    And backups older than 7 days for daily backups are removed
    And backups older than 4 weeks for weekly backups are removed
    And backup completion is logged in Coolify system logs

  @cicd @webhook
  Scenario: Git Push Automatic Deployment
    Given an application is deployed and connected to GitHub
    And the webhook is configured for branch "main"
    When a developer pushes a new commit to the monitored branch
    Then the GitHub webhook notifies Coolify of the change
    And Coolify automatically pulls the latest code
    And Coolify rebuilds and redeploys the application
    And zero-downtime deployment is performed where the old version runs until the new version is ready
    And a deployment status notification is sent indicating success or failure

  @resilience @reboot @slow
  Scenario: Platform Restart and Recovery
    Given Coolify VM 160 is running with multiple applications
    When the VM is restarted for host maintenance
    Then all Docker containers start automatically on boot
    And the Coolify control panel becomes accessible within 2 minutes
    And all deployed applications resume operation
    And monitoring and metrics collection resumes
    And no manual intervention is required

  @configuration
  Scenario: Application Environment Variables Management
    Given an application is deployed on Coolify
    When the administrator updates environment variables through the Coolify UI
    And the administrator triggers an application restart
    Then the new environment variables are injected into the application container
    And the application restarts with the updated configuration
    And the previous environment state is backed up for rollback

  @rollback
  Scenario: Deployment Rollback
    Given an application has multiple deployment versions in history
    When a new deployment introduces a bug or failure
    And the administrator initiates a rollback to the previous version
    Then Coolify stops the current deployment
    And Coolify restarts the previous stable deployment
    And the rollback completes in under 30 seconds
    And the application returns to a stable state
