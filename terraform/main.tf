# Read existing infrastructure catalog
locals {
  catalog = yamldecode(file("../android-19-proxmox/infrastructure-catalog.yml"))
}

# Test container - nginx at .30
resource "proxmox_virtual_environment_container" "test_nginx" {
  node_name = "proxmox"
  vm_id     = 130
  started   = true  # Ensure container is started after creation

  initialization {
    hostname = "test-nginx"

    ip_config {
      ipv4 {
        address = "192.168.0.30/24"
        gateway = local.catalog.network.gateway
      }
    }
  }

  operating_system {
    template_file_id = var.lxc_template
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 512
  }

  disk {
    datastore_id = "local-lvm"
    size         = 8
  }

  # Wait for container to be fully started
  provisioner "local-exec" {
    command = "sleep 10"
  }
}

# Null resource to verify container connectivity
resource "null_resource" "verify_container" {
  depends_on = [proxmox_virtual_environment_container.test_nginx]

  provisioner "local-exec" {
    command = <<-EOT
      echo "Waiting for container to be ready..."
      for i in $(seq 1 30); do
        if ping -c 1 -W 2 192.168.0.30 > /dev/null 2>&1; then
          echo "✅ Container is responding to ping at 192.168.0.30"
          exit 0
        fi
        echo "Attempt $i/30: Waiting for container..."
        sleep 2
      done
      echo "❌ Container failed to respond after 60 seconds"
      exit 1
    EOT
  }
}