from pathlib import Path

from app.models.project import Project

from app.services.workspace_service import WorkspaceService
from app.services.template_service import TemplateService
from app.services.manifest_service import ManifestService
from app.services.git_service import GitService


class ProjectManager:

    def __init__(self):

        self.workspace = WorkspaceService()
        self.templates = TemplateService()
        self.git = GitService()
        self.manifest = ManifestService()

    def create(self, project: Project):

        if self.workspace.exists(project.path):
            raise FileExistsError(
                f"{project.path} already exists."
            )

        # Crear carpeta
        self.workspace.create(project.path)

        # Copiar template
        self.templates.apply(
            project.template,
            project.path
        )

        # Inicializar Git
        self.git.init(project.path)

        # Guardar manifest
        self.manifest.save(project)

        return project

    def list(self):
        """
        Placeholder.
        En el siguiente sprint leerá todos los project.yaml.
        """
        return []

    def delete(self, project: Project):
        """
        Placeholder.
        """
        pass