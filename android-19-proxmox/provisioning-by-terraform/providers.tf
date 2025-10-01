terraform {
  required_version = ">= 1.0"
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.66"
    }
  }
}

provider "proxmox" {
  endpoint = "https://${local.catalog.proxmox.ip}:${local.catalog.proxmox.api_port}"
  api_token = var.proxmox_api_token
  insecure = true
}