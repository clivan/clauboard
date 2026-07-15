from app.models.plugin import Plugin
from app.repositories.plugin_repository import PluginRepository


class PluginManager:

    def __init__(self):
        self.repository = PluginRepository()

    def list(self) -> list[Plugin]:

        return self.repository.list()