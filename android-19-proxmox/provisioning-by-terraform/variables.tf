variable "proxmox_api_token" {
  description = "Proxmox API token (format: user@realm!tokenid=uuid)"
  type        = string
  sensitive   = true
}

variable "lxc_template" {
  description = "LXC template file ID for containers"
  type        = string
  default     = "local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst"
}