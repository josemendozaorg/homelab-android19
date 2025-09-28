# Homelab Infrastructure Management
# See: https://www.gnu.org/software/make/manual/make.html

# Variables
DOCKER_COMPOSE := docker compose
ANSIBLE_EXEC := $(DOCKER_COMPOSE) exec -T homelab-dev
ANSIBLE_INTERACTIVE := $(DOCKER_COMPOSE) exec homelab-dev
INVENTORY := inventory.yml

# Default target
.DEFAULT_GOAL := help

# Declare phony targets
.PHONY: help env-all env-setup env-shell env-clean env-check \
        test-ping test-ping-bastion test-ping-proxmox \
        setup-ssh \
        bastion-setup-sudo bastion-deploy \
        proxmox-host-setup proxmox-host-check \
        proxmox-host-storage proxmox-host-templates proxmox-host-api \
        proxmox-deploy proxmox-services adguard-service omarchy-service adguard-setup proxmox-adguard \
        proxmox-tf-init proxmox-tf-plan proxmox-tf-apply proxmox-tf-destroy proxmox-tf-show proxmox-full-deploy \
        omarchy-iso-setup omarchy-tf-plan omarchy-tf-apply omarchy-configure omarchy-full-deploy omarchy-destroy \
        omarchy-start omarchy-stop omarchy-status \
        deploy-vm-omarchy-devmachine-automated omarchy-automated-start omarchy-automated-stop omarchy-automated-status omarchy-automated-destroy \
        all-deploy all-ping

# Help target with color output
help: ## Show available commands
	@echo "🏠 Homelab Infrastructure Management"
	@echo "====================================="
	@echo ""
	@echo "Environment (env-*):"
	@$(MAKE) -s help-section SECTION="Environment"
	@echo ""
	@echo "Testing (test-*):"
	@$(MAKE) -s help-section SECTION="Testing"
	@echo ""
	@echo "Android #16 Bastion (bastion-*):"
	@$(MAKE) -s help-section SECTION="Android #16 Bastion"
	@echo ""
	@echo "Android #19 Proxmox (proxmox-*):"
	@$(MAKE) -s help-section SECTION="Android #19 Proxmox"
	@echo ""
	@echo "Proxmox Terraform (proxmox-tf-*):"
	@$(MAKE) -s help-section SECTION="Android #19 Proxmox"
	@echo ""
	@echo "Omarchy Dev VM (omarchy-*):"
	@$(MAKE) -s help-section SECTION="Omarchy"
	@echo ""
	@echo "All Machines (all-*):"
	@$(MAKE) -s help-section SECTION="All Machines"

help-section:
	@awk 'BEGIN {FS = ":.*?## "; in_section=0} \
	      /^# $(SECTION)$$/ {in_section=1; next} \
	      /^# [A-Z]/ && in_section {in_section=0} \
	      in_section && /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment
setup-ssh: ## Set up SSH key authentication for Ansible
	@bash scripts/setup-ssh.sh


env-all: env-setup test-ping ## Build environment and test connections

env-setup: ## Build and start development environment
	$(DOCKER_COMPOSE) up -d --build
	@echo "✅ Environment ready! Run 'make env-shell' to access"

env-shell: ## Open interactive shell in development container
	$(DOCKER_COMPOSE) exec homelab-dev bash || $(DOCKER_COMPOSE) run --rm homelab-dev bash

env-clean: ## Stop containers and clean Docker resources
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

env-check: ## Validate Ansible configuration
	$(ANSIBLE_EXEC) ansible-inventory --list --inventory $(INVENTORY)
	$(ANSIBLE_EXEC) ansible-playbook --syntax-check android-16-bastion/playbook.yml
	$(ANSIBLE_EXEC) ansible-playbook --syntax-check android-19-proxmox/playbook.yml
	$(ANSIBLE_EXEC) ansible-playbook --syntax-check android-19-proxmox/adguard-setup.yml

# Testing
test-ping: ## Test connection to all machines
	$(ANSIBLE_EXEC) ansible all --inventory $(INVENTORY) --module-name ping

