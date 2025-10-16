@acceptance
Feature: GPU-Passthrough Ubuntu VM for AI/LLM Workloads
  As a homelab administrator
  I want to deploy a GPU-enabled Ubuntu Server VM
  So that I can run AI/LLM workloads with hardware acceleration

  Background:
    Given the Proxmox host is accessible at "192.168.0.19"
    And the infrastructure catalog is loaded
    And GPU passthrough is enabled on the Proxmox host
    And Ubuntu Server ISO is available in Proxmox storage

  @deployment @happy_path
  Scenario: Initial VM Deployment (Happy Path)
    Given the infrastructure-catalog.yml includes vm-llm-aimachine definition
    When the administrator runs "make deploy-vm-llm-aimachine"
    Then Terraform creates a VM with ID 140 with 32 cores, 50GB RAM, 500GB disk
    And the VM has GPU passthrough configured for RTX 5060Ti
    And cloud-init configures SSH keys and creates ubuntu user
    And the VM is started successfully
    And Ansible connects to the VM via SSH
    And NVIDIA drivers are installed using ubuntu-drivers
    And vLLM and Ollama are installed and configured
    And the deployment completes with success message

  @gpu @verification
  Scenario: GPU Passthrough Verification
    Given the VM has been provisioned with GPU passthrough
    And NVIDIA drivers are installed
    When the administrator runs "nvidia-smi" inside the VM
    Then the output shows ZOTAC RTX 5060Ti with 16GB memory
    And the GPU driver version is displayed
    And no errors are present in "dmesg | grep -i nvidia"
    And CUDA is available and functional

  @nvidia @drivers
  Scenario: NVIDIA Driver Installation with Open-Distro Version
    Given the VM is running Ubuntu Server
    And the GPU is visible via PCIe passthrough
    When Ansible executes the driver installation tasks
    Then "ubuntu-drivers devices" lists available drivers
    And the "*-open - distro" driver version is selected
    And the driver is installed successfully
    And the system does not require reboot for driver activation
    And "nvidia-smi" command is available and functional

  @vllm @api
  Scenario: vLLM Service Deployment
    Given NVIDIA drivers and CUDA are installed
    And Python virtual environment is configured
    When Ansible installs and configures vLLM
    Then vLLM is installed in the Python virtual environment
    And vLLM API server can be started
    And the health endpoint responds: "curl http://localhost:8000/health"
    And vLLM can detect and utilize the GPU

  @ollama @cli
  Scenario: Ollama Installation and Verification
    Given the VM has NVIDIA drivers installed
    When Ansible installs Ollama
    Then Ollama CLI is available in PATH
    And "ollama --version" returns version information
    And Ollama service is running
    And "ollama list" command executes without errors
    And Ollama can detect and utilize the GPU

  @idempotency
  Scenario: Idempotent Re-deployment
    Given the VM vm-llm-aimachine already exists and is configured
    And all services are running
    When the administrator runs "make deploy-vm-llm-aimachine" again
    Then Terraform detects existing VM and makes no changes
    And Ansible re-applies configuration idempotently
    And no services are disrupted
    And GPU passthrough remains functional
    And deployment completes successfully without errors

  @error_handling @gpu
  Scenario: GPU Passthrough Failure Detection
    Given the Proxmox host has GPU passthrough enabled
    And the VM is being provisioned
    When GPU passthrough configuration fails (device busy or not available)
    Then Terraform reports a clear error message
    And VM creation is rolled back
    And administrator receives actionable error information
    And no partial VM remains in broken state

  @error_handling @nvidia
  Scenario: NVIDIA Driver Installation Failure Handling
    Given the VM is provisioned successfully
    And Ansible begins driver installation
    When driver installation fails (e.g., incompatible kernel, missing dependencies)
    Then Ansible reports the failure clearly
    And the playbook stops at the failed task
    And error logs are displayed to the administrator
    And the VM remains accessible for debugging
    And re-running the playbook after fixing issues succeeds

  @catalog @terraform
  Scenario: Infrastructure Catalog Integration
    Given a new VM definition needs to be added
    When the administrator adds vm-llm-aimachine to infrastructure-catalog.yml
    Then the catalog includes VM ID, name, CPU, RAM, disk specifications
    And GPU passthrough device ID is specified
    And Ubuntu Server ISO path is referenced
    And the catalog validates successfully (YAML syntax)
    And Terraform can read and parse the catalog
    And the VM can be provisioned from catalog definition
