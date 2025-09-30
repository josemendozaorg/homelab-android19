packer {
  required_plugins {
    proxmox = {
      version = ">= 1.1.3"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

source "proxmox-iso" "omarchy" {
  proxmox_url          = var.proxmox_url
  username             = var.proxmox_username
  token                = var.proxmox_token
  node                 = var.proxmox_node
  insecure_skip_tls_verify = true

  boot_iso {
    iso_file         = "local:iso/omarchy-3.0.2.iso"
    unmount          = true
  }

  vm_name              = "omarchy-golden-build"
  vm_id                = var.omarchy_vm_id

  memory               = var.omarchy_memory
  cores                = var.omarchy_cores
  sockets              = 1

  scsi_controller      = "virtio-scsi-single"
  disks {
    type              = "scsi"
    disk_size         = var.omarchy_disk_size
    storage_pool      = var.proxmox_storage
    format            = "raw"
  }

  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }

  boot_wait = "10s"
  boot_command = [
    "<enter><wait10>",
    "<enter><wait5>",
    "temp-password<enter><wait3>",
    "temp-password<enter><wait3>",
    "<enter><wait30>"
  ]

  ssh_username         = "root"
  ssh_password         = "temp-password"
  ssh_timeout          = "20m"

  template_name        = "omarchy-golden-template"
  template_description = "Omarchy (Arch Linux + Hyprland) golden template"
}

build {
  sources = ["source.proxmox-iso.omarchy"]
}