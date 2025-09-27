terraform {
  required_version = ">= 1.0"
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.66"
    }
  }
}

# Read infrastructure catalog for provider configuration
locals {
  catalog = yamldecode(file("../infrastructure-catalog.yml"))
}

provider "proxmox" {
  endpoint = "https://${local.catalog.physical.android19-proxmox.ip}:${local.catalog.physical.android19-proxmox.api_port}"
  api_token = var.proxmox_api_token
  insecure = true
}