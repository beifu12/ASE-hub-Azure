from sqlalchemy import select
from app.database import async_session
from app.models import Snippet

DEFAULT_SNIPPETS = [
    {"id": "snip_001", "category": "compute", "title": "List VMs", "command": "az vm list --resource-group <rg> --output table", "description": "List all VMs in a resource group", "user_id": "shared"},
    {"id": "snip_002", "category": "compute", "title": "Create VM", "command": "az vm create --resource-group <rg> --name <name> --image Ubuntu2204 --admin-username azureuser --generate-ssh-keys", "description": "Create a new Ubuntu VM with SSH keys", "user_id": "shared"},
    {"id": "snip_003", "category": "networking", "title": "List Public IPs", "command": "az network public-ip list --resource-group <rg> --output table", "description": "List all public IP addresses", "user_id": "shared"},
    {"id": "snip_004", "category": "networking", "title": "Show NSG Rules", "command": "az network nsg rule list --resource-group <rg> --nsg-name <nsg> --output table", "description": "View all NSG rules", "user_id": "shared"},
    {"id": "snip_005", "category": "storage", "title": "List Storage Accounts", "command": "az storage account list --resource-group <rg> --output table", "description": "List storage accounts in a resource group", "user_id": "shared"},
    {"id": "snip_006", "category": "kubernetes", "title": "Get AKS Credentials", "command": "az aks get-credentials --resource-group <rg> --name <cluster>", "description": "Get kubectl credentials for AKS cluster", "user_id": "shared"},
    {"id": "snip_007", "category": "database", "title": "List SQL Servers", "command": "az sql server list --resource-group <rg> --output table", "description": "List SQL servers in a resource group", "user_id": "shared"},
    {"id": "snip_008", "category": "monitoring", "title": "View Activity Log", "command": "az monitor activity-log list --resource-group <rg> --max-events 20 --output table", "description": "View recent activity log entries", "user_id": "shared"},
    {"id": "snip_009", "category": "bicep", "title": "Bicep Resource Group", "command": "resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {\n  name: '<name>'\n  location: '<location>'\n}", "description": "Bicep template for a resource group", "user_id": "shared"},
    {"id": "snip_010", "category": "bicep", "title": "Bicep VNet", "command": "resource vnet 'Microsoft.Network/virtualNetworks@2024-03-01' = {\n  name: '<name>'\n  location: '<location>'\n  properties: {\n    addressSpace: { addressPrefixes: ['10.0.0.0/16'] }\n  }\n}", "description": "Bicep template for a virtual network", "user_id": "shared"},
    {"id": "snip_011", "category": "compute", "title": "VM Sizes", "command": "az vm list-sizes --location <location> --output table", "description": "List available VM sizes in a region", "user_id": "shared"},
    {"id": "snip_012", "category": "kubernetes", "title": "AKS Node Pool", "command": "az aks nodepool list --resource-group <rg> --cluster-name <cluster> --output table", "description": "List node pools in AKS cluster", "user_id": "shared"},
]


async def get_snippets(category: str = "", user_id: str = "") -> dict:
    async with async_session() as db:
        query = select(Snippet)
        if category and category != "all":
            query = query.where(Snippet.category == category)
        result = await db.execute(query)
        snippets = result.scalars().all()
        items = [
            {
                "id": s.id,
                "category": s.category,
                "title": s.title,
                "command": s.command,
                "description": s.description,
                "user_id": s.user_id,
            }
            for s in snippets
        ]
        return {"items": items, "count": len(items)}
