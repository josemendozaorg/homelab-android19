# Read existing infrastructure catalog
locals {
  catalog = yamldecode(file("../android-19-proxmox/infrastructure-catalog.yml"))
  # Filter services to only include those provisioned by Terraform
  terraform_containers = {
    for id, service in local.catalog.services :
    id => service
    if lookup(service, "provisioner", "") == "terraform" && service.type == "container"
  }
}

# Create containers defined in the catalog with provisioner: terraform
resource "proxmox_virtual_environment_container" "containers" {
  for_each = local.terraform_containers

  node_name = "proxmox"
  vm_id     = tonumber(each.key)
  started   = true  # Ensure container is started after creation

  initialization {
    hostname = each.value.name

    ip_config {
      ipv4 {
        address = "${each.value.ip}/24"
        gateway = local.catalog.network.gateway
      }
    }
  }

  operating_system {
    template_file_id = "local:vztmpl/${lookup(each.value, "template", var.lxc_template)}"
  }

  cpu {
    cores = lookup(each.value.resources, "cores", 1)
  }

  memory {
    dedicated = lookup(each.value.resources, "memory", 512)
  }

  disk {
    datastore_id = lookup(each.value, "storage", "local-lvm")
    size         = lookup(each.value.resources, "disk", 8)
  }

  # Wait for container to be fully started
  provisioner "local-exec" {
    command = "sleep 10"
  }
}

# Null resource to verify container connectivity for each container
resource "null_resource" "verify_containers" {
  for_each = local.terraform_containers
  depends_on = [proxmox_virtual_environment_container.containers]

  provisioner "local-exec" {
    command = <<-EOT
      echo "Waiting for container ${each.value.name} to be ready..."
      for i in $(seq 1 30); do
        if ping -c 1 -W 2 ${each.value.ip} > /dev/null 2>&1; then
          echo "✅ Container ${each.value.name} is responding to ping at ${each.value.ip}"
          exit 0
        fi
        echo "Attempt $i/30: Waiting for ${each.value.name}..."
        sleep 2
      done
      echo "❌ Container ${each.value.name} failed to respond after 60 seconds"
      exit 1
    EOT
  }
}