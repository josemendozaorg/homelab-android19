output "terraform_containers" {
  description = "Information about containers managed by Terraform"
  value = {
    for id, container in proxmox_virtual_environment_container.containers :
    container.initialization[0].hostname => {
      id          = container.vm_id != null ? container.vm_id : tonumber(id)
      hostname    = container.initialization[0].hostname
      ip          = container.vm_id != null ? local.terraform_containers[tostring(container.vm_id)].ip : local.terraform_containers[id].ip
      status      = container.started ? "started" : "stopped"
      description = container.vm_id != null ? local.terraform_containers[tostring(container.vm_id)].description : local.terraform_containers[id].description
    }
  }
}

output "next_steps" {
  description = "Next steps after container creation"
  value       = <<-EOT
    Containers created successfully!

    Test connectivity with Ansible:
      make test-ping

    Configure services with Ansible:
      make proxmox-deploy
      make proxmox-services

    View all containers:
      make proxmox-tf-show
  EOT
}