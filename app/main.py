from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

from app.database import init_db, async_session
from app.models import Snippet
from app.routes import api, pages

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SNIPPETS_DATA = [
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


async def seed_snippets():
    async with async_session() as db:
        result = await db.execute(select(Snippet))
        if not result.scalars().first():
            for s in SNIPPETS_DATA:
                db.add(Snippet(**s))
            await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_snippets()
    yield


app = FastAPI(title="ASE Hub", version="2.3.0", lifespan=lifespan)

# ═══════════ Security ═══════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ase.hefuzh.com", "http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

from app.middleware import rate_limit_middleware, login_gate_middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(login_gate_middleware)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ═══════════ Routes ═══════════

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(api.router, prefix="/api")
app.include_router(pages.router)
