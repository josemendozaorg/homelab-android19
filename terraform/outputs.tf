output "test_container_info" {
  description = "Information about the test nginx container"
  value = {
    id       = proxmox_virtual_environment_container.test_nginx.vm_id
    hostname = proxmox_virtual_environment_container.test_nginx.initialization[0].hostname
    ip       = "192.168.0.30"
    status   = proxmox_virtual_environment_container.test_nginx.started ? "started" : "stopped"
  }
}

output "next_steps" {
  description = "Next steps after container creation"
  value = <<-EOT
    Container created successfully!

    Test connectivity:
      ping 192.168.0.30

    SSH to container (from Proxmox):
      ssh root@192.168.0.19 "pct enter 130"

    Configure with Ansible:
      make configure-test-container
  EOT
}