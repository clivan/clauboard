from fastapi import APIRouter

from app.models.project import Project
from app.managers.project_manager import ProjectManager

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

manager = ProjectManager()


@router.get("/")
def list_projects():
    return manager.list()


@router.post("/")
def create_project(project: Project):
    return manager.create(project)