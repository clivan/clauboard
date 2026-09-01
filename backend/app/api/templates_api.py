from fastapi import APIRouter

from app.managers.application_manager import ApplicationManager
from app.models.application_type import ApplicationType
from app.services.framework_registry import get_frameworks_for_template

router = APIRouter(prefix="/templates", tags=["Templates"])

manager = ApplicationManager()


@router.get("")
def list_templates():

    return manager.list(type_filter=ApplicationType.TOOLCHAIN)


@router.get("/{template_id}/frameworks")
def get_template_frameworks(template_id: str):
    """
    Opciones de framework/arquitectura disponibles para un template,
    si las tiene (ej. rpi-pico). Regresa {} para templates sin
    variantes — el frontend interpreta eso como "sin dropdown extra".
    """

    return get_frameworks_for_template(template_id)