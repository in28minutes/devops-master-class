output "resource_group" {
    value = azurerm_resource_group.resource_group
}

output "storage_account_name" {
    value = azurerm_storage_account.storage_account.name
}

output "storage_account_access_key" {
    value = azurerm_storage_account.storage_account.primary_access_key
}

output "storage_container_name" {
    value = azurerm_storage_container.storage_container.name
}