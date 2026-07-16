from fastapi import APIRouter

from app.managers.application_manager import ApplicationManager
from app.models.application_type import ApplicationType

router = APIRouter(prefix="/templates", tags=["Templates"])

manager = ApplicationManager()


@router.get("")
def list_templates():

    return manager.list(type_filter=ApplicationType.TOOLCHAIN)