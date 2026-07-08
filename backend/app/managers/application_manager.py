from app.models.application_status import ApplicationStatus

from app.services.registry import Registry
from app.services.docker_service import DockerService
from app.services.container_factory import ContainerFactory


class ApplicationManager:

    def __init__(self):

        self.registry = Registry()

        self.docker = DockerService()

    def list(self):

        apps = self.registry.list_applications()

        for app in apps:

            if not self.docker.exists(app.container_name):

                app.status = ApplicationStatus.NOT_INSTALLED

            elif self.docker.running(app.container_name):

                app.status = ApplicationStatus.RUNNING

            else:

                app.status = ApplicationStatus.STOPPED

        return apps

    def get(self, app_id):

        app = self.registry.get_application(app_id)

        if app is None:
            return None

        if not self.docker.exists(app.container_name):

            app.status = ApplicationStatus.NOT_INSTALLED

        elif self.docker.running(app.container_name):

            app.status = ApplicationStatus.RUNNING

        else:

            app.status = ApplicationStatus.STOPPED

        return app
    def install(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        if self.docker.exists(app.container_name):
            return True

        config = ContainerFactory.build(app)

        self.docker.run(config)

        return True

    def uninstall(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        self.docker.remove(app.container_name)

        return True

    def start(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        self.docker.start(app.container_name)

        return True

    def stop(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        self.docker.stop(app.container_name)

        return True

    def restart(self, app_id: str):

        app = self.registry.get_application(app_id)

        if app is None:
            return False

        self.docker.restart(app.container_name)

        return True