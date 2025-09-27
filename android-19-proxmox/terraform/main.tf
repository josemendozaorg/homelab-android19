# Read existing infrastructure catalog
locals {
  catalog = yamldecode(file("../infrastructure-catalog.yml"))
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

    # Use cloud-init for initial container setup
    user_account {
      keys     = [file("~/.ssh/id_rsa.pub")]
      password = "changeme"
    }
  }

  operating_system {
    template_file_id = "local:vztmpl/${lookup(each.value, "template", var.lxc_template)}"
    type            = "debian"
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

  # Cloud-init startup script for basic setup
  startup {
    order      = 3
    up_delay   = 30
    down_delay = 60
  }

  # Features for better container functionality
  features {
    nesting = true
  }

  # Wait for container to be fully started
  provisioner "local-exec" {
    command = "sleep 15"
  }
}

