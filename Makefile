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
        proxmox-deploy proxmox-services adguard-service adguard-setup proxmox-adguard \
        proxmox-tf-init proxmox-tf-plan proxmox-tf-apply proxmox-tf-destroy proxmox-tf-show proxmox-full-deploy \
        omarchy-download-iso omarchy-check-iso omarchy-deploy omarchy-full-deploy omarchy-destroy \
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
	@echo "Omarchy VM (omarchy-*):"
	@$(MAKE) -s help-section SECTION="Omarchy VM"
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

# Omarchy VM Deployment
omarchy-download-iso: ## Download Omarchy ISO to Proxmox storage
	@echo "📥 Downloading Omarchy 3.0.2 ISO to Proxmox storage (6.2GB - may take 10+ minutes)..."
	$(ANSIBLE_EXEC) ansible proxmox --inventory $(INVENTORY) --module-name get_url --args "url=https://iso.omarchy.org/omarchy-3.0.2.iso dest=/var/lib/vz/template/iso/omarchy-3.0.2.iso checksum=sha256:8d136a99d74ef534b57356268e5dad392a124c7e28487fc00330af9105fc6626 timeout=1800"
	@echo "✅ Omarchy ISO download complete"

omarchy-check-iso: ## Check if Omarchy ISO exists in Proxmox storage
	@echo "🔍 Checking for Omarchy ISO in Proxmox storage..."
	$(ANSIBLE_EXEC) ansible proxmox --inventory $(INVENTORY) --module-name shell --args "ls -la /var/lib/vz/template/iso/omarchy-3.0.2.iso 2>/dev/null || echo 'ISO not found'"

omarchy-deploy: omarchy-check-iso ## Deploy Omarchy VM with Terraform (creates VM with ISO attached)
	@echo "🚀 Deploying Omarchy VM with ISO..."
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"
	@echo "✅ Omarchy VM created! Next steps:"
	@echo "1. Open Proxmox console for VM 101"
	@echo "2. Start the VM and complete manual installation"
	@echo "3. Select keyboard layout, timezone, and create user"
	@echo "4. After installation, enable SSH if needed"

omarchy-full-deploy: ## Complete Omarchy deployment: download ISO and create VM
	@echo "🚀 Starting complete Omarchy deployment..."
	@echo "📋 Step 1: Checking if ISO exists..."
	@$(ANSIBLE_EXEC) ansible proxmox --inventory $(INVENTORY) --module-name shell --args "test -f /var/lib/vz/template/iso/omarchy-3.0.2.iso" 2>/dev/null || $(MAKE) omarchy-download-iso
	@echo "📋 Step 2: Creating VM with ISO..."
	@$(MAKE) omarchy-deploy
	@echo "✅ Complete Omarchy deployment finished!"

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

