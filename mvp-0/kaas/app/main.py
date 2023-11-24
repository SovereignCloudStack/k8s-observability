from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from . import models, kaas, prerequisites
from .database import engine

models.Base.metadata.create_all(bind=engine)

description = """
The SCS KaaS mock service is designed solely for development and demonstration purposes.

🚀 You will be able to:

* **Create KaaS cluster**
* **List KaaS clusters**
* **Delete KaaS cluster**.
* **Get KaaS cluster kubeconfig**
"""

app = FastAPI(
    title="SCS KaaS service",
    description=description,
    docs_url="/kaas"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(kaas.router, tags=["Clusters"], prefix="/api/clusters")


@app.on_event("startup")
async def ensure_prerequisites():
    await prerequisites.ensure()


@app.on_event("startup")
async def kaas_controller():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(kaas.bootstrap_cluster, "interval", seconds=5)
    scheduler.start()


@app.get(
    "/health",
    tags=["Health"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=models.OKSchema,
)
def get_health() -> models.OKSchema:
    return models.OKSchema(status="OK")
