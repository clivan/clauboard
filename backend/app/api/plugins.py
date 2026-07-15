from fastapi import APIRouter

from app.managers.plugin_manager import PluginManager

router = APIRouter(tags=["Plugins"])

manager = PluginManager()


@router.get("/plugins")
def plugins():

    return manager.list()