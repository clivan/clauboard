from pathlib import Path

from app.services.workspace_service import WorkspaceService
from app.config import PROJECTS_DIR
from app.models.project import Project
from app.schemas.project import CreateProjectRequest
from backend.app.models.projects import Project
from app.repositories.project_repository import ProjectRepository


class ProjectManager:

    def __init__(self):
        self.repository = ProjectRepository()
        self.workspace = WorkspaceService()

    def list(self) -> list[Project]:

        return self.repository.list()

    def get(self, project_id: str) -> Project | None:

        return self.repository.get(project_id)

    def create(self, request: CreateProjectRequest) -> Project:
        if self._exists(request.id):
            raise ValueError(
                f"Project '{request.id}' already exists."
            )
        project = Project(
            id=request.id,
            name=request.name,
            description=request.description,
            template=request.template,
            path=str(PROJECTS_DIR / request.id)
        )
        self.repository.save(project)

        self.workspace.initialize(Path(project.path))
        return project

    def delete(self, project_id: str):

        self.repository.delete(project_id)