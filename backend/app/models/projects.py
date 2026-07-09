from fastapi import APIRouter, HTTPException

from app.models.project import Project
from app.services.project_manager import ProjectManager

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

manager = ProjectManager()


@router.get("/")
def list_projects():

    return manager.list()


@router.get("/{project_id}")
def get_project(project_id: str):

    project = manager.get(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


@router.post("/", status_code=201)
def create_project(project: Project):

    try:

        manager.create(project)

    except ValueError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    return project


@router.delete("/{project_id}")
def delete_project(project_id: str):

    project = manager.get(project_id)

    if project is None:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    manager.delete(project_id)

    return {
        "message": "Project deleted"
    }