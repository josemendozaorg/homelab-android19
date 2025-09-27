# Read existing infrastructure catalog
locals {
  catalog = yamldecode(file("../android-19-proxmox/infrastructure-catalog.yml"))
}

# Test container - nginx at .30
resource "proxmox_virtual_environment_container" "test_nginx" {
  node_name = "android19"
  vm_id     = 130

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
    template_file_id = "local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 512
  }
}