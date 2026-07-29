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
from app.services.env_service import EnvService


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
        self.env = EnvService()

    def list(self) -> list[Project]:

        return self.repository.list()

    def get(self, project_id: str) -> Project | None:

        return self.repository.get(project_id)

    def create(self, request: CreateProjectRequest) -> Project:

        if self.repository.get(request.id) is not None:
            raise ValueError(
                f"Project '{request.id}' already exists."
            )

        project_path = (
            Path(request.path) if request.path
            else PROJECTS_DIR / request.id
        )

        try:
            project_path.resolve().relative_to(PROJECTS_DIR.resolve())
        except ValueError:
            raise ValueError(
                f"'{project_path}' está fuera de {PROJECTS_DIR}: el "
                "backend solo puede escribir dentro de la carpeta de "
                "proyectos montada (variable CLAUBOARD_PROJECTS_DIR "
                "en tu .env del compose principal)."
            )

        project = Project(
            id=request.id,
            name=request.name,
            description=request.description,
            template=request.template,
            path=str(project_path),
        )

        # Crear estructura del workspace
        self.workspace.initialize(project_path, request.template)

        # Copiar template si existe
        if self.templates.exists(request.template):
            self.templates.apply(request.template, str(project_path))

        # Generar .env compose-compatible (CLAVE=VALOR) con los
        # valores que el compose.yml del template espera.
        self.env.save(project_path, project.id, request.template, request.device)

        # Inicializar Git
        self.git.init(str(project_path))

        # Guardar manifest (.clauboard/project.yaml)
        self.manifest.save(project)

        # Persistir project.json vía repository
        self.repository.save(project)

        return project

    def delete(self, project_id: str):

        self.repository.delete(project_id)

    def clone(self, source_id: str, new_id: str, new_name: str, new_path: str | None = None) -> Project:

        source = self._get_or_raise(source_id)

        if self.repository.get(new_id) is not None:
            raise ValueError(f"Ya existe un proyecto con id '{new_id}'")

        dest_path = (
            Path(new_path) if new_path
            else PROJECTS_DIR / new_id
        )

        try:
            dest_path.resolve().relative_to(PROJECTS_DIR.resolve())
        except ValueError:
            raise ValueError(
                f"'{dest_path}' está fuera de {PROJECTS_DIR}"
            )

        import shutil
        shutil.copytree(Path(source.path), dest_path)

        # Actualizar project.json con los nuevos datos
        cloned = Project(
            id=new_id,
            name=new_name,
            description=source.description,
            template=source.template,
            path=str(dest_path),
            version=source.version,
            tags=list(source.tags),
        )

        self.repository.save(cloned)

        # Reinicializar git en el clon (no copiar el historial del original)
        self.git.init(str(dest_path))

        return cloned

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

    def run_stack(self, project_id: str) -> str:
        """
        Genera el comando `docker compose run --rm` para ejecutar el
        toolchain del proyecto en una terminal local. No abre un TTY
        desde la API — retorna el comando para que el usuario lo copie
        y pegue en su propia terminal.
        """

        project = self._get_or_raise(project_id)

        compose_file = self._compose_file(project)

        return self.compose.run(
            compose_file,
            project.id,
            project.template,
        )

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