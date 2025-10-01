# Read existing infrastructure catalog
locals {
  catalog = yamldecode(file("../infrastructure-catalog.yml"))
  # All container services are managed by Terraform
  terraform_containers = {
    for id, service in local.catalog.services :
    id => service
    if service.type == "container"
  }
  # All VM services are managed by Terraform
  terraform_vms = {
    for id, service in local.catalog.services :
    id => service
    if service.type == "vm"
  }
}

# Create all containers defined in the catalog
resource "proxmox_virtual_environment_container" "containers" {
  for_each = local.terraform_containers

  node_name    = local.catalog.physical.android19-proxmox.node_name
  vm_id        = tonumber(each.key)
  started      = true  # Ensure container is started after creation
  unprivileged = true  # Use unprivileged containers (required for API token access)

  # Network interface configuration
  network_interface {
    name = "eth0"
    bridge = "vmbr0"
  }

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
}

# Create all VMs defined in the catalog
resource "proxmox_virtual_environment_vm" "vms" {
  for_each = local.terraform_vms

  node_name = local.catalog.physical.android19-proxmox.node_name
  vm_id     = tonumber(each.key)
  name      = each.value.name
  started   = lookup(each.value, "cloud_init", false)  # Auto-start cloud-init VMs, manual for ISO-based

  description = each.value.description

  # BIOS and boot configuration
  bios = lookup(each.value, "bios", "ovmf")  # Default to UEFI

  machine = lookup(each.value, "machine", "q35")  # Modern chipset

  # Boot order: cloud images boot from disk, ISOs boot from ISO first
  boot_order = lookup(each.value, "cloud_init", false) ? ["scsi0"] : ["ide2", "scsi0"]

  # Enable QEMU guest agent if specified
  agent {
    enabled = lookup(each.value, "agent", false)
  }

  # CPU configuration
  cpu {
    cores   = lookup(each.value.resources, "cores", 2)
    type    = "host"  # Pass through CPU features for better performance
    sockets = 1
  }

  # Memory configuration with balloon
  memory {
    dedicated = lookup(each.value.resources, "memory", 4096)
    floating  = lookup(each.value.resources, "memory", 4096)  # Enable balloon memory
  }

  # Clone configuration for cloud-init VMs (clone from template)
  dynamic "clone" {
    for_each = lookup(each.value, "cloud_init", false) ? [1] : []
    content {
      vm_id = lookup(each.value, "template_vm_id", null)
      full  = true
    }
  }

  # Disk configuration
  # For cloud-init VMs: Resize cloned disk
  # For ISO VMs: Create blank disk
  dynamic "disk" {
    for_each = [1]
    content {
      datastore_id = lookup(each.value, "storage", "vm-storage")
      size         = lookup(each.value.resources, "disk", 150)
      interface    = "scsi0"
    }
  }

  # ISO for installation (skip for cloud images)
  dynamic "cdrom" {
    for_each = lookup(each.value, "iso", null) != null ? [1] : []
    content {
      enabled   = true
      file_id   = "local:iso/${each.value.iso}"
      interface = "ide2"
    }
  }

  # Cloud-init ISO for cloud images
  dynamic "cdrom" {
    for_each = lookup(each.value, "cloud_init", false) ? [1] : []
    content {
      enabled = true
      file_id = "local:iso/cloud-init-${each.key}.iso"
      interface = "ide2"
    }
  }

  # Network interface
  network_device {
    bridge = "vmbr0"
    model  = "virtio"
  }

  # VGA display - default settings for remote access
  vga {
    type = "std"  # Default standard VGA (compatible with remote desktop)
  }

  # On boot behavior
  on_boot = lookup(each.value, "onboot", false)

  # Operating system type for optimization
  operating_system {
    type = "l26"  # Linux 2.6/3.x/4.x/5.x/6.x kernel
  }

  # Cloud-init configuration (only for VMs with cloud_init: true)
  dynamic "initialization" {
    for_each = lookup(each.value, "cloud_init", false) ? [1] : []
    content {
      datastore_id = lookup(each.value, "storage", "local")

      # User account configuration (only works with cloud images)
      user_account {
        username = lookup(each.value, "cloud_init_user", "dev")
        password = lookup(each.value, "cloud_init_password", "dev")
        keys     = [file("~/.ssh/id_rsa.pub")]
      }

      ip_config {
        ipv4 {
          address = "${each.value.ip}/24"
          gateway = local.catalog.network.gateway
        }
      }

      dns {
        servers = [local.catalog.network.dns]
      }
    }
  }
}

