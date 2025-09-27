variable "proxmox_api_token" {
  description = "Proxmox API token (format: user@realm!tokenid=uuid)"
  type        = string
  sensitive   = true
}