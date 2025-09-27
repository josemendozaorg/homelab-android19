output "terraform_containers" {
  description = "Information about containers managed by Terraform"
  value = {
    for id, container in proxmox_virtual_environment_container.containers :
    container.initialization[0].hostname => {
      id       = container.vm_id
      hostname = container.initialization[0].hostname
      ip       = local.terraform_containers[tostring(container.vm_id)].ip
      status   = container.started ? "started" : "stopped"
      description = local.terraform_containers[tostring(container.vm_id)].description
    }
  }
}

output "next_steps" {
  description = "Next steps after container creation"
  value = <<-EOT
    Containers created successfully!

    Test connectivity:
      ${join("\n      ", [for id, svc in local.terraform_containers : "ping ${svc.ip}  # ${svc.name}"])}

    Configure with Ansible:
      make configure-container

    View all containers:
      make tf-show
  EOT
}