.PHONY: help setup shell ping deploy clean

# Default target
help: ## Show available commands
	@echo "🏠 Homelab Management"
	@echo "===================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Build and start development environment
	docker-compose up -d --build
	@echo "✅ Environment ready! Run 'make shell' to access"

shell: ## Open shell in development container
	docker-compose exec homelab-dev bash || docker-compose run --rm homelab-dev bash

ping: ## Test connection to all machines
	docker-compose exec -T homelab-dev ansible all -i inventory.yml -m ping

setup-sudo: ## Configure passwordless sudo (run once)
	docker-compose exec homelab-dev ansible-playbook --ask-become-pass android-16-bastion/setup.yml

deploy-bastion: ## Deploy configuration to bastion host only
	docker-compose exec -T homelab-dev ansible-playbook android-16-bastion/playbook.yml

deploy-proxmox: ## Deploy configuration to Proxmox server only
	docker-compose exec -T homelab-dev ansible-playbook android-19-proxmox/playbook.yml

deploy: ## Deploy configuration to all machines
	docker-compose exec -T homelab-dev ansible-playbook android-16-bastion/playbook.yml android-19-proxmox/playbook.yml

clean: ## Stop and clean everything
	docker-compose down -v
	docker system prune -f