variable "proxmox_url" {
  type        = string
  description = "Proxmox API URL"
  default     = "https://192.168.0.19:8006/api2/json"
}

variable "proxmox_username" {
  type        = string
  description = "Proxmox username"
  default     = "terraform@pve"
}

variable "proxmox_token" {
  type        = string
  description = "Proxmox API token"
  sensitive   = true
}

variable "proxmox_node" {
  type        = string
  description = "Proxmox node name"
  default     = "proxmox"
}

variable "proxmox_storage" {
  type        = string
  description = "Proxmox storage pool"
  default     = "vm-storage"
}

variable "omarchy_vm_id" {
  type        = number
  description = "VM ID for Omarchy builder"
  default     = 9101
}

variable "omarchy_memory" {
  type        = number
  description = "Memory allocation in MB"
  default     = 32768
}

variable "omarchy_cores" {
  type        = number
  description = "CPU cores"
  default     = 16
}

variable "omarchy_disk_size" {
  type        = string
  description = "Disk size"
  default     = "250G"
}