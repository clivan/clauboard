import docker


class DockerService:

    def __init__(self):

        self.client = docker.from_env()

    def containers(self):

        return self.client.containers.list(all=True)

    def get(self, name):

        try:
            return self.client.containers.get(name)

        except docker.errors.NotFound:
            return None

    def exists(self, name):

        return self.get(name) is not None

    def running(self, name):

        container = self.get(name)

        if container is None:
            return False

        return container.status == "running"

    def start(self, name):

        container = self.get(name)

        if container:
            container.start()

    def stop(self, name):

        container = self.get(name)

        if container:
            container.stop()

    def restart(self, name):

        container = self.get(name)

        if container:
            container.restart()

    def remove(self, name):

        container = self.get(name)

        if container:
            container.remove(force=True)

    def run(self, config):

        return self.client.containers.run(**config)
    
    def run(self, config):

        try:

            return self.client.containers.run(**config)

        except docker.errors.APIError as e:

            raise RuntimeError(str(e))