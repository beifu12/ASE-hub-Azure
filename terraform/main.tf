terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# ── Resource Group ──────────────────────────────────────────────
resource "azurerm_resource_group" "ase_hub" {
  name     = "rg-ase-hub"
  location = var.location
}

# ── Azure Container Registry ────────────────────────────────────
resource "azurerm_container_registry" "ase_hub" {
  name                = "asehubacr${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.ase_hub.name
  location            = azurerm_resource_group.ase_hub.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "random_string" "suffix" {
  length  = 4
  special = false
  upper   = false
}

# ── Virtual Network ─────────────────────────────────────────────
resource "azurerm_virtual_network" "ase_hub" {
  name                = "vnet-ase-hub"
  resource_group_name = azurerm_resource_group.ase_hub.name
  location            = azurerm_resource_group.ase_hub.location
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "ase_hub" {
  name                 = "snet-ase-hub"
  resource_group_name  = azurerm_resource_group.ase_hub.name
  virtual_network_name = azurerm_virtual_network.ase_hub.name
  address_prefixes     = ["10.0.1.0/24"]
}

# ── Public IP ───────────────────────────────────────────────────
resource "azurerm_public_ip" "ase_hub" {
  name                = "pip-ase-hub"
  resource_group_name = azurerm_resource_group.ase_hub.name
  location            = azurerm_resource_group.ase_hub.location
  allocation_method   = "Static"
  sku                 = "Standard"
}

# ── Network Security Group ──────────────────────────────────────
resource "azurerm_network_security_group" "ase_hub" {
  name                = "nsg-ase-hub"
  resource_group_name = azurerm_resource_group.ase_hub.name
  location            = azurerm_resource_group.ase_hub.location

  security_rule {
    name                       = "AllowSSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP8000"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "ase_hub" {
  subnet_id                 = azurerm_subnet.ase_hub.id
  network_security_group_id = azurerm_network_security_group.ase_hub.id
}

# ── Network Interface ───────────────────────────────────────────
resource "azurerm_network_interface" "ase_hub" {
  name                = "nic-ase-hub"
  resource_group_name = azurerm_resource_group.ase_hub.name
  location            = azurerm_resource_group.ase_hub.location

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ase_hub.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ase_hub.id
  }
}

# ── Virtual Machine ─────────────────────────────────────────────
resource "azurerm_linux_virtual_machine" "ase_hub" {
  name                = "vm-ase-hub"
  resource_group_name = azurerm_resource_group.ase_hub.name
  location            = azurerm_resource_group.ase_hub.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [azurerm_network_interface.ase_hub.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.ssh_public_key_path)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    acr_login_server = azurerm_container_registry.ase_hub.login_server
  }))

  identity {
    type = "SystemAssigned"
  }
}

# ── Role Assignment: VM → ACR pull ─────────────────────────────
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.ase_hub.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_linux_virtual_machine.ase_hub.identity[0].principal_id
}
