from pathlib import Path
import yaml

from app.models.project import Project


class ManifestService:

    MANIFEST_DIR = ".clauboard"
    MANIFEST_FILE = "project.yaml"

    def save(self, project: Project):

        manifest = Path(project.path) / self.MANIFEST_DIR

        manifest.mkdir(
            exist_ok=True
        )

        file = manifest / self.MANIFEST_FILE

        with open(file, "w") as f:

            yaml.safe_dump(
                project.model_dump(),
                f,
                sort_keys=False
            )

    def load(self, project_path: str):

        file = (
            Path(project_path)
            / self.MANIFEST_DIR
            / self.MANIFEST_FILE
        )

        if not file.exists():
            return None

        with open(file) as f:

            data = yaml.safe_load(f)

        return Project(**data)

    def exists(self, project_path: str):

        file = (
            Path(project_path)
            / self.MANIFEST_DIR
            / self.MANIFEST_FILE
        )

        return file.exists()