test-ping-bastion: ## Test connection to bastion host only
	$(ANSIBLE_EXEC) ansible bastion --inventory $(INVENTORY) --module-name ping

test-ping-proxmox: ## Test connection to Proxmox server only
	$(ANSIBLE_EXEC) ansible proxmox --inventory $(INVENTORY) --module-name ping

# Android #16 Bastion
bastion-setup-sudo: ## Configure passwordless sudo on bastion (run once)
	$(ANSIBLE_INTERACTIVE) ansible-playbook --ask-become-pass android-16-bastion/setup.yml

bastion-deploy: ## Deploy configuration to bastion host
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-16-bastion/playbook.yml

# Android #19 Proxmox
proxmox-host-setup: ## Configure Proxmox host (storage, network, templates, API)
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/proxmox-host-setup.yml

proxmox-host-check: ## SAFE MODE: Validate Proxmox host configuration without making changes
	@echo "🔍 Running Proxmox host configuration in CHECK MODE (no changes made)"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/proxmox-host-setup.yml --check --diff

# Network configuration removed - Proxmox handles this during installation

proxmox-host-storage: ## Configure Proxmox storage only
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/proxmox-host-setup.yml --tags storage

proxmox-host-templates: ## Download container and VM templates
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/proxmox-host-setup.yml --tags templates

proxmox-host-api: ## Configure API tokens for automation
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/proxmox-host-setup.yml --tags api

proxmox-deploy: ## Deploy base configuration to Proxmox server
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/playbook.yml

proxmox-services: deploy-proxmox-all ## Deploy all Proxmox services (orchestration)

