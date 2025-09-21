.PHONY: help build up down shell test ping-all configure-bastion configure-proxmox configure-all lint clean

# Default target
help: ## Show this help message
	@echo "Homelab Infrastructure Management"
	@echo "================================="
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the development container
	docker build -t homelab-dev .

up: ## Start the development environment
	docker-compose up -d

down: ## Stop the development environment
	docker-compose down

shell: ## Open a shell in the development container
	docker-compose exec homelab-dev bash || docker-compose run --rm homelab-dev bash

test: ## Test connections to all machines
	docker-compose exec homelab-dev ansible all -i inventory.yml -m ping

ping-all: ## Ping all machines to test connectivity
	@echo "Testing connection to all machines..."
	docker-compose exec homelab-dev ansible all -i inventory.yml -m ping

ping-bastion: ## Ping bastion host only
	docker-compose exec homelab-dev ansible bastion -i inventory.yml -m ping

ping-proxmox: ## Ping Proxmox server only
	docker-compose exec homelab-dev ansible proxmox -i inventory.yml -m ping

configure-bastion: ## Configure the bastion host
	docker-compose exec homelab-dev ansible-playbook android-16-bastion/playbook.yml

configure-proxmox: ## Configure the Proxmox server
	docker-compose exec homelab-dev ansible-playbook android-19-proxmox/playbook.yml

configure-all: ## Configure all machines
	docker-compose exec homelab-dev ansible-playbook android-16-bastion/playbook.yml android-19-proxmox/playbook.yml

lint: ## Lint Ansible playbooks
	docker-compose exec homelab-dev ansible-lint android-16-bastion/playbook.yml
	docker-compose exec homelab-dev ansible-lint android-19-proxmox/playbook.yml

check-syntax: ## Check Ansible syntax
	docker-compose exec homelab-dev ansible-playbook --syntax-check android-16-bastion/playbook.yml
	docker-compose exec homelab-dev ansible-playbook --syntax-check android-19-proxmox/playbook.yml

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

dev-setup: build up ## Complete development setup
	@echo "Development environment ready!"
	@echo "Run 'make shell' to access the container"
	@echo "Run 'make ping-all' to test connectivity"