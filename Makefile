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
        test-ping test-ping-bastion test-ping-proxmox test-catalog test-unit test-all \
        setup-ssh \
        bastion-setup-sudo bastion-deploy \
        proxmox-host-setup proxmox-host-check proxmox-host-gpu-passthrough proxmox-host-pcie-aspm \
        proxmox-host-storage proxmox-host-templates proxmox-host-api \
        proxmox-deploy adguard-setup \
        proxmox-tf-init proxmox-tf-plan proxmox-tf-apply proxmox-tf-destroy proxmox-tf-show proxmox-tf-rebuild-state proxmox-full-deploy \
        deploy-lxc-adguard-dns deploy-proxmox-all \
        omarchy-deploy omarchy-destroy \
        deploy-vm-ubuntu-desktop-devmachine \
        all-deploy

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
	@echo "Terraform (proxmox-tf-*):"
	@$(MAKE) -s help-section SECTION="Terraform"
	@echo ""
	@echo "VMs (omarchy-*, deploy-vm-*):"
	@$(MAKE) -s help-section SECTION="VMs"
	@echo ""
	@echo "Services (deploy-lxc-*):"
	@$(MAKE) -s help-section SECTION="Services"
	@echo ""
	@echo "All Machines (all-*):"
	@$(MAKE) -s help-section SECTION="All Machines"

help-section:
	@awk 'BEGIN {FS = ":.*?## "; in_section=0} \
	      /^# $(SECTION)$$/ {in_section=1; next} \
	      /^# [A-Z]/ && in_section {in_section=0} \
	      in_section && /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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
	$(ANSIBLE_EXEC) ansible-playbook --syntax-check android-19-proxmox/configuration-by-ansible/playbook.yml
	$(ANSIBLE_EXEC) ansible-playbook --syntax-check android-19-proxmox/configuration-by-ansible/adguard-setup.yml

# Testing
test-ping: ## Test connection to all machines
	$(ANSIBLE_EXEC) ansible all --inventory $(INVENTORY) --module-name ping

test-ping-bastion: ## Test connection to bastion host only
	$(ANSIBLE_EXEC) ansible bastion --inventory $(INVENTORY) --module-name ping

test-ping-proxmox: ## Test connection to Proxmox server only
	$(ANSIBLE_EXEC) ansible proxmox --inventory $(INVENTORY) --module-name ping

test-catalog: ## Validate infrastructure catalog with pytest
	$(ANSIBLE_EXEC) pytest android-19-proxmox/tests/unit/test_catalog.py -v

test-unit: ## Run all unit tests
	$(ANSIBLE_EXEC) pytest android-19-proxmox/tests/unit/ -v

test-all: test-unit test-ping ## Run all tests (unit + connectivity)

# Android #16 Bastion
bastion-setup-sudo: ## Configure passwordless sudo on bastion (run once)
	$(ANSIBLE_INTERACTIVE) ansible-playbook --ask-become-pass android-16-bastion/setup.yml

bastion-deploy: ## Deploy configuration to bastion host
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-16-bastion/playbook.yml

# Android #19 Proxmox
proxmox-host-setup: ## Configure Proxmox host (storage, templates, API)
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml

proxmox-host-check: ## SAFE MODE: Validate Proxmox host config without changes
	@echo "🔍 Running Proxmox host configuration in CHECK MODE (no changes made)"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml --check --diff

proxmox-host-gpu-passthrough: ## Configure GPU passthrough for NVIDIA RTX 5060Ti
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/gpu-passthrough-setup.yml

proxmox-host-pcie-aspm: ## Disable PCIe ASPM to prevent network card disconnections
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml --tags pcie-aspm

proxmox-host-storage: ## Configure Proxmox storage only
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml --tags storage

proxmox-host-templates: ## Download container and VM templates
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml --tags templates

proxmox-host-api: ## Configure API tokens for automation
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/proxmox-host-setup.yml --tags api

proxmox-deploy: ## Deploy base configuration to Proxmox server
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/playbook.yml

proxmox-full-deploy: ## Complete deployment: Terraform + Ansible + all services
	@echo "🚀 Starting complete Proxmox infrastructure deployment..."
	@echo "📋 Step 1/4: Initialize Terraform"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform init"
	@echo "📋 Step 2/4: Apply Terraform configuration"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve"
	@echo "📋 Step 3/4: Deploy base Proxmox configuration"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/playbook.yml
	@echo "📋 Step 4/4: Deploy all services"
	$(MAKE) deploy-proxmox-all
	@echo "✅ Complete Proxmox deployment finished!"
	@echo "🌐 Run 'make test-ping' to validate deployment"

# Terraform
proxmox-tf-init: ## Initialize Terraform for Proxmox infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform init"

proxmox-tf-plan: ## Show Terraform execution plan for Proxmox
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform plan"

proxmox-tf-apply: ## Apply Terraform configuration for Proxmox
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve"

proxmox-tf-destroy: ## Destroy Terraform-managed Proxmox infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform destroy -auto-approve"

proxmox-tf-show: ## Show current Terraform state and outputs
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform show && echo '=== OUTPUTS ===' && terraform output"

proxmox-tf-rebuild-state: ## Rebuild Terraform state by importing existing infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && ./rebuild-state.sh"

# Services
deploy-lxc-adguard-dns: proxmox-tf-init ## Deploy AdGuard DNS server (LXC container)
	@echo "🚀 Deploying AdGuard DNS server (LXC)..."
	@echo "📋 Step 1/2: Provisioning container with Terraform"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_container.containers[\\\"125\\\"]"
	@echo "📋 Step 2/2: Configuring AdGuard with Ansible"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/adguard-setup.yml
	@echo "✅ AdGuard DNS server deployment complete!"

deploy-proxmox-all: deploy-lxc-adguard-dns ## Deploy all Proxmox VMs and LXCs

adguard-setup: ## Deploy AdGuard Home configuration only (Ansible)
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/adguard-setup.yml

# VMs
omarchy-deploy: proxmox-tf-init ## Deploy Omarchy VM (ISO + Terraform)
	@echo "🚀 Starting Omarchy VM deployment..."
	@echo "📋 Step 1/2: Downloading ISO if needed"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/omarchy-vm-setup.yml
	@echo "📋 Step 2/2: Creating VM with Terraform"
	@$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"
	@echo "✅ Omarchy VM created! Next steps:"
	@echo "  1. Open Proxmox console for VM 101"
	@echo "  2. Start the VM and complete manual installation"

omarchy-destroy: ## Destroy Omarchy VM with Terraform
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform destroy -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"101\\\"]"

deploy-vm-ubuntu-desktop-devmachine: proxmox-tf-init ## Deploy Ubuntu Desktop VM (ISO + Terraform)
	@echo "🖥️ Deploying Ubuntu Desktop development workstation..."
	@echo "📋 Step 1/2: Downloading Ubuntu ISO"
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-19-proxmox/configuration-by-ansible/ubuntu-desktop-dev-setup.yml
	@echo "📋 Step 2/2: Creating VM with Terraform"
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd android-19-proxmox/provisioning-by-terraform && terraform apply -auto-approve -target=proxmox_virtual_environment_vm.vms[\\\"103\\\"]"
	@echo "✅ Ubuntu Desktop VM created! Open Proxmox console to complete installation"

# All Machines
all-deploy: ## Deploy configuration to all machines
	$(ANSIBLE_EXEC) ansible-playbook --inventory $(INVENTORY) android-16-bastion/playbook.yml android-19-proxmox/configuration-by-ansible/playbook.yml
