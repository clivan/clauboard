from fastapi import APIRouter

from app.managers.application_manager import ApplicationManager
from app.models.application_type import ApplicationType

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure"])

manager = ApplicationManager()


@router.get("")
def list_infrastructure():

    return manager.list(type_filter=ApplicationType.INFRASTRUCTURE)