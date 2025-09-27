# Homelab Infrastructure Management
# See: https://www.gnu.org/software/make/manual/make.html

# Variables
DOCKER_COMPOSE := docker-compose
ANSIBLE_EXEC := $(DOCKER_COMPOSE) exec -T homelab-dev
ANSIBLE_INTERACTIVE := $(DOCKER_COMPOSE) exec homelab-dev
INVENTORY := inventory.yml

# Default target
.DEFAULT_GOAL := help

# Declare phony targets
.PHONY: help env-all env-setup env-shell env-clean env-check \
        test-ping test-ping-bastion test-ping-proxmox \
        bastion-setup-sudo bastion-deploy \
        proxmox-deploy proxmox-services proxmox-adguard proxmox-terraform-prep \
        tf-init tf-plan tf-apply tf-destroy test-provision \
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
	@echo "Terraform (tf-*):"
	@$(MAKE) -s help-section SECTION="Terraform"
	@echo ""
	@echo "All Machines (all-*):"
	@$(MAKE) -s help-section SECTION="All Machines"

help-section:
	@awk 'BEGIN {FS = ":.*?## "; in_section=0} \
	      /^# $(SECTION)$$/ {in_section=1; next} \
	      /^# [A-Z]/ && in_section {in_section=0} \
	      in_section && /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment
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
	$(ANSIBLE_EXEC) ansible-playbook --syntax-check android-19-proxmox/services.yml

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
	$(ANSIBLE_EXEC) ansible-playbook android-16-bastion/playbook.yml

# Android #19 Proxmox
proxmox-deploy: ## Deploy base configuration to Proxmox server
	$(ANSIBLE_EXEC) ansible-playbook android-19-proxmox/playbook.yml

proxmox-services: ## Deploy all Proxmox services
	$(ANSIBLE_EXEC) ansible-playbook android-19-proxmox/services.yml

proxmox-adguard: ## Deploy AdGuard Home service only
	$(ANSIBLE_EXEC) ansible-playbook android-19-proxmox/services.yml --tags adguard

proxmox-terraform-prep: ## Prepare Proxmox for Terraform (download templates, etc.)
	$(ANSIBLE_EXEC) ansible-playbook android-19-proxmox/terraform-prep.yml

# Terraform
tf-init: ## Initialize Terraform
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd terraform && terraform init"

tf-plan: proxmox-terraform-prep ## Show Terraform execution plan (with Proxmox prep)
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd terraform && terraform plan"

tf-apply: proxmox-terraform-prep ## Apply Terraform configuration (with Proxmox prep)
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd terraform && terraform apply -auto-approve"

tf-destroy: ## Destroy Terraform-managed infrastructure
	$(DOCKER_COMPOSE) exec -T homelab-dev sh -c "cd terraform && terraform destroy -auto-approve"

test-provision: tf-apply test-ping ## Test workflow: prep Proxmox, provision with Terraform, test connectivity

# All Machines
all-deploy: ## Deploy configuration to all machines
	$(ANSIBLE_EXEC) ansible-playbook android-16-bastion/playbook.yml android-19-proxmox/playbook.yml

all-ping: test-ping ## Test connection to all machines (alias)

