from app.models.application_status import ApplicationStatus
from app.models.application_type import ApplicationType

from app.services.registry import Registry
from app.services.docker_service import DockerService
from app.services.container_factory import ContainerFactory


class ApplicationManager:

    def __init__(self):

        self.registry = Registry()

        self.docker = DockerService()

    def _with_status(self, app):

        if not self.docker.exists(app.container_name):

            app.status = ApplicationStatus.NOT_INSTALLED

        elif self.docker.running(app.container_name):

            app.status = ApplicationStatus.RUNNING

        else:

            app.status = ApplicationStatus.STOPPED

        return app

    def list(self, type_filter=None):

        apps = self.registry.list_applications(type_filter=type_filter)

        return [self._with_status(app) for app in apps]

    def get(self, app_id):

        app = self.registry.get_application(app_id)

        if app is None:
            return None

        return self._with_status(app)

    def install(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        if app.type != ApplicationType.SERVICE:
            raise ValueError(
                f"'{app_id}' es type={app.type.value}: no se instala "
                "desde este flujo. Los toolchains se usan vía "
                "'docker compose run --rm' en tu proyecto; la "
                "infraestructura compartida se levanta con "
                "'docker compose up' en infra/."
            )

        if self.docker.exists(app.container_name):
            return True

        config = ContainerFactory.build(app)

        self.docker.run(config)

        return True

    def uninstall(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        if app.type != ApplicationType.SERVICE:
            raise ValueError(
                f"'{app_id}' es type={app.type.value}: no se "
                "desinstala desde este flujo (ver install())."
            )

        self.docker.remove(app.container_name)

        return True

    def start(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        if app.type == ApplicationType.TOOLCHAIN:
            raise ValueError(
                f"'{app_id}' es type=toolchain: no corre persistente, "
                "se usa vía 'docker compose run --rm'."
            )

        self.docker.start(app.container_name)

        return True

    def stop(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        if app.type == ApplicationType.TOOLCHAIN:
            raise ValueError(f"'{app_id}' es type=toolchain: no aplica.")

        self.docker.stop(app.container_name)

        return True

    def restart(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        if app.type == ApplicationType.TOOLCHAIN:
            raise ValueError(f"'{app_id}' es type=toolchain: no aplica.")

        self.docker.restart(app.container_name)

        return True