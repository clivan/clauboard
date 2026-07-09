from fastapi import APIRouter, HTTPException
from app.schemas.project import CreateProjectRequest

from app.managers.application_manager import ApplicationManager

router = APIRouter(prefix="/applications", tags=["Applications"])

manager = ApplicationManager()


@router.get("")
def list_applications():

    return manager.list()


@router.get("/{app_id}")
def get_application(app_id: str):

    app = manager.get(app_id)

    if app is None:
        raise HTTPException(404, "Application not found")

    return app

@router.post("/{app_id}/install")
def install(app_id: str):

    if not manager.install(app_id):
        raise HTTPException(404)

    return {"status": "installed"}


@router.post("/{app_id}/start")
def start(app_id: str):

    if not manager.start(app_id):
        raise HTTPException(404)

    return {"status": "running"}


@router.post("/{app_id}/stop")
def stop(app_id: str):

    if not manager.stop(app_id):
        raise HTTPException(404)

    return {"status": "stopped"}


@router.post("/{app_id}/restart")
def restart(app_id: str):

    if not manager.restart(app_id):
        raise HTTPException(404)

    return {"status": "restarted"}


@router.delete("/{app_id}")
def uninstall(app_id: str):

    if not manager.uninstall(app_id):
        raise HTTPException(404)

    return {"status": "removed"}

@router.post("/", response_model=Project)
def create_project(request: CreateProjectRequest):
    try:
        return manager.create(request)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )