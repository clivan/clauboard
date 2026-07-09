import json

from pathlib import Path

from app.models.project import Project
from app.config import PROJECTS_DIR


class ProjectRepository:

    def __init__(self):

        PROJECTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    def list(self) -> list[Project]:

        projects = []

        for directory in PROJECTS_DIR.iterdir():

            if not directory.is_dir():
                continue

            project_file = directory / "project.json"

            if not project_file.exists():
                continue

            with open(project_file, "r") as file:

                data = json.load(file)

            projects.append(Project(**data))

        return projects

    def get(self, project_id: str) -> Project | None:

        project_file = (
            PROJECTS_DIR /
            project_id /
            "project.json"
        )

        if not project_file.exists():
            return None

        with open(project_file, "r") as file:

            data = json.load(file)

        return Project(**data)

    def save(self, project: Project):

        directory = PROJECTS_DIR / project.id

        directory.mkdir(
            parents=True,
            exist_ok=True
        )

        project_file = directory / "project.json"

        with open(project_file, "w") as file:

            json.dump(
                project.model_dump(),
                file,
                indent=4
            )

    def delete(self, project_id: str):

        directory = PROJECTS_DIR / project_id

        if not directory.exists():
            return

        for file in directory.iterdir():
            file.unlink()

        directory.rmdir()