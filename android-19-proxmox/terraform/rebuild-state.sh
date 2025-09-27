#!/bin/bash
# Terraform State Reconstruction Script
# Rebuilds terraform.tfstate by importing existing resources from Proxmox
# Uses infrastructure-catalog.yml as source of truth

# Don't exit on errors - we want to handle them gracefully
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATALOG_FILE="../infrastructure-catalog.yml"

# Read Proxmox configuration from catalog
PROXMOX_HOST=$(python3 -c "
import yaml
with open('$CATALOG_FILE', 'r') as f:
    catalog = yaml.safe_load(f)
print(catalog['physical']['android19-proxmox']['ip'])
")

PROXMOX_NODE=$(python3 -c "
import yaml
with open('$CATALOG_FILE', 'r') as f:
    catalog = yaml.safe_load(f)
print(catalog['physical']['android19-proxmox']['node_name'])
")

echo "🔧 Terraform State Reconstruction Tool"
echo "======================================"
echo "📡 Proxmox Host: $PROXMOX_HOST"
echo "🖥️  Proxmox Node: $PROXMOX_NODE"
echo ""

# Check if we're in the right directory
if [[ ! -f "main.tf" ]]; then
    echo "❌ Error: main.tf not found. Run this script from the terraform directory."
    exit 1
fi

# Check if catalog exists
if [[ ! -f "$CATALOG_FILE" ]]; then
    echo "❌ Error: Infrastructure catalog not found at $CATALOG_FILE"
    exit 1
fi

# Parse YAML and extract terraform-managed containers
echo "📋 Reading infrastructure catalog..."
terraform_containers=$(python3 -c "
import yaml
import sys

try:
    with open('$CATALOG_FILE', 'r') as f:
        catalog = yaml.safe_load(f)

    terraform_services = {}
    for service_id, service in catalog.get('services', {}).items():
        if service.get('provisioner') == 'terraform' and service.get('type') == 'container':
            terraform_services[service_id] = service

    for service_id, service in terraform_services.items():
        print(f'{service_id}:{service[\"name\"]}:{service[\"ip\"]}')

except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
")

if [[ -z "$terraform_containers" ]]; then
    echo "ℹ️  No Terraform-managed containers found in catalog."
    exit 0
fi

echo "🔍 Found Terraform-managed containers:"
echo "$terraform_containers" | while IFS=':' read -r id name ip; do
    echo "  - ID $id: $name ($ip)"
done
echo ""

# Check what actually exists on Proxmox
echo "🌐 Checking what exists on Proxmox..."
existing_containers=$(ssh root@$PROXMOX_HOST "pct list" 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")

if [[ -z "$existing_containers" ]]; then
    echo "⚠️  Warning: Could not retrieve container list from Proxmox"
    echo "   Make sure SSH is set up: make setup-ssh"
    exit 1
fi

echo "📦 Existing containers on Proxmox: $(echo $existing_containers | tr '\n' ' ')"
echo ""

# Backup existing state if it exists
if [[ -f "terraform.tfstate" ]]; then
    backup_file="terraform.tfstate.backup.$(date +%Y%m%d-%H%M%S)"
    echo "💾 Backing up existing state to $backup_file"
    cp terraform.tfstate "$backup_file"
fi

# Initialize terraform if needed
if [[ ! -d ".terraform" ]]; then
    echo "🏗️  Initializing Terraform..."
    terraform init
fi

# Import each existing container that should be managed by Terraform
echo "📥 Importing existing containers into Terraform state..."
echo "$terraform_containers" | while IFS=':' read -r id name ip; do
    if echo "$existing_containers" | grep -q "^$id$"; then
        echo "  🔍 Checking container $id ($name)..."

        # Try to import, capture both stdout and stderr
        import_output=$(terraform import "proxmox_virtual_environment_container.containers[\"$id\"]" "$PROXMOX_NODE/$id" 2>&1)
        import_result=$?

        if [[ $import_result -eq 0 ]]; then
            echo "  ✅ Successfully imported container $id"
        elif echo "$import_output" | grep -q "Resource already managed by Terraform"; then
            echo "  ℹ️  Container $id already in Terraform state - skipping"
        else
            echo "  ⚠️  Warning: Failed to import container $id"
            echo "     Error details:"
            echo "$import_output" | sed 's/^/       /'
        fi
    else
        echo "  ⚠️  Container $id ($name) not found on Proxmox - will be created on next apply"
    fi
done

echo ""
echo "🎉 State reconstruction complete!"
echo ""
echo "Next steps:"
echo "  1. Review the plan: terraform plan"
echo "  2. Check what will be created/modified"
echo "  3. Apply if everything looks correct: terraform apply"
echo ""
echo "If something went wrong, restore from backup:"
echo "  cp terraform.tfstate.backup.* terraform.tfstate"

# Exit successfully - even if some imports failed, the script completed its job
exit 0