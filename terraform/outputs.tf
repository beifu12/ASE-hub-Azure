output "resource_group_name" {
  value = azurerm_resource_group.ase_hub.name
}

output "acr_login_server" {
  value = azurerm_container_registry.ase_hub.login_server
}

output "acr_name" {
  value = azurerm_container_registry.ase_hub.name
}

output "vm_public_ip" {
  value = azurerm_public_ip.ase_hub.ip_address
}

output "vm_ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.ase_hub.ip_address}"
}

output "web_url" {
  value = "http://${azurerm_public_ip.ase_hub.ip_address}:8000"
}
