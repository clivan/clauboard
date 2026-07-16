from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.plugins import router as plugin_router
from app.api.applications import router as application_router
from app.api.projects import router as projects_router
from app.api.agents import router as agents_router
from app.api.templates import router as templates_router
from app.api.infrastructure import router as infrastructure_router

from app.services.docker_service import DockerService
from fastapi.middleware.cors import CORSMiddleware

from app.utils.logger import logger

logger.info("Clauboard iniciado")

app = FastAPI(
    title="Clauboard",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://clauboard.localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "clauboard",
        "status": "running"
    }

app.include_router(health_router)
app.include_router(plugin_router)
app.include_router(application_router)
app.include_router(projects_router)
app.include_router(agents_router)
app.include_router(templates_router)
app.include_router(infrastructure_router)