# Service-level orchestration (Terraform + Ansible)
# Services depend on Proxmox host being properly configured
deploy-lxc-adguard-dns: proxmox-tf-init ## Deploy AdGuard DNS server (LXC container)
	@echo "🚀 Deploying AdGuard DNS server (LXC)..."
	@echo "📋 Step 1/2: Provisioning container with Terraform"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_container.containers[\\\"125\\\"]"
	@echo "📋 Step 2/2: Configuring AdGuard with Ansible"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/adguard-setup.yml
	@echo "✅ AdGuard DNS server deployment complete!"

deploy-vm-omarchy-devmachine: proxmox-tf-init ## Deploy Omarchy development workstation (VM)
	@echo "🚀 Deploying Omarchy development workstation (VM)..."
	@echo "📋 Step 1/3: Download ISO"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/omarchy-setup.yml --tags iso
	@echo "📋 Step 2/3: Provisioning VM with Terraform"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"
	@echo "📋 Step 3/3: Initial configuration with Ansible"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/omarchy-setup.yml --tags configure
	@echo "✅ Omarchy development workstation deployment complete! Complete OS installation manually."

omarchy-start: ## Start Omarchy VM
	@echo "🚀 Starting Omarchy VM..."
	$(ANSIBLE_EXEC) ansible proxmox -m command -a "qm start 101" --inventory $(INVENTORY)

omarchy-stop: ## Stop Omarchy VM
	@echo "🛑 Stopping Omarchy VM..."
	$(ANSIBLE_EXEC) ansible proxmox -m command -a "qm stop 101" --inventory $(INVENTORY)

omarchy-status: ## Check Omarchy VM status
	@echo "📊 Checking Omarchy VM status..."
	$(ANSIBLE_EXEC) ansible proxmox -m shell -a "qm status 101 && echo '---' && qm config 101 | grep -E 'cores|memory|balloon|boot'" --inventory $(INVENTORY)

deploy-vm-omarchy-devmachine-automated: proxmox-tf-init ## Deploy Omarchy development workstation - Fully automated cloud-init installation (VM)
	@echo "🤖 Deploying Omarchy development workstation with cloud-init automation..."
	@echo "📋 Step 1/3: Download Arch Linux Cloud Image (QCOW2)"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/omarchy-automated-setup.yml --tags download
	@echo "📋 Step 2/3: Prepare cloud-init configuration"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/omarchy-automated-setup.yml --tags cloud-init
	@echo "📋 Step 3/3: Provision VM with Terraform (imports QCOW2 + cloud-init)"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"102\\\"]"
	@echo "🔄 Cloud-init will automatically install Omarchy (monitor via VM console)"
	@echo "✅ Automated Omarchy development workstation deployment initiated!"
	@echo "📊 Check status with: make omarchy-automated-status"

omarchy-automated-start: ## Start Automated Omarchy VM
	@echo "🚀 Starting Automated Omarchy VM..."
	$(ANSIBLE_EXEC) ansible proxmox -m command -a "qm start 102" --inventory $(INVENTORY)

omarchy-automated-stop: ## Stop Automated Omarchy VM
	@echo "🛑 Stopping Automated Omarchy VM..."
	$(ANSIBLE_EXEC) ansible proxmox -m command -a "qm stop 102" --inventory $(INVENTORY)

omarchy-automated-status: ## Check Automated Omarchy VM status
	@echo "📊 Checking Automated Omarchy VM status..."
	$(ANSIBLE_EXEC) ansible proxmox -m shell -a "qm status 102 && echo '---' && qm config 102 | grep -E 'cores|memory|balloon|boot'" --inventory $(INVENTORY)

omarchy-automated-destroy: ## Destroy Automated Omarchy VM with Terraform
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform destroy -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"102\\\"]"

# Group deployment targets
deploy-proxmox-all: deploy-lxc-adguard-dns ## Deploy all Proxmox VMs and LXCs

# Individual component deployment
adguard-setup: ## Deploy AdGuard Home configuration only (Ansible)
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/adguard-setup.yml


proxmox-tf-init: ## Initialize Terraform for Proxmox infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform init"

proxmox-tf-plan: ## Show Terraform execution plan for Proxmox
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform plan"

proxmox-tf-apply: ## Apply Terraform configuration for Proxmox
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve"

proxmox-tf-destroy: ## Destroy Terraform-managed Proxmox infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform destroy -auto-approve"

proxmox-tf-show: ## Show current Terraform state and outputs for Proxmox
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform show && echo '=== OUTPUTS ===' && terraform output"

proxmox-tf-rebuild-state: ## Rebuild Terraform state by importing existing infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && ./rebuild-state.sh"

# Omarchy
omarchy-iso-setup: ## Download Omarchy ISO to Proxmox storage
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/omarchy-setup.yml --tags iso

omarchy-tf-plan: ## Plan Terraform changes for Omarchy VM
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform plan -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"

omarchy-tf-apply: omarchy-iso-setup ## Provision Omarchy VM with Terraform (downloads ISO first)
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"

omarchy-configure: ## Configure Omarchy VM post-provisioning
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/omarchy-setup.yml --tags configure

omarchy-full-deploy: omarchy-tf-apply omarchy-configure ## Complete Omarchy deployment (Terraform + Ansible)
	@echo "✅ Omarchy VM provisioned and configured. Next steps:"
	@echo "1. Start VM: qm start 101"
	@echo "2. Complete Omarchy installation via Proxmox console"
	@echo "3. Install QEMU guest agent in the VM"
	@echo "4. Verify SSH access at 192.168.0.101"

omarchy-destroy: ## Destroy Omarchy VM with Terraform
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform destroy -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"


# Complete Infrastructure Deployment
proxmox-full-deploy: ## Complete Proxmox deployment: Terraform provision + Ansible configure
	@echo "🚀 Starting complete Proxmox infrastructure deployment..."
	@echo "📋 Step 1/4: Initialize Terraform"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform init"
	@echo "📋 Step 2/4: Apply Terraform configuration"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve"
	@echo "📋 Step 3/4: Deploy base Proxmox configuration"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/playbook.yml
	@echo "📋 Step 4/4: Deploy all services"
	$(MAKE) deploy-proxmox-all
	@echo "✅ Complete Proxmox deployment finished!"
	@echo "🌐 Run 'make test-ping' to validate deployment"

# All Machines
all-deploy: ## Deploy configuration to all machines
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-16-bastion/playbook.yml android-19-proxmox/playbook.yml

all-ping: test-ping ## Test connection to all machines (alias)

