from fastapi import APIRouter, HTTPException

from app.schemas.project import CreateProjectRequest, CloneProjectRequest
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


@router.get("/{project_id}/stack-status")
def stack_status_simple(project_id: str):
    """
    Devuelve el estado del stack de forma simple para el LED del dashboard:
    running / partial / stopped / no_compose
    """

    try:
        result = manager.stack_status(project_id)

        if not result or result.strip() == "":
            return {"status": "stopped"}

        import json as _json

        try:
            containers = _json.loads(result)

            if not containers:
                return {"status": "stopped"}

            if isinstance(containers, dict):
                containers = [containers]

            states = [c.get("State", c.get("Status", "")) for c in containers]
            running = sum(1 for s in states if "running" in s.lower())

            if running == len(states):
                return {"status": "running"}
            elif running > 0:
                return {"status": "partial"}
            else:
                return {"status": "stopped"}

        except Exception:
            return {"status": "stopped"}

    except FileNotFoundError:
        return {"status": "no_compose"}

    except Exception:
        return {"status": "stopped"}


@router.post("/{project_id}/clone", status_code=201)
def clone_project(project_id: str, request: CloneProjectRequest):

    try:
        return manager.clone(
            project_id,
            request.new_id,
            request.new_name,
            request.new_path,
        )

    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/{project_id}/compose/run")
def compose_run_command(project_id: str):
    """
    Retorna el comando `docker compose run --rm` que debes ejecutar
    en tu terminal local para abrir una shell en el toolchain del
    proyecto. No abre la shell — solo te da el comando resuelto.
    """

    command = _handle_stack_action(manager.run_stack, project_id)

    return {"command": command}