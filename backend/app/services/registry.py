from pathlib import Path

import yaml

from app.models.application import Application
from app.utils.logger import logger


class Registry:

    def __init__(self):

        self.base_path = (
            Path(__file__)
            .parent.parent
            / "registry"
            / "applications"
        )

    def list_applications(self, type_filter=None):

        apps = []

        for file in sorted(self.base_path.glob("*.yaml")):

            with open(file, "r") as f:

                data = yaml.safe_load(f)

            if not data:
                # Archivo vacío o mal formado: se ignora en vez de
                # tumbar el listado completo de aplicaciones.
                logger.warning(f"[registry] omitiendo {file.name}: vacío o inválido")
                continue

            try:
                app = Application(**data)

            except Exception as error:
                logger.warning(f"[registry] omitiendo {file.name}: {error}")
                continue

            if type_filter is not None and app.type != type_filter:
                continue

            apps.append(app)

        return apps

    def get_application(self, app_id: str):

        for app in self.list_applications():

            if app.id == app_id:
                return app

        return None