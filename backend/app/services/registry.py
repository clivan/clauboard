from pathlib import Path

import yaml

from app.models.application import Application


class Registry:

    def __init__(self):

        self.base_path = (
            Path(__file__)
            .parent.parent
            / "registry"
            / "applications"
        )

    def list_applications(self):

        apps = []

        for file in sorted(self.base_path.glob("*.yaml")):

            with open(file, "r") as f:

                data = yaml.safe_load(f)

            apps.append(Application(**data))

        return apps

    def get_application(self, app_id: str):

        for app in self.list_applications():

            if app.id == app_id:
                return app

        return None