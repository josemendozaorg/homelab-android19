#!/bin/bash
# Test script to verify VM 103 is properly defined in infrastructure catalog

set -e

echo "🧪 Testing VM 103 catalog entry..."
echo "=================================="

# Test 1: YAML syntax validation
echo "Test 1: Validating YAML syntax..."
python3 -c "import yaml; yaml.safe_load(open('android-19-proxmox/infrastructure-catalog.yml'))" && echo "✅ YAML syntax valid" || { echo "❌ YAML syntax invalid"; exit 1; }

# Test 2: VM 103 exists in catalog
echo "Test 2: Checking VM 103 exists..."
python3 -c "import yaml; catalog = yaml.safe_load(open('android-19-proxmox/infrastructure-catalog.yml')); assert 103 in catalog['services'], 'VM 103 not found'" && echo "✅ VM 103 exists" || { echo "❌ VM 103 not found"; exit 1; }

# Test 3: Verify required fields
echo "Test 3: Verifying required fields..."
python3 << 'EOF'
import yaml
catalog = yaml.safe_load(open('android-19-proxmox/infrastructure-catalog.yml'))
vm = catalog['services'][103]

required_fields = ['name', 'type', 'ip', 'description', 'iso', 'resources', 'storage']
for field in required_fields:
    assert field in vm, f"Missing required field: {field}"

assert vm['type'] == 'vm', "Type must be 'vm'"
assert vm['name'] == 'ubuntu-desktop-dev', "Name mismatch"
assert vm['ip'] == '192.168.0.103', "IP mismatch"
assert 'cores' in vm['resources'], "Missing cores in resources"
assert 'memory' in vm['resources'], "Missing memory in resources"
assert 'disk' in vm['resources'], "Missing disk in resources"

print("✅ All required fields present and valid")
EOF

# Test 4: Playbook can read catalog
echo "Test 4: Testing playbook can read catalog..."
docker compose exec -T homelab-dev ansible-playbook --syntax-check android-19-proxmox/ubuntu-desktop-dev-setup.yml > /dev/null 2>&1 && echo "✅ Playbook syntax valid" || { echo "❌ Playbook syntax check failed"; exit 1; }

echo ""
echo "=================================="
echo "✅ All tests passed!"
echo "VM 103 (ubuntu-desktop-dev) is properly configured"
