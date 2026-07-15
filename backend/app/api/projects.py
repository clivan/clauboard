from fastapi import APIRouter, HTTPException

from app.schemas.project import CreateProjectRequest
from app.managers.project_manager import ProjectManager

router = APIRouter(
    prefix="/projects",
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
def create_project(request: CreateProjectRequest):

    try:
        return manager.create(request)

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error)
        )


@router.delete("/{project_id}")
def delete_project(project_id: str):

    project = manager.get(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    manager.delete(project_id)

    return {"message": "Project deleted"}


def _handle_stack_action(action, *args, **kwargs):

    try:
        return action(*args, **kwargs)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except FileNotFoundError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/{project_id}/compose/up")
def compose_up(project_id: str):

    _handle_stack_action(manager.start_stack, project_id)

    return {"status": "up"}


@router.post("/{project_id}/compose/down")
def compose_down(project_id: str):

    _handle_stack_action(manager.stop_stack, project_id)

    return {"status": "down"}


@router.post("/{project_id}/compose/restart")
def compose_restart(project_id: str):

    _handle_stack_action(manager.restart_stack, project_id)

    return {"status": "restarted"}


@router.get("/{project_id}/compose/logs")
def compose_logs(project_id: str, tail: int = 200):

    logs = _handle_stack_action(manager.stack_logs, project_id, tail)

    return {"logs": logs}


@router.get("/{project_id}/compose/status")
def compose_status(project_id: str):

    status = _handle_stack_action(manager.stack_status, project_id)

    return {"status": status}