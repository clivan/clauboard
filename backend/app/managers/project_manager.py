from pathlib import Path

from app.config import PROJECTS_DIR
from app.models.project import Project
from app.schemas.project import CreateProjectRequest
from app.repositories.project_repository import ProjectRepository
from app.services.workspace_service import WorkspaceService
from app.services.template_service import TemplateService
from app.services.manifest_service import ManifestService
from app.services.git_service import GitService
from app.services.docker_compose_service import DockerComposeService


class ProjectManager:

    COMPOSE_FILENAMES = (
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    )

    def __init__(self):
        self.repository = ProjectRepository()
        self.workspace = WorkspaceService()
        self.templates = TemplateService()
        self.git = GitService()
        self.manifest = ManifestService()
        self.compose = DockerComposeService()

    def list(self) -> list[Project]:

        return self.repository.list()

    def get(self, project_id: str) -> Project | None:

        return self.repository.get(project_id)

    def create(self, request: CreateProjectRequest) -> Project:

        if self.repository.get(request.id) is not None:
            raise ValueError(
                f"Project '{request.id}' already exists."
            )

        project_path = PROJECTS_DIR / request.id

        project = Project(
            id=request.id,
            name=request.name,
            description=request.description,
            template=request.template,
            path=str(project_path),
        )

        # Crear estructura del workspace
        self.workspace.initialize(project_path)

        # Copiar template si existe
        if self.templates.exists(request.template):
            self.templates.apply(request.template, str(project_path))

        # Inicializar Git
        self.git.init(str(project_path))

        # Guardar manifest (.clauboard/project.yaml)
        self.manifest.save(project)

        # Persistir project.json vía repository
        self.repository.save(project)

        return project

    def delete(self, project_id: str):

        self.repository.delete(project_id)

    def _compose_file(self, project: Project) -> Path:

        compose_dir = Path(project.path) / "compose"

        for filename in self.COMPOSE_FILENAMES:

            candidate = compose_dir / filename

            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            f"No se encontró docker-compose.yml en {compose_dir}"
        )

    def _get_or_raise(self, project_id: str) -> Project:

        project = self.repository.get(project_id)

        if project is None:
            raise ValueError(f"Project '{project_id}' not found")

        return project

    def start_stack(self, project_id: str):

        project = self._get_or_raise(project_id)

        self.compose.up(self._compose_file(project), project.id)

    def stop_stack(self, project_id: str):

        project = self._get_or_raise(project_id)

        self.compose.down(self._compose_file(project), project.id)

    def restart_stack(self, project_id: str):

        project = self._get_or_raise(project_id)

        self.compose.restart(self._compose_file(project), project.id)

    def stack_logs(self, project_id: str, tail: int = 200) -> str:

        project = self._get_or_raise(project_id)

        return self.compose.logs(
            self._compose_file(project), project.id, tail
        )

    def stack_status(self, project_id: str) -> str:

        project = self._get_or_raise(project_id)

        return self.compose.status(self._compose_file(project), project.id)