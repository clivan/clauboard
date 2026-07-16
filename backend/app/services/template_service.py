from pathlib import Path
import shutil

from app.config import TEMPLATES_DIR


class TemplateService:

    def __init__(self, templates_path: Path = TEMPLATES_DIR):
        self.templates_path = Path(templates_path)

    def list(self):
        if not self.templates_path.exists():
            return []

        return [
            d.name
            for d in self.templates_path.iterdir()
            if d.is_dir()
        ]

    def exists(self, template: str) -> bool:
        return (self.templates_path / template).exists()

    def apply(self, template: str, destination: str):

        source = self.templates_path / template

        if not source.exists():
            raise FileNotFoundError(
                f"Template '{template}' not found."
            )

        destination = Path(destination)

        for item in source.iterdir():

            target = destination / item.name

            if item.is_dir():
                shutil.copytree(
                    item,
                    target,
                    dirs_exist_ok=True
                )

            else:
                shutil.copy2(item, target)